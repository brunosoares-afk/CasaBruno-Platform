class Dispatcher:

    def dispatch(self,service):

        services={
            "LightService":"Executando LightService",
            "WeatherService":"Executando WeatherService",
            "DockerService":"Executando DockerService",
            "NetworkService":"Executando NetworkService",
            "HomeAssistantService":"Executando HomeAssistantService",
            "FallbackService":"Nenhum serviço encontrado"
        }

        return services.get(service,"Serviço inválido")

dispatcher=Dispatcher()
