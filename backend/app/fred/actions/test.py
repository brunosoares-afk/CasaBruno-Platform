from engine import engine

engine.register("hello",lambda:"Olá Bruno")
engine.register("status",lambda:"CBOS Online")
engine.register("fred",lambda:"FRED Ready")

print(engine.execute("hello"))
print(engine.execute("status"))
print(engine.execute("fred"))
print(engine.execute("teste"))
