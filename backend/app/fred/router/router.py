class Router:

    def __init__(self):
        self.routes = {
            "light": "LightService",
            "weather": "WeatherService",
            "docker": "DockerService",
            "network": "NetworkService",
            "homeassistant": "HomeAssistantService"
        }

    def route(self,intent):
        return self.routes.get(intent,"FallbackService")

router = Router()
