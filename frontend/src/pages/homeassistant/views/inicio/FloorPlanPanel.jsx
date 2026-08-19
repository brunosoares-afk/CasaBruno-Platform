import { useEffect, useRef, useState } from "react";
import { Box, Card, Tooltip, Typography } from "@mui/material";
import { keyframes } from "@emotion/react";
import HomeIcon from "@mui/icons-material/Home";
import LightbulbIcon from "@mui/icons-material/Lightbulb";
import GarageIcon from "@mui/icons-material/Garage";
import VideocamIcon from "@mui/icons-material/Videocam";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import BedIcon from "@mui/icons-material/Bed";
import KitchenIcon from "@mui/icons-material/Kitchen";

import api from "../../../../services/api";
import { useFloorPlanMarkers } from "../../../../hooks/useFloorPlanMarkers";
import { useHaServiceCall } from "../../../../modules/jarvis/services/haApi";

// Nomes salvos em floor_plan_markers -> componente real. Checar
// node_modules/@mui/icons-material antes de adicionar um nome novo aqui
// (gotcha já conhecido neste repo: nem todo nome "óbvio" existe na versão
// instalada).
export const MARKER_ICONS = {
    Lightbulb: LightbulbIcon,
    Garage: GarageIcon,
    Videocam: VideocamIcon,
    DirectionsCar: DirectionsCarIcon,
    Bed: BedIcon,
    Kitchen: KitchenIcon,
};

const glowAnim = keyframes`
    0%, 100% { filter: drop-shadow(0 0 2px currentColor); opacity: .85; }
    50% { filter: drop-shadow(0 0 9px currentColor); opacity: 1; }
`;

// Antes o "aceso" era só o ícone brilhando — pedido do usuário (2026-08-18):
// uma lâmpada ligada de verdade clareia o ambiente ao redor dela, não só
// ela mesma. Halo bem maior que o ícone, atrás dele, decorativo (sem
// pointerEvents) pra não atrapalhar o clique. Só faz sentido pra luz —
// aplicado só em marcadores tipo "state" com ícone Lightbulb.
const roomGlowAnim = keyframes`
    0%, 100% { opacity: .55; transform: translate(-50%, -50%) scale(1); }
    50% { opacity: .85; transform: translate(-50%, -50%) scale(1.08); }
`;

const bounceAnim = keyframes`
    0%, 100% { transform: translate(-50%, -50%) scale(1); }
    50% { transform: translate(-50%, -50%) scale(1.6); }
`;

const slideAnim = keyframes`
    0% { transform: translate(-50%, -50%) translateX(0); opacity: 0; }
    20% { opacity: 1; }
    80% { opacity: 1; }
    100% { transform: translate(-50%, -50%) translateX(28px); opacity: 0; }
`;

const PULSE_ANIMATIONS = { bounce: bounceAnim, slide: slideAnim };
const PULSE_DURATION_MS = 2500;

function FloorPlanMarker({ marker, entity }) {
    const Icon = MARKER_ICONS[marker.icon] || LightbulbIcon;
    const activeStates = marker.active_states || ["on"];
    const prevStateRef = useRef(entity?.state);
    const [pulsing, setPulsing] = useState(false);
    const { mutate: callService, isPending } = useHaServiceCall();

    const isStateActive = marker.type === "state" && activeStates.includes(entity?.state);

    // Planta era só decorativa até aqui (overlay tinha pointerEvents:
    // "none") — agora cada marcador chama o serviço real, igual um
    // SwitchCard faria: "pulse" (ex: portão, relé sem estado real) sempre
    // dispara turn_on; "state" alterna on/off pelo estado atual.
    const handleClick = () => {
        if (isPending || !marker.entity_id) return;
        const domain = marker.entity_id.split(".")[0];
        const service = marker.type === "pulse" || !isStateActive ? "turn_on" : "turn_off";
        callService({ domain, service, entityId: marker.entity_id });
    };

    useEffect(() => {
        if (marker.type !== "pulse") return undefined;

        const prev = prevStateRef.current;
        const current = entity?.state;
        prevStateRef.current = current;

        if (prev !== undefined && current !== prev && activeStates.includes(current)) {
            setPulsing(true);
            const timer = setTimeout(() => setPulsing(false), PULSE_DURATION_MS);
            return () => clearTimeout(timer);
        }

        return undefined;
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [entity?.state, marker.type]);

    const isActive = marker.type === "state" ? isStateActive : pulsing;
    const isRoomLight = marker.type === "state" && marker.icon === "Lightbulb";

    // Alguns marcadores (ex: carro representando presença) não fazem
    // sentido "apagados" quando inativos — o certo é sumir da planta de
    // vez, pra mostrar visualmente que a pessoa/coisa não está em casa.
    if (marker.type === "state" && marker.hide_when_inactive && !isStateActive) {
        return null;
    }

    let animation = "none";
    if (isActive) {
        if (marker.type === "state") {
            animation = `${glowAnim} 1.8s ease-in-out infinite`;
        } else {
            const anim = PULSE_ANIMATIONS[marker.anim_style] || bounceAnim;
            animation = `${anim} ${PULSE_DURATION_MS}ms ease-in-out 1`;
        }
    }

    return (
        <>
            {isRoomLight && isActive && (
                <Box
                    sx={{
                        position: "absolute",
                        left: `${marker.x_pct}%`,
                        top: `${marker.y_pct}%`,
                        width: "36%",
                        aspectRatio: "1 / 1",
                        transform: "translate(-50%, -50%)",
                        borderRadius: "50%",
                        background: (theme) =>
                            `radial-gradient(circle, ${theme.palette.warning.light} 0%, ${theme.palette.warning.main}55 35%, transparent 72%)`,
                        mixBlendMode: "screen",
                        pointerEvents: "none",
                        animation: `${roomGlowAnim} 3.2s ease-in-out infinite`,
                    }}
                />
            )}

            <Tooltip title={marker.label || marker.entity_id}>
                <Box
                    onClick={handleClick}
                    sx={{
                        position: "absolute",
                        left: `${marker.x_pct}%`,
                        top: `${marker.y_pct}%`,
                        transform: "translate(-50%, -50%)",
                        color: isActive ? "warning.main" : "rgba(255,255,255,.4)",
                        display: "flex",
                        animation,
                        pointerEvents: "auto",
                        cursor: isPending ? "default" : "pointer",
                        opacity: isPending ? 0.6 : 1,
                        p: 1,
                        "&:hover": { color: isPending ? undefined : "warning.light" },
                    }}
                >
                    <Icon fontSize="small" />
                </Box>
            </Tooltip>
        </>
    );
}

// Imagem real enviada em Gerência → Configurações → Planta da Casa (ver
// FloorPlanSection em pages/Settings.jsx). Sem imagem ainda, mostra um
// placeholder — troca sozinho assim que alguém faz upload. Marcadores
// (posição + entidade) são editados na mesma tela de Gerência
// (FloorPlanMarkersEditor) e só lidos aqui.
export default function FloorPlanPanel({ byId = {} }) {

    const [info, setInfo] = useState(null);
    const { data: markers } = useFloorPlanMarkers();

    useEffect(() => {
        api.get("/api/uploads/floor-plan/info")
            .then((res) => setInfo(res.data))
            .catch(() => setInfo({ exists: false, url: null }));
    }, []);

    if (info?.exists) {
        // Carro desenhado na garagem da planta some quando o Bruno (POCO
        // X8) não está em casa — troca pra uma variante da imagem sem o
        // carro, gerada à parte (ver away_url em /api/uploads/floor-plan/info).
        const brunoHome = byId["person.casa_inteligente"]?.state === "home";
        const imageUrl = !brunoHome && info.away_url ? info.away_url : info.url;

        return (
            <Card
                sx={{
                    aspectRatio: "4 / 3",
                    position: "relative",
                    overflow: "hidden",
                }}
            >
                <Box
                    component="img"
                    src={`${api.defaults.baseURL}${imageUrl}`}
                    alt="Planta da casa"
                    sx={{ width: "100%", height: "100%", objectFit: "contain", display: "block" }}
                />

                <Box sx={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
                    {(markers || []).map((marker) => (
                        <FloorPlanMarker
                            key={marker.id}
                            marker={marker}
                            entity={byId[marker.entity_id]}
                        />
                    ))}
                </Box>
            </Card>
        );
    }

    return (
        <Card
            sx={{
                aspectRatio: "4 / 3",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                gap: 1,
                border: "1px dashed rgba(255,255,255,.15)",
                background: "repeating-linear-gradient(45deg, rgba(255,255,255,.02) 0 10px, rgba(255,255,255,.04) 10px 20px)",
            }}
        >
            <HomeIcon sx={{ fontSize: 40, color: "text.secondary" }} />

            <Typography sx={{ fontSize: 13, color: "text.secondary", textAlign: "center", px: 2 }}>
                Planta da casa em breve — envie em Gerência → Configurações
            </Typography>
        </Card>
    );
}
