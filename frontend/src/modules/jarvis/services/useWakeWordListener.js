import { useEffect, useRef, useState } from "react";

const DEFAULT_WAKE_WORDS = ["jarvis", "fred"];
const NO_SPEECH_TIMEOUT_MS = 5000;
// Abaixo disso a Web Speech API já está sinalizando que não tem certeza da
// transcrição — sem essa checagem, qualquer "achismo" de baixa confiança
// (ruído, sotaque, fala cortada) era mandado pro Fred como se fosse certo,
// e ele processava/executava o texto errado sem avisar ninguém. confidence
// vem 0 em alguns navegadores/engines que não implementam isso de verdade
// (não é "confiança zero", é "não informado") — só rejeita quando o valor é
// realmente maior que 0 e ainda assim baixo.
const MIN_CONFIDENCE = 0.5;

// Erros esperados/transitórios do ciclo normal (silêncio, ou o abort que a
// gente mesmo dispara pelo timeout) — não valem a pena mostrar como falha
// pro usuário, só os outros (not-allowed, audio-capture, network, etc.).
const BENIGN_ERRORS = new Set(["no-speech", "aborted"]);

function getSpeechRecognition() {
    return window.SpeechRecognition || window.webkitSpeechRecognition || null;
}

// Escuta contínua no navegador (Web Speech API) esperando uma palavra de
// ativação. Ao detectar, abre uma segunda escuta curta (não-contínua) só
// pra capturar o comando em si, e depois volta pra escuta contínua.
// Se o navegador não suporta a API, reporta supported=false pro chamador
// cair no fallback de chat digitado.
export function useWakeWordListener({
    wakeWords = DEFAULT_WAKE_WORDS,
    onWake,
    enabled,
}) {
    const [supported, setSupported] = useState(true);
    const [status, setStatus] = useState("idle"); // idle | listening | capturing
    const [error, setError] = useState(null);

    const continuousRef = useRef(null);
    const capturingRef = useRef(false);
    const enabledRef = useRef(enabled);
    const listenNowRef = useRef(null);
    const captureTimeoutRef = useRef(null);
    // Marcado pelo chamador (JarvisContext) logo depois que o Fred termina
    // de falar — na próxima vez que o efeito abaixo (re)ligar a escuta,
    // pula direto pra captura de comando em vez de esperar "jarvis"/"fred"
    // de novo, permitindo continuar a conversa sem repetir a palavra de
    // ativação. Consumido uma única vez (reseta sozinho).
    const primeCaptureRef = useRef(false);
    // true entre "pedimos pra parar o reconhecedor contínuo" e "o onend dele
    // realmente disparou" — evita chamar .start() num reconhecedor novo antes
    // do navegador confirmar que o anterior encerrou de vez (fazer isso
    // síncrono, sem esperar o onend, podia lançar InvalidStateError e travar
    // a captura num estado morto, sem nunca completar nem dar timeout).
    const pendingCaptureRef = useRef(false);

    useEffect(() => {
        enabledRef.current = enabled;
    }, [enabled]);

    useEffect(() => {
        const SpeechRecognition = getSpeechRecognition();

        if (!SpeechRecognition) {
            setSupported(false);
            return;
        }

        if (!enabled) {
            setStatus("idle");
            listenNowRef.current = null;
            pendingCaptureRef.current = false;
            return;
        }

        let stopped = false;

        // Qualquer chamada da Web Speech API (start/stop/abort) pode
        // lançar de forma síncrona (ex: InvalidStateError se o navegador
        // ainda não liberou o reconhecedor anterior, ou NotAllowedError
        // em contexto inseguro/sem permissão de mic) — sem isso, uma
        // exceção aqui travava o reconhecedor no estado "capturing"/
        // "listening" pra sempre, sem nunca voltar a responder a clique
        // nem a fala.
        function safeCall(fn, resetOnFail) {
            try {
                fn();
                return true;
            } catch (err) {
                setError(err?.message || String(err));
                if (resetOnFail) resetOnFail();
                return false;
            }
        }

        function startCapture() {
            capturingRef.current = true;
            setStatus("capturing");

            const capture = new SpeechRecognition();
            capture.lang = "pt-BR";
            capture.continuous = false;
            capture.interimResults = false;

            // Sem isso, se nenhuma fala for detectada o reconhecedor não-
            // contínuo podia ficar "escutando" indefinidamente (varia por
            // navegador) — trava a captura em até 5s sem fala e volta pra
            // escuta contínua normalmente.
            captureTimeoutRef.current = setTimeout(() => {
                safeCall(() => capture.abort());
            }, NO_SPEECH_TIMEOUT_MS);

            capture.onresult = (event) => {
                clearTimeout(captureTimeoutRef.current);
                const result = event.results[0][0];
                const command = result.transcript.trim();
                if (!command) return;
                if (result.confidence > 0 && result.confidence < MIN_CONFIDENCE) {
                    setError("low-confidence");
                    return;
                }
                setError(null);
                onWake(command);
            };

            capture.onend = () => {
                clearTimeout(captureTimeoutRef.current);
                capturingRef.current = false;
                if (!stopped && enabledRef.current) startContinuous();
            };

            capture.onerror = (event) => {
                clearTimeout(captureTimeoutRef.current);
                capturingRef.current = false;
                if (!BENIGN_ERRORS.has(event.error)) setError(event.error);
            };

            const ok = safeCall(() => capture.start(), () => {
                capturingRef.current = false;
            });
            if (!ok && !stopped && enabledRef.current) startContinuous();
        }

        function startContinuous() {
            const recognizer = new SpeechRecognition();
            recognizer.lang = "pt-BR";
            recognizer.continuous = true;
            recognizer.interimResults = true;

            recognizer.onresult = (event) => {
                // resultados parciais (interimResults=true) disparam onresult
                // várias vezes pra UMA fala só ("jar" -> "jarvis" -> "jarvis
                // qual" -> ...) — sem essa guarda, a palavra de ativação
                // "bate" em vários desses eventos e capturava/despachava o
                // mesmo comando duas vezes, sobrecarregando o Ollama (só
                // processa uma coisa por vez nessa CPU).
                if (capturingRef.current || pendingCaptureRef.current) return;

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    // Só considera resultado FINAL, não parcial — trechos
                    // interinos (ainda sendo corrigidos pelo reconhecedor)
                    // disparavam falso-positivo com frequência (ruído/fala
                    // de fundo "batendo" com "jarvis"/"fred" num fragmento
                    // que depois mudava), abrindo e fechando a captura em
                    // loop (efeito de "ligar e desligar" visível no chip do
                    // Fred). Custa um pouco de latência pra detectar a
                    // palavra de ativação (espera o trecho fechar), troca
                    // aceitável pela estabilidade.
                    if (!event.results[i].isFinal) continue;

                    const transcript = event.results[i][0].transcript.toLowerCase();
                    const hit = wakeWords.find((w) => transcript.includes(w));

                    if (hit) {
                        // o texto após a palavra de ativação, se vier na mesma
                        // frase, é descartado de propósito — a segunda escuta
                        // (startCapture) é a fonte confiável do comando.
                        // startCapture só roda depois do onend confirmar que
                        // este reconhecedor realmente parou (ver onend abaixo).
                        pendingCaptureRef.current = true;
                        safeCall(() => recognizer.stop());
                        return;
                    }
                }
            };

            recognizer.onend = () => {
                if (pendingCaptureRef.current) {
                    pendingCaptureRef.current = false;
                    if (!stopped) startCapture();
                    return;
                }
                // o Chrome para o modo contínuo sozinho depois de um tempo
                // sem fala — reinicia, a menos que estejamos capturando um
                // comando ou o hook tenha sido desligado.
                if (!stopped && enabledRef.current && !capturingRef.current) {
                    startContinuous();
                } else if (!capturingRef.current) {
                    setStatus("idle");
                }
            };

            recognizer.onerror = (event) => {
                // 'no-speech' e outros erros transitórios não devem matar a
                // escuta contínua — o onend cuida do restart. Erros sérios
                // (not-allowed, audio-capture, network...) ficam visíveis
                // em `error` pra dar pra diagnosticar.
                if (!BENIGN_ERRORS.has(event.error)) setError(event.error);
            };

            continuousRef.current = recognizer;
            setStatus("listening");
            safeCall(() => recognizer.start(), () => {
                setStatus("idle");
            });
        }

        // Aciona manualmente a captura de comando (botão "Falar com o
        // Fred"), pulando a espera pela palavra de ativação. Só chama
        // startCapture direto se não houver reconhecedor contínuo rodando —
        // caso contrário marca pendingCaptureRef e deixa o onend dele (acima)
        // iniciar a captura, depois que o navegador confirmar que parou.
        listenNowRef.current = () => {
            if (capturingRef.current || pendingCaptureRef.current) return;

            if (continuousRef.current) {
                pendingCaptureRef.current = true;
                const ok = safeCall(() => continuousRef.current.stop());
                if (!ok) {
                    pendingCaptureRef.current = false;
                    startCapture();
                }
            } else {
                startCapture();
            }
        };

        if (primeCaptureRef.current) {
            primeCaptureRef.current = false;
            startCapture();
        } else {
            startContinuous();
        }

        return () => {
            stopped = true;
            listenNowRef.current = null;
            pendingCaptureRef.current = false;
            clearTimeout(captureTimeoutRef.current);
            safeCall(() => continuousRef.current?.stop());
        };
    }, [enabled, onWake, wakeWords]);

    function listenNow() {
        listenNowRef.current?.();
    }

    // Chamar logo antes de reabilitar a escuta (ver comentário no
    // primeCaptureRef acima) pra continuar a conversa sem repetir a
    // palavra de ativação.
    function primeCaptureNext() {
        primeCaptureRef.current = true;
    }

    return { supported, status, listenNow, primeCaptureNext, error };
}
