import requests

# Mesmas coordenadas já usadas em weatherService.js (frontend).
LATITUDE = -20.6280219
LONGITUDE = -40.4826293

WEATHER_CODE_LABEL = {
    0: "céu limpo", 1: "principalmente limpo", 2: "parcialmente nublado", 3: "nublado",
    45: "com nevoeiro", 48: "com nevoeiro", 51: "com garoa fraca", 53: "com garoa",
    55: "com garoa forte", 61: "com chuva fraca", 63: "com chuva", 65: "com chuva forte",
    71: "com neve fraca", 73: "com neve", 75: "com neve forte", 80: "com pancadas de chuva",
    81: "com pancadas de chuva fortes", 82: "com pancadas de chuva violentas",
    95: "com trovoada",
}


def get_current() -> dict:
    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "current": "temperature_2m,weather_code",
            "timezone": "America/Sao_Paulo",
        },
        timeout=10,
    )
    resp.raise_for_status()
    current = resp.json().get("current", {})

    return {
        "temperature": current.get("temperature_2m"),
        "label": WEATHER_CODE_LABEL.get(current.get("weather_code"), "variável"),
    }
