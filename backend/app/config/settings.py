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
    # OLLAMA
    # =====================================================

    OLLAMA_URL = os.getenv(
        "OLLAMA_URL",
        "http://127.0.0.1:11434"
    )

    OLLAMA_MODEL = os.getenv(
        "OLLAMA_MODEL",
        "llama3.2:1b"
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


settings = Settings()
