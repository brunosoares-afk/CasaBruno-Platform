import api from "../../../services/api";

// Respostas de conversa livre passam pelo LLM nessa CPU sem AVX e podem
// levar 60-100s de ponta a ponta (ver memória casa-bruno-fred-latency-tuning-2026-08-11).
// O timeout padrão do axios (15s) derrubaria quase toda resposta antes de
// terminar, então sobrescreve por chamada aqui.
const ASK_TIMEOUT_MS = 150000;
const SPEAK_TIMEOUT_MS = 30000;
const GREET_TIMEOUT_MS = 30000;

export async function askFred(text) {
    const res = await api.post(
        "/ask",
        { command: text, channel: "web" },
        { timeout: ASK_TIMEOUT_MS }
    );
    return res.data;
}

// Saudação personalizada (usa o perfil/resumo da pessoa) pro reconhecimento
// facial pela câmera web — ver [[casa-bruno-profile-aware-greeting-2026-08-23]].
export async function greetPerson(name) {
    const res = await api.get(`/fred/greet/${encodeURIComponent(name)}`, { timeout: GREET_TIMEOUT_MS });
    return res.data.text;
}

export async function speakText(text, voice) {
    const res = await api.post(
        "/speak",
        { text, voice },
        { timeout: SPEAK_TIMEOUT_MS, responseType: "blob" }
    );
    return res.data;
}
