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

    # =====================================================
    # HOME ASSISTANT
    # =====================================================

    HOMEASSISTANT_URL = os.getenv(
        "HOMEASSISTANT_URL",
        os.getenv(
            "HA_URL",
            "http://192.168.2.80:8123"
        )
    )

    HOMEASSISTANT_TOKEN = os.getenv(
        "HOMEASSISTANT_TOKEN",
        os.getenv(
            "HA_TOKEN",
            ""
        )
    )

    # Compatibilidade

    HA_URL = HOMEASSISTANT_URL
    HA_TOKEN = HOMEASSISTANT_TOKEN

    # =====================================================
    # OLLAMA
    # =====================================================

    OLLAMA_URL = os.getenv(
        "OLLAMA_URL",
        "http://192.168.2.80:11434"
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
