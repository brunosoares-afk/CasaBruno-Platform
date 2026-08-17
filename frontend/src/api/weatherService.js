import axios from "axios";

// Coordenadas reais de casa (mesmas usadas pelo device_tracker na HA).
const LATITUDE = -20.6280219;
const LONGITUDE = -40.4826293;

export async function getWeather() {
    const { data } = await axios.get("https://api.open-meteo.com/v1/forecast", {
        params: {
            latitude: LATITUDE,
            longitude: LONGITUDE,
            current: "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            daily: "weather_code,temperature_2m_max,temperature_2m_min",
            timezone: "America/Sao_Paulo",
        },
        timeout: 10000,
    });
    return data;
}
