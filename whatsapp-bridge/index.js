const {
  default: makeWASocket,
  useMultiFileAuthState,
  downloadMediaMessage,
  DisconnectReason,
} = require("@whiskeysockets/baileys");
const { Boom } = require("@hapi/boom");
const express = require("express");
const QRCode = require("qrcode");
const qrcodeTerminal = require("qrcode-terminal");
const pino = require("pino");
const path = require("path");
const fs = require("fs");

const PORT = process.env.WHATSAPP_BRIDGE_PORT || 8095;
const BACKEND_WEBHOOK =
  process.env.CASABRUNO_WEBHOOK || "http://127.0.0.1:8090/whatsapp/incoming";
const QR_PATH = path.join(__dirname, "last-qr.png");

// Só responde a esses JIDs (evita o Fred responder qualquer contato que
// mande mensagem pro número pessoal vinculado). Por padrão só o "Mensagens
// para você mesmo" (self-chat). Adicione outros números em
// WHATSAPP_ALLOWED_JIDS separados por vírgula, formato 55XXXXXXXXXXX@s.whatsapp.net
let selfJid = null;
let selfLid = null;
const extraAllowed = (process.env.WHATSAPP_ALLOWED_JIDS || "")
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);

const logger = pino({ level: "info" });

let sock = null;
let connectionState = { connected: false, hasQr: false };
const sentByBridge = new Set();

// Esse número é exclusivo do Fred (não é mais o pessoal do Bruno), então
// qualquer contato 1:1 pode falar com ele — grupos continuam bloqueados
// à parte (ver "@g.us" no listener de messages.upsert).
function isAllowed(jid) {
  return true;
}

async function extractIncoming(msg) {
  const sender = msg.key.remoteJid;
  const pushName = msg.pushName || "";
  const m = msg.message;
  if (!m) return null;

  if (m.conversation) {
    return { sender, pushName, text: m.conversation };
  }
  if (m.extendedTextMessage?.text) {
    return { sender, pushName, text: m.extendedTextMessage.text };
  }
  if (m.audioMessage) {
    const buffer = await downloadMediaMessage(
      msg,
      "buffer",
      {},
      { logger, reuploadRequest: sock.updateMediaMessage }
    );
    return {
      sender,
      pushName,
      audioBase64: buffer.toString("base64"),
      mimetype: m.audioMessage.mimetype || "audio/ogg",
    };
  }
  return null;
}

async function forwardToBackend(payload) {
  try {
    const res = await fetch(BACKEND_WEBHOOK, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      logger.error({ status: res.status }, "backend webhook respondeu erro");
      return null;
    }
    return await res.json();
  } catch (err) {
    logger.error({ err: err.message }, "falha ao chamar backend webhook");
    return null;
  }
}

async function start() {
  const { state, saveCreds } = await useMultiFileAuthState(
    path.join(__dirname, "auth_state")
  );

  sock = makeWASocket({
    auth: state,
    logger,
    printQRInTerminal: false,
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", async (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      connectionState.hasQr = true;
      await QRCode.toFile(QR_PATH, qr, { width: 400 });
      console.log("\n===== ESCANEIE ESTE QR NO WHATSAPP (Aparelhos conectados) =====\n");
      qrcodeTerminal.generate(qr, { small: true });
      console.log("\n=================================================================\n");
      logger.info(`QR code também salvo em ${QR_PATH}`);
    }

    if (connection === "open") {
      connectionState = { connected: true, hasQr: false };
      selfJid = sock.user?.id?.split(":")[0] + "@s.whatsapp.net";
      // WhatsApp multi-device roteia o chat "Mensagens para você mesmo"
      // por um identificador @lid (Linked ID), não pelo JID de telefone
      // tradicional — sem isso, mensagens no self-chat nunca batem com
      // selfJid e ficam fora da allowlist.
      selfLid = sock.user?.lid ? sock.user.lid.split(":")[0] + "@lid" : null;
      logger.info({ jid: selfJid, lid: selfLid, rawUser: sock.user }, "WhatsApp conectado");
      if (fs.existsSync(QR_PATH)) fs.unlinkSync(QR_PATH);
    }

    if (connection === "close") {
      connectionState.connected = false;
      const statusCode = new Boom(lastDisconnect?.error)?.output?.statusCode;
      const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
      logger.warn({ statusCode, shouldReconnect }, "conexão fechada");
      if (shouldReconnect) {
        start();
      } else {
        logger.error("sessão deslogada — apague auth_state/ e escaneie o QR de novo");
      }
    }
  });

  sock.ev.on("messages.upsert", async ({ messages, type }) => {
    if (type !== "notify") return;

    for (const msg of messages) {
      const jid = msg.key.remoteJid;

      // Mensagens que o próprio bridge mandou (respostas do Fred) voltam
      // aqui como um evento normal — precisa ignorar SÓ essas, não todo
      // fromMe. No chat "Mensagens para você mesmo" (self-chat), TODA
      // mensagem sua também vem com fromMe:true (é você mandando pra
      // você), então filtrar por fromMe sozinho descartava tudo,
      // inclusive as mensagens de verdade que você mandava pro Fred.
      if (sentByBridge.has(msg.key.id)) {
        sentByBridge.delete(msg.key.id);
        continue;
      }

      if (jid?.endsWith("@g.us")) continue; // ignora grupos

      const isSelfChat = jid === selfJid || jid === selfLid;

      // Fora do self-chat, só reage a mensagens recebidas de terceiros
      // (não intercepta o que você manda pra outras pessoas).
      if (!isSelfChat && msg.key.fromMe) continue;

      if (!isAllowed(jid)) {
        logger.info({ from: jid }, "mensagem ignorada (fora da allowlist)");
        continue;
      }

      const parsed = await extractIncoming(msg).catch((err) => {
        logger.error({ err: err.message }, "falha ao extrair mensagem");
        return null;
      });
      if (!parsed) continue;

      const reply = await forwardToBackend(parsed);
      logger.info(
        { hasText: !!reply?.text, hasAudio: !!reply?.audioBase64 },
        "resposta do backend recebida"
      );

      if (reply?.text) {
        try {
          const sent = await sock.sendMessage(jid, { text: reply.text });
          if (sent?.key?.id) sentByBridge.add(sent.key.id);
        } catch (err) {
          logger.error({ err: err.message }, "falha ao mandar texto");
        }
      }

      if (reply?.audioBase64) {
        try {
          const sentAudio = await sock.sendMessage(jid, {
            audio: Buffer.from(reply.audioBase64, "base64"),
            mimetype: reply.mimetype || "audio/ogg; codecs=opus",
            ptt: true,
          });
          if (sentAudio?.key?.id) sentByBridge.add(sentAudio.key.id);
          logger.info("nota de voz enviada com sucesso");
        } catch (err) {
          logger.error({ err: err.message, stack: err.stack }, "falha ao mandar áudio");
        }
      }
    }
  });
}

const app = express();
app.use(express.json({ limit: "20mb" }));

app.get("/status", (req, res) => {
  res.json({ ...connectionState, selfJid });
});

app.post("/send", async (req, res) => {
  if (!connectionState.connected) {
    return res.status(503).json({ error: "WhatsApp não conectado" });
  }
  const { jid, text, audioBase64, mimetype } = req.body || {};
  if (!jid || (!text && !audioBase64)) {
    return res.status(400).json({ error: "jid e (text ou audioBase64) são obrigatórios" });
  }
  try {
    if (text) {
      const sent = await sock.sendMessage(jid, { text });
      if (sent?.key?.id) sentByBridge.add(sent.key.id);
    }
    if (audioBase64) {
      const sentAudio = await sock.sendMessage(jid, {
        audio: Buffer.from(audioBase64, "base64"),
        mimetype: mimetype || "audio/ogg; codecs=opus",
        ptt: true,
      });
      if (sentAudio?.key?.id) sentByBridge.add(sentAudio.key.id);
    }
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, "127.0.0.1", () => {
  logger.info(`whatsapp-bridge escutando em 127.0.0.1:${PORT}`);
});

start().catch((err) => {
  logger.error({ err: err.message }, "falha ao iniciar Baileys");
  process.exit(1);
});
