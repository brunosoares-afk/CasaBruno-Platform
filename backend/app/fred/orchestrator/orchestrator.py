import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from intent.engine import engine as intent
from router.router import router
from pipeline.pipeline import pipeline
from dispatcher.dispatcher import dispatcher

pipeline.steps=[]

pipeline.add("intent")
pipeline.add("router")
pipeline.add("skills")
pipeline.add("actions")

class Orchestrator:

    def execute(self,text):

        detected=intent.detect(text)

        service=router.route(detected)

        result=dispatcher.dispatch(service)

        return {
            "text":text,
            "intent":detected,
            "service":service,
            "result":result,
            "pipeline":pipeline.execute()
        }

orchestrator=Orchestrator()
