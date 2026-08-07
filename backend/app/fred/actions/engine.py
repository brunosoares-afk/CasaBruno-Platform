class ActionEngine:

    def __init__(self):
        self.actions={}

    def register(self,name,callback):
        self.actions[name]=callback

    def execute(self,name):

        if name in self.actions:
            return self.actions[name]()

        return "Action not found"

engine=ActionEngine()
