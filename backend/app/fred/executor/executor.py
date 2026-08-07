from dispatcher.dispatcher import dispatcher

class Executor:

    def execute(self,service):

        return {
            "status":"success",
            "service":service,
            "response":dispatcher.dispatch(service)
        }

executor=Executor()
