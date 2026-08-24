import { Box, keyframes } from "@mui/material";

const spin = keyframes`
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
`;

const spinReverse = keyframes`
    from { transform: rotate(360deg); }
    to { transform: rotate(0deg); }
`;

const corePulse = keyframes`
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.12); }
`;

const glowPulse = keyframes`
    0%, 100% { opacity: .55; }
    50% { opacity: 1; }
`;

// Piscada periódica — aplicada por cima de qualquer estado "acordado"
// (tudo que não é inactive/error), só pra dar sensação de "vivo" mesmo
// parado. scaleY quase 0 no meio do ciclo = olho fechado por um instante.
const blink = keyframes`
    0%, 92%, 100% { transform: scaleY(1); }
    96% { transform: scaleY(0.08); }
`;

// thinking — olhar de um lado pro outro, tipo "pensando/procurando a
// resposta" em vez de olhar fixo parado.
const lookAround = keyframes`
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-3px); }
    75% { transform: translateX(3px); }
`;

// speaking — boca abre/fecha em ritmo, parecido com waveform de fala.
const talk = keyframes`
    0%, 100% { transform: scaleY(0.35); }
    50% { transform: scaleY(1); }
`;

const STATE_STYLE = {
    inactive: { color: "#3a4552", ring: false, spin: 0, glow: false, core: false },
    listening: { color: "#EB42AF", ring: true, spin: 7, glow: true, core: true },
    capturing: { color: "#29B6F6", ring: true, spin: 2.2, glow: true, core: true, reverse: true },
    thinking: { color: "#FFB300", ring: true, spin: 3.5, glow: true, core: true },
    speaking: { color: "#FF4FD8", ring: true, spin: 1.6, glow: true, core: true },
    error: { color: "#E53935", ring: false, spin: 0, glow: true, core: true },
};

// Expressão do rosto por estado — olhos abertos/fechados/em movimento e
// se tem boca (só fala quando "speaking"). Personagem "orbe com rosto":
// evolução do orbe abstrato de antes, não substitui o esquema de cor/anel.
const FACE_STYLE = {
    inactive: { eyeHeight: 3, blink: false, lookAround: false, mouth: false, tilt: 0 },
    listening: { eyeHeight: 26, blink: true, lookAround: false, mouth: false, tilt: 0 },
    capturing: { eyeHeight: 30, blink: true, lookAround: false, mouth: false, tilt: 0 },
    thinking: { eyeHeight: 22, blink: true, lookAround: true, mouth: false, tilt: 0 },
    speaking: { eyeHeight: 26, blink: true, lookAround: false, mouth: true, tilt: 0 },
    error: { eyeHeight: 18, blink: false, lookAround: false, mouth: false, tilt: 18 },
};

// Rosto em SVG (viewBox fixo) sobreposto ao núcleo do orbe — escala
// limpo em qualquer size, do ícone minúsculo do header até um card
// grande de destaque, sem duplicar a lógica de olhos/boca em dois lugares.
function FredFace({ state }) {
    const f = FACE_STYLE[state] || FACE_STYLE.inactive;

    const eyeCommonSx = {
        transformBox: "fill-box",
        transformOrigin: "center",
        transition: "height .25s ease, y .25s ease",
        animation: [
            f.blink ? `${blink} 4.5s ease-in-out infinite` : null,
            f.lookAround ? `${lookAround} 2.6s ease-in-out infinite` : null,
        ].filter(Boolean).join(", ") || "none",
    };

    return (
        <Box
            component="svg"
            viewBox="0 0 100 100"
            sx={{
                position: "absolute",
                inset: 0,
                width: "100%",
                height: "100%",
                pointerEvents: "none",
            }}
        >
            <Box
                component="g"
                sx={{ transform: `rotate(${f.tilt}deg)`, transformOrigin: "50% 45%", transition: "transform .3s ease" }}
            >
                <Box
                    component="rect"
                    x="30" y={45 - f.eyeHeight / 2} width="12" rx="6" height={f.eyeHeight}
                    sx={{ fill: "#fff", ...eyeCommonSx }}
                />
                <Box
                    component="rect"
                    x="58" y={45 - f.eyeHeight / 2} width="12" rx="6" height={f.eyeHeight}
                    sx={{ fill: "#fff", ...eyeCommonSx, animationDelay: f.blink ? ".08s" : "0s" }}
                />
            </Box>

            {f.mouth && (
                <Box
                    component="rect"
                    x="38" y="66" width="24" rx="6" height="10"
                    sx={{
                        fill: "#fff",
                        opacity: 0.9,
                        transformBox: "fill-box",
                        transformOrigin: "center",
                        animation: `${talk} .35s ease-in-out infinite`,
                    }}
                />
            )}
        </Box>
    );
}

// Núcleo circular animado inspirado em HUDs de assistente de voz (tipo
// J.A.R.V.I.S.): anel rotativo + brilho + pulso no centro, cor e velocidade
// mudam conforme o estado real do Fred (useJarvis().listenStatus/processing).
export default function FredOrb({ state = "inactive", size = 44 }) {

    const s = STATE_STYLE[state] || STATE_STYLE.inactive;

    return (

        <Box
            sx={{
                position: "relative",
                width: size,
                height: size,
                flexShrink: 0,
                borderRadius: "50%",
                background: `radial-gradient(circle, ${s.color}2e 0%, transparent 72%)`,
                animation: s.glow ? `${glowPulse} 2.4s ease-in-out infinite` : "none",
            }}
        >

            {s.ring && (
                <Box
                    sx={{
                        position: "absolute",
                        inset: 0,
                        borderRadius: "50%",
                        background: `conic-gradient(from 0deg, transparent 0%, ${s.color} 18%, transparent 34%, transparent 66%, ${s.color} 82%, transparent 100%)`,
                        animation: `${s.reverse ? spinReverse : spin} ${s.spin}s linear infinite`,
                        WebkitMask: "radial-gradient(farthest-side, transparent calc(100% - 3px), #000 calc(100% - 3px))",
                        mask: "radial-gradient(farthest-side, transparent calc(100% - 3px), #000 calc(100% - 3px))",
                    }}
                />
            )}

            <Box
                sx={{
                    position: "absolute",
                    inset: size * 0.24,
                    borderRadius: "50%",
                    background: `radial-gradient(circle at 35% 32%, ${s.color}, ${s.color}66 70%)`,
                    boxShadow: s.core ? `0 0 ${size * 0.35}px ${s.color}99` : "none",
                    animation: s.core ? `${corePulse} 1.8s ease-in-out infinite` : "none",
                    overflow: "hidden",
                }}
            >
                <FredFace state={state} />
            </Box>

        </Box>

    );

}
