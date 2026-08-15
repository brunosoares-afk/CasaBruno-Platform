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

const STATE_STYLE = {
    inactive: { color: "#3a4552", ring: false, spin: 0, glow: false, core: false },
    listening: { color: "#EB42AF", ring: true, spin: 7, glow: true, core: true },
    capturing: { color: "#29B6F6", ring: true, spin: 2.2, glow: true, core: true, reverse: true },
    thinking: { color: "#FFB300", ring: true, spin: 3.5, glow: true, core: true },
    speaking: { color: "#FF4FD8", ring: true, spin: 1.6, glow: true, core: true },
};

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
                }}
            />

        </Box>

    );

}
