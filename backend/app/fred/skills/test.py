from engine import engine

engine.register("homeassistant","Controle do Home Assistant")
engine.register("docker","Gerenciamento Docker")
engine.register("network","Monitoramento de Rede")

print(engine.list())
