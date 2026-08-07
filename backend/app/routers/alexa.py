from fastapi import APIRouter, Request

from app.services.fred_service import fred
from app.services import tts_service

router = APIRouter(prefix="/alexa", tags=["Alexa"])


def _speech_response(text, end_session=True):
    audio_url = tts_service.synthesize(text)

    if audio_url:
        ssml = f'<speak><audio src="{audio_url}"/></speak>'
        output_speech = {
            "type": "SSML",
            "ssml": ssml
        }
    else:
        output_speech = {
            "type": "PlainText",
            "text": text
        }

    return {
        "version": "1.0",
        "response": {
            "outputSpeech": output_speech,
            "shouldEndSession": end_session
        }
    }


@router.post("/webhook")
async def alexa_webhook(request: Request):
    try:
        body = await request.json()
    except Exception:
        return _speech_response("Não entendi a requisição.")

    req = body.get("request", {})
    req_type = req.get("type")

    if req_type == "LaunchRequest":
        return _speech_response(
            "Fred pronto. Pode falar o que precisa.",
            end_session=False
        )

    if req_type == "IntentRequest":
        intent = req.get("intent", {})
        intent_name = intent.get("name")

        if intent_name in ("AMAZON.StopIntent", "AMAZON.CancelIntent"):
            return _speech_response("Até mais.")

        slots = intent.get("slots", {})
        consulta = slots.get("consulta", {}).get("value", "")

        if not consulta:
            return _speech_response("Não entendi o que você pediu.")

        result = fred.ask(consulta)
        message = result.get("message", "Não consegui processar.")

        return _speech_response(message, end_session=False)

    if req_type == "SessionEndedRequest":
        return {
            "version": "1.0",
            "response": {}
        }

    return _speech_response("Não entendi.")
