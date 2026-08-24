import { useEffect, useRef, useState } from "react";
import { Box, Typography } from "@mui/material";
import VideocamIcon from "@mui/icons-material/Videocam";

import api from "../../services/api";
import { useJarvis } from "../../modules/jarvis/context/JarvisContext";

const CAPTURE_INTERVAL_MS = 8000;

// Pede a câmera de quem está com o painel aberto (não a câmera fixa da
// sala) e manda um frame de tempos em tempos pro mesmo reconhecedor
// facial já treinado — ajuda o Fred a saber quem está usando o painel
// mesmo longe da câmera icsee, pra atribuir voz/perfil à pessoa certa.
// Indicador de câmera sempre visível enquanto ativo (nunca captura
// escondido) e some sozinho se a permissão for negada/não tiver câmera.
export default function FredFaceRecognizer() {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const streamRef = useRef(null);
    const [active, setActive] = useState(false);
    const [recognized, setRecognized] = useState(null);
    const { speak } = useJarvis();

    // Quem já foi cumprimentado nessa sessão da página — sem isso, uma
    // oscilação normal do reconhecimento (frame passa de "Bruno" pra null
    // e volta) faria o Fred repetir "Olá Bruno" a cada 8s enquanto a
    // pessoa fica parada ali. Reseta sozinho só recarregando a página.
    const greetedRef = useRef(new Set());

    useEffect(() => {
        let cancelled = false;
        let intervalId = null;

        async function start() {
            if (!navigator.mediaDevices?.getUserMedia) return;

            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: "user", width: 320, height: 240 },
                    audio: false,
                });
                if (cancelled) {
                    stream.getTracks().forEach((t) => t.stop());
                    return;
                }
                streamRef.current = stream;
                videoRef.current.srcObject = stream;
                await videoRef.current.play();
                setActive(true);

                intervalId = setInterval(capture, CAPTURE_INTERVAL_MS);
                capture();
            } catch {
                // Sem câmera/permissão negada — fica quieto, o painel
                // funciona normal sem reconhecimento web.
                setActive(false);
            }
        }

        function capture() {
            const video = videoRef.current;
            const canvas = canvasRef.current;
            if (!video || !canvas || video.readyState < 2) return;

            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext("2d").drawImage(video, 0, 0);

            canvas.toBlob(async (blob) => {
                if (!blob) return;
                const form = new FormData();
                form.append("file", blob, "frame.jpg");
                try {
                    const res = await api.post("/web-recognition", form);
                    const name = res.data.recognized;
                    if (cancelled) return;

                    setRecognized(name);

                    if (name && !greetedRef.current.has(name)) {
                        greetedRef.current.add(name);
                        speak(`Olá ${name}! Tudo bem? Em que posso ser útil?`);
                    }
                } catch {
                    // Falha pontual (backend fora, etc.) — tenta de novo
                    // no próximo ciclo, não precisa de retry aqui.
                }
            }, "image/jpeg", 0.85);
        }

        start();

        return () => {
            cancelled = true;
            if (intervalId) clearInterval(intervalId);
            streamRef.current?.getTracks().forEach((t) => t.stop());
        };
    }, []);

    return (
        <Box sx={{ display: "flex", alignItems: "center", gap: 0.75 }}>
            <video ref={videoRef} muted playsInline style={{ display: "none" }} />
            <canvas ref={canvasRef} style={{ display: "none" }} />

            {active && (
                <>
                    <VideocamIcon sx={{ fontSize: 16, color: "text.secondary" }} titleAccess="Câmera ativa pro reconhecimento" />
                    {recognized && (
                        <Typography variant="body2" color="text.secondary">
                            Oi, {recognized}
                        </Typography>
                    )}
                </>
            )}
        </Box>
    );
}
