from pipeline import pipeline

pipeline.add("intent")
pipeline.add("router")
pipeline.add("skills")
pipeline.add("actions")

print(pipeline.execute())
