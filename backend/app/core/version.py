from config.settings import settings


class Version:

    def info(self):

        return {

            "project": settings.PROJECT_NAME,

            "version": settings.VERSION,

            "api_version": settings.APP_VERSION,

            "assistant": "FRED",

            "status": "development",

            "architecture": "CBOS 2.0"

        }


version = Version()
