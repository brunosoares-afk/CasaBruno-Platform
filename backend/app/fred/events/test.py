from bus import bus

bus.emit("system.boot")
bus.emit("docker.started",{"container":"homeassistant"})
bus.emit("ha.connected")

print(bus.history())
