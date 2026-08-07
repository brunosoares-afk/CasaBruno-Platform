from engine import engine

engine.register("status",lambda:"System Online")
engine.register("docker",lambda:"Docker OK")
engine.register("ha",lambda:"Home Assistant OK")

print(engine.run("status"))
print(engine.run("docker"))
print(engine.run("ha"))
print(engine.run("teste"))
