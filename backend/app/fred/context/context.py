class Context:

    def __init__(self):
        self.context={}

    def set(self,key,value):
        self.context[key]=value

    def get(self,key):
        return self.context.get(key)

    def dump(self):
        return self.context

context=Context()
