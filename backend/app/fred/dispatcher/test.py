from dispatcher import dispatcher

print(dispatcher.dispatch("LightService"))
print(dispatcher.dispatch("WeatherService"))
print(dispatcher.dispatch("DockerService"))
print(dispatcher.dispatch("NetworkService"))
print(dispatcher.dispatch("HomeAssistantService"))
print(dispatcher.dispatch("FallbackService"))
