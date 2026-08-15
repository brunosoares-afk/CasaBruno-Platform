import WbSunnyIcon from "@mui/icons-material/WbSunny";
import CloudQueueIcon from "@mui/icons-material/CloudQueue";
import CloudIcon from "@mui/icons-material/Cloud";
import BlurOnIcon from "@mui/icons-material/BlurOn";
import GrainIcon from "@mui/icons-material/Grain";
import UmbrellaIcon from "@mui/icons-material/Umbrella";
import ThunderstormIcon from "@mui/icons-material/Thunderstorm";
import AcUnitIcon from "@mui/icons-material/AcUnit";

// Códigos WMO usados pela Open-Meteo.
// https://open-meteo.com/en/docs (weather_code)
const CODES = {
    0: { label: "Céu limpo", icon: WbSunnyIcon },
    1: { label: "Principalmente limpo", icon: WbSunnyIcon },
    2: { label: "Parcialmente nublado", icon: CloudQueueIcon },
    3: { label: "Nublado", icon: CloudIcon },
    45: { label: "Nevoeiro", icon: BlurOnIcon },
    48: { label: "Nevoeiro com geada", icon: BlurOnIcon },
    51: { label: "Garoa fraca", icon: GrainIcon },
    53: { label: "Garoa", icon: GrainIcon },
    55: { label: "Garoa forte", icon: GrainIcon },
    56: { label: "Garoa congelante", icon: GrainIcon },
    57: { label: "Garoa congelante forte", icon: GrainIcon },
    61: { label: "Chuva fraca", icon: UmbrellaIcon },
    63: { label: "Chuva", icon: UmbrellaIcon },
    65: { label: "Chuva forte", icon: UmbrellaIcon },
    66: { label: "Chuva congelante", icon: UmbrellaIcon },
    67: { label: "Chuva congelante forte", icon: UmbrellaIcon },
    71: { label: "Neve fraca", icon: AcUnitIcon },
    73: { label: "Neve", icon: AcUnitIcon },
    75: { label: "Neve forte", icon: AcUnitIcon },
    77: { label: "Grãos de neve", icon: AcUnitIcon },
    80: { label: "Pancadas de chuva", icon: UmbrellaIcon },
    81: { label: "Pancadas de chuva fortes", icon: UmbrellaIcon },
    82: { label: "Pancadas de chuva violentas", icon: UmbrellaIcon },
    85: { label: "Pancadas de neve", icon: AcUnitIcon },
    86: { label: "Pancadas de neve fortes", icon: AcUnitIcon },
    95: { label: "Trovoada", icon: ThunderstormIcon },
    96: { label: "Trovoada com granizo", icon: ThunderstormIcon },
    99: { label: "Trovoada com granizo forte", icon: ThunderstormIcon },
};

export function describeWeatherCode(code) {
    return CODES[code] || { label: "--", icon: CloudQueueIcon };
}
