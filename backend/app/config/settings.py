from dotenv import load_dotenv
import os

load_dotenv()


class Settings:

    # =====================================================
    # CBOS
    # =====================================================

    PROJECT_NAME = os.getenv(
        "PROJECT_NAME",
        "CasaBruno Operating System"
    )

    APP_NAME = os.getenv(
        "APP_NAME",
        PROJECT_NAME
    )

    VERSION = os.getenv(
        "VERSION",
        "2.0.0"
    )

    APP_VERSION = os.getenv(
        "APP_VERSION",
        VERSION
    )

    # =====================================================
    # API
    # =====================================================

    API_HOST = os.getenv(
        "CBOS_API_HOST",
        "0.0.0.0"
    )

    API_PORT = int(
        os.getenv(
            "CBOS_API_PORT",
            "8088"
        )
    )

    # Home Assistant: host/porta/token vêm de app/config.json (ver
    # app/core/config/config.py e app/core/homeassistant/client.py),
    # não daqui. Não reintroduzir HA_URL/HA_TOKEN aqui.

    # =====================================================
    # GEMINI (papo livre/saudação/resumo do Fred — ver
    # [[casa-bruno-voice-quality-2026-08-21]] pro motivo original da
    # migração. Desde 2026-09-05 é 100% Gemini, sem fallback pro Ollama
    # local — comandos de dispositivo nunca passaram por LLM nenhum,
    # são resolvidos por regra em intent_engine.py)
    # =====================================================

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.6-flash"
    )

    # =====================================================
    # KNOWLEDGE (busca externa tipo Wikipedia)
    # =====================================================

    WIKIPEDIA_LANG = os.getenv(
        "WIKIPEDIA_LANG",
        "pt"
    )

    KNOWLEDGE_CACHE_DAYS = int(
        os.getenv(
            "KNOWLEDGE_CACHE_DAYS",
            "30"
        )
    )

    # =====================================================
    # FRED PROATIVO
    # =====================================================

    # Pra onde o Fred manda os avisos proativos (jobs do scheduler_service,
    # /fred/notify). Era o @lid do self-chat de quando o número do
    # WhatsApp era o pessoal do Bruno (ver memória casa-bruno-whatsapp-fred)
    # — desde 2026-08-15 o número é dedicado só ao Fred (ver memória
    # casa-bruno-whatsapp-reconnect-2026-08-15), então o alvo agora é o
    # JID de telefone real do Bruno, não mais um self-chat.
    FRED_NOTIFY_JID = os.getenv(
        "FRED_NOTIFY_JID",
        ""
    )

    # =====================================================
    # GERÊNCIA (login do painel administrativo)
    # =====================================================

    # Senha usada só na primeira vez (seed do hash em config.json, ver
    # app/api/auth.py::_get_or_seed_auth) — depois disso o login real
    # nunca mais lê este valor.
    GERENCIA_DEFAULT_PASSWORD = os.getenv(
        "GERENCIA_DEFAULT_PASSWORD",
        ""
    )

    # =====================================================
    # CÂMERA PTZ ICSEE (DVR-IP/Sofia)
    # =====================================================

    DVRIP_CAMERA_ICSEE_FRENTE_HOST = os.getenv(
        "DVRIP_CAMERA_ICSEE_FRENTE_HOST",
        ""
    )

    DVRIP_CAMERA_ICSEE_FRENTE_USER = os.getenv(
        "DVRIP_CAMERA_ICSEE_FRENTE_USER",
        ""
    )

    DVRIP_CAMERA_ICSEE_FRENTE_PASSWORD = os.getenv(
        "DVRIP_CAMERA_ICSEE_FRENTE_PASSWORD",
        ""
    )

    # =====================================================
    # DOCKER
    # =====================================================

    DOCKER_SOCKET = os.getenv(
        "DOCKER_SOCKET",
        "/var/run/docker.sock"
    )

    # =====================================================
    # DATABASE
    # =====================================================

    DATABASE_PATH = os.getenv(
        "CBOS_DATABASE",
        "/app/database/cbos.db"
    )

    API_KEY = os.getenv(
        "CBOS_API_KEY",
        ""
    )

    # =====================================================
    # LOGS
    # =====================================================

    LOG_LEVEL = os.getenv(
        "CBOS_LOG_LEVEL",
        "INFO"
    )

    LOG_DIRECTORY = "/app/logs"

    # =====================================================
    # CACHE
    # =====================================================

    CACHE_TTL = int(
        os.getenv(
            "CACHE_TTL",
            "30"
        )
    )

    REFRESH_SECONDS = int(
        os.getenv(
            "REFRESH_SECONDS",
            "5"
        )
    )

    # =====================================================
    # CASA (app financeiro /opt/casa) — pro Fred registrar
    # lançamentos direto de uma conversa (ver casa_finance_service.py)
    # =====================================================

    CASA_API_URL = os.getenv("CASA_API_URL", "")

    CASA_TOKEN = os.getenv("CASA_TOKEN", "")


settings = Settings()
