class CommandEngine:

    def __init__(self):
        self.commands={}

    def register(self,name,action):
        self.commands[name]=action

    def run(self,name):

        if name in self.commands:
            return self.commands[name]()

        return "Unknown command"

engine=CommandEngine()
