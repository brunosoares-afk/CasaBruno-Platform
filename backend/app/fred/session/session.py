class Session:

    def __init__(self):
        self.sessions={}

    def open(self,user):
        self.sessions[user]="active"

    def close(self,user):
        self.sessions[user]="closed"

    def status(self,user):
        return self.sessions.get(user)

    def list(self):
        return self.sessions

session=Session()
