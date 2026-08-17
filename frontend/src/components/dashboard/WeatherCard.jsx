import { useState } from "react";
import { Card, Box, Typography } from "@mui/material";
import { keyframes } from "@emotion/react";
import AirIcon from "@mui/icons-material/Air";
import WaterDropIcon from "@mui/icons-material/WaterDrop";
import WbSunnyIcon from "@mui/icons-material/WbSunny";
import CloudIcon from "@mui/icons-material/Cloud";
import CloudQueueIcon from "@mui/icons-material/CloudQueue";
import BlurOnIcon from "@mui/icons-material/BlurOn";
import UmbrellaIcon from "@mui/icons-material/Umbrella";
import AcUnitIcon from "@mui/icons-material/AcUnit";
import BoltIcon from "@mui/icons-material/Bolt";
import { describeWeatherCode } from "../../utils/weatherCodes";

const WEEKDAY = (iso) =>
    new Date(`${iso}T00:00:00`).toLocaleDateString("pt-BR", { weekday: "short" }).replace(".", "");

// Agrupa os códigos WMO em categorias visuais — cada uma vira uma cena
// animada diferente (fundo + ícones em movimento), não só um ícone parado.
function sceneGroup(code) {
    if (code == null) return "clear";
    if ([0, 1].includes(code)) return "clear";
    if ([2].includes(code)) return "partly";
    if ([3].includes(code)) return "cloudy";
    if ([45, 48].includes(code)) return "fog";
    if ([51, 53, 55, 56, 57, 61, 63, 80].includes(code)) return "rain";
    if ([65, 66, 67, 81, 82].includes(code)) return "heavy-rain";
    if ([71, 73, 75, 77, 85, 86].includes(code)) return "snow";
    if ([95, 96, 99].includes(code)) return "storm";
    return "clear";
}

const SCENE_BG = {
    clear: "linear-gradient(135deg, #2f5da8 0%, #f2a33e 100%)",
    partly: "linear-gradient(135deg, #35619c 0%, #6f95c4 100%)",
    cloudy: "linear-gradient(135deg, #4a5568 0%, #718096 100%)",
    fog: "linear-gradient(135deg, #5b6572 0%, #8c96a3 100%)",
    rain: "linear-gradient(135deg, #2c3e50 0%, #4a6580 100%)",
    "heavy-rain": "linear-gradient(135deg, #232f3a 0%, #3a5066 100%)",
    snow: "linear-gradient(135deg, #4a5a70 0%, #93a8bd 100%)",
    storm: "linear-gradient(135deg, #14181f 0%, #333c4d 100%)",
};

const spin = keyframes`from { transform: rotate(0deg); } to { transform: rotate(360deg); }`;
const pulse = keyframes`0%,100% { opacity:.85; transform:scale(1); } 50% { opacity:1; transform:scale(1.08); }`;
const drift = keyframes`0% { transform: translateX(-10%); } 100% { transform: translateX(110%); }`;
const driftSlow = keyframes`0% { transform: translateX(-15%); } 100% { transform: translateX(120%); }`;
const fall = keyframes`0% { transform: translateY(-6px); opacity:0; } 20% { opacity:1; } 100% { transform: translateY(34px); opacity:0; }`;
const sway = keyframes`0%,100% { transform: translateX(0) translateY(-6px); } 50% { transform: translateX(6px) translateY(18px); }`;
const flash = keyframes`0%, 92%, 100% { opacity:0; } 94%, 97% { opacity:1; }`;

function WeatherScene({ code }) {
    const group = sceneGroup(code);

    return (
        <Box
            sx={{
                position: "relative",
                height: 84,
                borderRadius: 2,
                overflow: "hidden",
                background: SCENE_BG[group],
            }}
        >
            {/* SOL — clear / partly */}
            {(group === "clear" || group === "partly") && (
                <Box
                    sx={{
                        position: "absolute",
                        top: group === "clear" ? 18 : 12,
                        left: group === "clear" ? "50%" : "28%",
                        transform: "translateX(-50%)",
                        animation: `${pulse} 3.5s ease-in-out infinite`,
                    }}
                >
                    <WbSunnyIcon sx={{ fontSize: group === "clear" ? 40 : 32, color: "#ffd873", animation: `${spin} 18s linear infinite`, filter: "drop-shadow(0 0 10px rgba(255,216,115,.7))" }} />
                </Box>
            )}

            {/* NUVENS — partly / cloudy / rain / heavy-rain / storm */}
            {["partly", "cloudy", "rain", "heavy-rain", "storm"].includes(group) && (
                <>
                    <Box sx={{ position: "absolute", top: group === "partly" ? 30 : 20, left: 0, animation: `${drift} 26s linear infinite` }}>
                        <CloudIcon sx={{ fontSize: 46, color: "rgba(255,255,255,.9)" }} />
                    </Box>
                    <Box sx={{ position: "absolute", top: group === "partly" ? 42 : 34, left: 0, animation: `${driftSlow} 34s linear infinite 4s` }}>
                        <CloudQueueIcon sx={{ fontSize: 32, color: "rgba(255,255,255,.55)" }} />
                    </Box>
                </>
            )}

            {/* NEVOEIRO */}
            {group === "fog" && (
                <>
                    {[14, 34, 54].map((top, i) => (
                        <Box
                            key={top}
                            sx={{
                                position: "absolute",
                                top,
                                left: 0,
                                width: "60%",
                                height: 10,
                                borderRadius: 5,
                                bgcolor: "rgba(255,255,255,.35)",
                                filter: "blur(6px)",
                                animation: `${i % 2 ? driftSlow : drift} ${20 + i * 6}s linear infinite`,
                            }}
                        />
                    ))}
                    <BlurOnIcon sx={{ position: "absolute", bottom: 8, right: 12, fontSize: 26, color: "rgba(255,255,255,.6)" }} />
                </>
            )}

            {/* CHUVA — rain / heavy-rain / storm */}
            {["rain", "heavy-rain", "storm"].includes(group) && (
                <Box sx={{ position: "absolute", bottom: 6, left: 0, right: 0, height: 40, display: "flex", justifyContent: "space-evenly" }}>
                    {Array.from({ length: group === "rain" ? 5 : 8 }).map((_, i) => (
                        <UmbrellaIconDrop key={i} delay={i * 0.18} />
                    ))}
                </Box>
            )}

            {/* NEVE */}
            {group === "snow" && (
                <>
                    <Box sx={{ position: "absolute", top: 16, left: "30%", animation: `${drift} 30s linear infinite` }}>
                        <CloudIcon sx={{ fontSize: 40, color: "rgba(255,255,255,.9)" }} />
                    </Box>
                    <Box sx={{ position: "absolute", bottom: 6, left: 0, right: 0, height: 40, display: "flex", justifyContent: "space-evenly" }}>
                        {Array.from({ length: 7 }).map((_, i) => (
                            <Box
                                key={i}
                                sx={{
                                    width: 5, height: 5, borderRadius: "50%", bgcolor: "#fff",
                                    animation: `${sway} ${1.6 + (i % 3) * 0.4}s ease-in-out infinite`,
                                    animationDelay: `${i * 0.22}s`,
                                }}
                            />
                        ))}
                    </Box>
                </>
            )}

            {/* RAIO — storm */}
            {group === "storm" && (
                <BoltIcon sx={{ position: "absolute", top: 26, right: "32%", fontSize: 30, color: "#fff59d", animation: `${flash} 3.2s ease-in-out infinite` }} />
            )}
        </Box>
    );
}

function UmbrellaIconDrop({ delay }) {
    return (
        <Box
            sx={{
                width: 2.5,
                height: 12,
                borderRadius: 2,
                bgcolor: "rgba(174,214,255,.85)",
                animation: `${fall} 1s linear infinite`,
                animationDelay: `${delay}s`,
            }}
        />
    );
}

export default function WeatherCard({ data }) {

    const [selectedDay, setSelectedDay] = useState(0);

    const current = data?.current;
    const daily = data?.daily;

    const { label } = describeWeatherCode(current?.weather_code);
    const dayCount = daily?.time?.length || 0;
    const selected = Math.min(selectedDay, Math.max(dayCount - 1, 0));

    return (

        <Card sx={{ p: 2, overflow: "hidden" }}>

            <WeatherScene code={current?.weather_code} />

            {/* HERO: temperatura + condição */}
            <Box sx={{ display: "flex", gap: 2, alignItems: "center", mt: 1.5 }}>

                <Box sx={{ minWidth: 0, flex: 1 }}>

                    <Box sx={{ display: "flex", alignItems: "baseline", gap: 1 }}>
                        <Typography sx={{ fontSize: 28, fontWeight: 700, lineHeight: 1.1 }}>
                            {current ? `${Math.round(current.temperature_2m)}°` : "--"}
                        </Typography>
                        <Typography sx={{ fontSize: 13, color: "text.secondary" }}>
                            {label}
                        </Typography>
                    </Box>

                    {current && (
                        <Typography sx={{ fontSize: 11, color: "text.secondary", mt: 0.2 }}>
                            Sensação {Math.round(current.apparent_temperature)}°
                            {daily && ` · Máx ${Math.round(daily.temperature_2m_max?.[0])}° Mín ${Math.round(daily.temperature_2m_min?.[0])}°`}
                        </Typography>
                    )}

                </Box>

                {current && (
                    <Box sx={{ display: "flex", flexDirection: "column", gap: 0.4, alignItems: "flex-end", flexShrink: 0 }}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                            <WaterDropIcon sx={{ fontSize: 13, color: "text.secondary" }} />
                            <Typography sx={{ fontSize: 11, color: "text.secondary" }}>{current.relative_humidity_2m}%</Typography>
                        </Box>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                            <AirIcon sx={{ fontSize: 13, color: "text.secondary" }} />
                            <Typography sx={{ fontSize: 11, color: "text.secondary" }}>{Math.round(current.wind_speed_10m)} km/h</Typography>
                        </Box>
                    </Box>
                )}

            </Box>

            {/* FAIXA DIÁRIA — compacta, sem painel de detalhe separado */}
            {dayCount > 0 && (
                <Box sx={{ display: "flex", gap: 0.25, overflowX: "auto", mt: 1.5, pt: 1, borderTop: "1px solid rgba(255,255,255,.08)" }}>
                    {daily.time.map((t, i) => {
                        const { icon: DIcon } = describeWeatherCode(daily.weather_code?.[i]);
                        return (
                            <Box
                                key={t}
                                onClick={() => setSelectedDay(i)}
                                sx={(theme) => ({
                                    flex: "1 1 0",
                                    minWidth: 40,
                                    display: "flex",
                                    flexDirection: "column",
                                    alignItems: "center",
                                    gap: 0.2,
                                    py: 0.5,
                                    borderRadius: 1.5,
                                    cursor: "pointer",
                                    bgcolor: i === selected ? `${theme.palette.primary.main}1f` : "transparent",
                                    "&:hover": { bgcolor: `${theme.palette.primary.main}14` },
                                })}
                            >
                                <Typography sx={{ fontSize: 9.5, fontWeight: 600, color: "text.secondary", textTransform: "capitalize" }}>
                                    {i === 0 ? "Hoje" : WEEKDAY(t)}
                                </Typography>
                                <DIcon sx={{ fontSize: 16, color: i === selected ? "primary.main" : "text.secondary" }} />
                                <Typography sx={{ fontSize: 10.5, fontWeight: 700, whiteSpace: "nowrap" }}>
                                    {Math.round(daily.temperature_2m_max?.[i])}°
                                    <Box component="span" sx={{ color: "text.secondary", fontWeight: 500 }}> {Math.round(daily.temperature_2m_min?.[i])}°</Box>
                                </Typography>
                            </Box>
                        );
                    })}
                </Box>
            )}

        </Card>

    );

}
