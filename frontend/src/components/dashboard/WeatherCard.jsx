import { Card, Box, Typography } from "@mui/material";
import AirIcon from "@mui/icons-material/Air";
import WaterDropIcon from "@mui/icons-material/WaterDrop";
import { describeWeatherCode } from "../../utils/weatherCodes";

export default function WeatherCard({ data }) {

    const current = data?.current;
    const daily = data?.daily;

    const { label, icon: Icon } = describeWeatherCode(current?.weather_code);

    return (

        <Card sx={{ flex: "1 1 320px", p: 2.5 }}>

            <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>

                <Box sx={{ color: "primary.main", display: "flex" }}>
                    <Icon sx={{ fontSize: 44 }} />
                </Box>

                <Box sx={{ minWidth: 0, flex: 1 }}>

                    <Typography sx={{ fontSize: 10, fontWeight: 600, letterSpacing: "0.09em", textTransform: "uppercase", color: "text.secondary" }}>
                        Clima externo
                    </Typography>

                    <Box sx={{ display: "flex", alignItems: "baseline", gap: 1 }}>
                        <Typography sx={{ fontSize: 30, fontWeight: 700, lineHeight: 1.1 }}>
                            {current ? `${Math.round(current.temperature_2m)}°` : "--"}
                        </Typography>
                        <Typography sx={{ fontSize: 13, color: "text.secondary" }}>
                            {label}
                        </Typography>
                    </Box>

                    {current && (
                        <Typography sx={{ fontSize: 11, color: "text.secondary", mt: 0.3 }}>
                            Sensação {Math.round(current.apparent_temperature)}°
                            {daily && ` · Máx ${Math.round(daily.temperature_2m_max?.[0])}° Mín ${Math.round(daily.temperature_2m_min?.[0])}°`}
                        </Typography>
                    )}

                </Box>

                {current && (
                    <Box sx={{ display: "flex", flexDirection: "column", gap: 0.5, alignItems: "flex-end" }}>

                        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                            <WaterDropIcon sx={{ fontSize: 14, color: "text.secondary" }} />
                            <Typography sx={{ fontSize: 11, color: "text.secondary" }}>
                                {current.relative_humidity_2m}%
                            </Typography>
                        </Box>

                        <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                            <AirIcon sx={{ fontSize: 14, color: "text.secondary" }} />
                            <Typography sx={{ fontSize: 11, color: "text.secondary" }}>
                                {Math.round(current.wind_speed_10m)} km/h
                            </Typography>
                        </Box>

                    </Box>
                )}

            </Box>

        </Card>

    );

}
