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


def _label(code) -> str:
    return WEATHER_CODE_LABEL.get(code, "variável")


def get_current() -> dict:
    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "timezone": "America/Sao_Paulo",
        },
        timeout=10,
    )
    resp.raise_for_status()
    current = resp.json().get("current", {})

    return {
        "temperature": current.get("temperature_2m"),
        "feels_like": current.get("apparent_temperature"),
        "humidity": current.get("relative_humidity_2m"),
        "wind_speed": current.get("wind_speed_10m"),
        "label": _label(current.get("weather_code")),
    }


def get_forecast(days: int = 3) -> list[dict]:
    """Previsão diária (hoje + N-1 dias seguintes) — mesma fonte (Open-Meteo,
    sem chave/autenticação), pra quem precisar de mais que o clima agora
    (ex: core/homeassistant/weather.py, ou um futuro intent de 'previsão
    de amanhã')."""
    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "timezone": "America/Sao_Paulo",
            "forecast_days": days,
        },
        timeout=10,
    )
    resp.raise_for_status()
    daily = resp.json().get("daily", {})
    dates = daily.get("time", [])
    codes = daily.get("weather_code", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])

    return [
        {
            "date": dates[i],
            "label": _label(codes[i] if i < len(codes) else None),
            "temp_max": highs[i] if i < len(highs) else None,
            "temp_min": lows[i] if i < len(lows) else None,
        }
        for i in range(len(dates))
    ]
