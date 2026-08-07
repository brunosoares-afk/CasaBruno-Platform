from app.core.android.manager import android


class AndroidService:

    def devices(self):

        return android.list()

    def connect(self):

        android.connect_all()

        return {

            "status": "connected"

        }


android_service = AndroidService()
