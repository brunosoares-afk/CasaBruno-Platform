class Pipeline:

    def __init__(self):
        self.steps=[]

    def add(self,name):
        self.steps.append(name)

    def execute(self):
        return self.steps

pipeline=Pipeline()
