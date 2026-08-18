import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { useWakeWordListener } from "../services/useWakeWordListener";
import { askFred, speakText } from "../services/fredApi";
import api from "../../../services/api";

const JarvisContext = createContext(null);

// Fica montado no App.jsx, acima do Layout (que troca de página) — assim a
// escuta contínua de voz sobrevive à troca de aba do dashboard, em vez de
// morrer sempre que o usuário sai da aba Jarvis.
export function JarvisProvider({ children }) {

    const [messages, setMessages] = useState([]);
    const [processing, setProcessing] = useState(null); // null | "thinking" | "speaking"
    const [micEnabled, setMicEnabled] = useState(true);
    const [voice, setVoiceState] = useState("pm_alex");
    const [wakeWords, setWakeWordsState] = useState(["jarvis", "fred"]);

    const audioRef = useRef(null);
    // Referência pro primeCaptureNext do useWakeWordListener (definido mais
    // abaixo, depois de handleCommand) — precisa desse indireto porque
    // handleCommand é declarado antes do hook existir.
    const primeCaptureNextRef = useRef(null);

    // Carrega voz + palavra de ativação salvas (GET /fred/config, público —
    // ver app/routers/fred.py). Também editável via Gerência → Configurações,
    // que grava na mesma seção "fred" do config.json.
    useEffect(() => {
        api.get("/fred/config")
            .then((res) => {
                if (res.data?.voice) setVoiceState(res.data.voice);

                const fetched = res.data?.wakeWords;
                if (Array.isArray(fetched) && fetched.length) {
                    // Só troca a referência do array (e reinicia o reconhecedor
                    // de voz, que depende dela) se o conteúdo realmente mudou —
                    // sem isso, todo carregamento de página reiniciava a escuta
                    // contínua por causa de um array "igual" mas com identidade
                    // nova vindo do JSON, o que podia deixar o Fred travado em
                    // "inativo" se esse restart caísse num momento ruim (ex:
                    // permissão de microfone ainda sendo negociada).
                    setWakeWordsState((prev) => {
                        const same = prev.length === fetched.length && prev.every((w, i) => w === fetched[i]);
                        return same ? prev : fetched;
                    });
                }
            })
            .catch(() => {});
    }, []);

    const setVoice = useCallback((next) => {
        setVoiceState(next);
        api.post("/fred/config", { voice: next }).catch(() => {});
    }, []);

    const setWakeWords = useCallback((next) => {
        setWakeWordsState(next);
        api.post("/fred/config", { wakeWords: next }).catch(() => {});
    }, []);

    const handleCommand = useCallback(async (text) => {

        setMessages((prev) => [...prev, { role: "user", text }]);
        setProcessing("thinking");

        let reply;
        try {
            const res = await askFred(text);
            reply = res?.message || "Não consegui pensar em uma resposta.";
        } catch {
            reply = "Não consegui falar com o Fred agora.";
        }

        setMessages((prev) => [...prev, { role: "fred", text: reply }]);
        setProcessing("speaking");

        // Continua a conversa sem precisar repetir "Jarvis"/"Fred": assim
        // que o Fred termina de falar (sucesso ou falha), a próxima vez que
        // a escuta reabilitar (enabled volta a true) já entra direto
        // ouvindo um comando. Some sozinho se ninguém falar em 5s (mesmo
        // timeout já usado pra captura normal).
        function continueListening() {
            primeCaptureNextRef.current?.();
            setProcessing(null);
        }

        try {
            const blob = await speakText(reply, voice);
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);
            audioRef.current = audio;

            audio.onended = () => {
                URL.revokeObjectURL(url);
                continueListening();
            };
            audio.onerror = () => continueListening();

            await audio.play();
        } catch {
            continueListening();
        }

    }, [voice]);

    const { supported, status: listenStatus, listenNow, primeCaptureNext, error: micError } = useWakeWordListener({
        wakeWords,
        enabled: micEnabled && processing === null,
        onWake: handleCommand,
    });

    useEffect(() => {
        primeCaptureNextRef.current = primeCaptureNext;
    }, [primeCaptureNext]);

    const value = {
        messages,
        processing,
        micEnabled,
        setMicEnabled,
        voice,
        setVoice,
        wakeWords,
        setWakeWords,
        handleCommand,
        supported,
        listenStatus,
        listenNow,
        micError,
    };

    return (
        <JarvisContext.Provider value={value}>
            {children}
        </JarvisContext.Provider>
    );
}

export function useJarvis() {
    const ctx = useContext(JarvisContext);
    if (!ctx) throw new Error("useJarvis precisa estar dentro de <JarvisProvider>");
    return ctx;
}
