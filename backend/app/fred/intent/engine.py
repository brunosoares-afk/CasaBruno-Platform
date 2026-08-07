class IntentEngine:

    def detect(self,text):

        text=text.lower()

        if "luz" in text:
            return "light"

        if "clima" in text:
            return "weather"

        if "temperatura" in text:
            return "weather"

        if "docker" in text:
            return "docker"

        return "unknown"

engine=IntentEngine()
