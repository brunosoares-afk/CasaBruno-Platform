class SkillEngine:

    def __init__(self):
        self.skills={}

    def register(self,name,description):
        self.skills[name]=description

    def list(self):
        return self.skills

engine=SkillEngine()
