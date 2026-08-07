from app.services.homeassistant_service import call_service


def cinema():

    return call_service(

        "scene",

        "turn_on",

        "scene.unitv_projetor"

    )


def abrir_portao():

    return call_service(

        "switch",

        "turn_on",

        "switch.portao_casa_switch_1"

    )


def fechar_portao():

    return call_service(

        "switch",

        "turn_off",

        "switch.portao_casa_switch_1"

    )


def ligar(entity_id):

    domain = entity_id.split(".")[0]

    return call_service(

        domain,

        "turn_on",

        entity_id

    )


def desligar(entity_id):

    domain = entity_id.split(".")[0]

    return call_service(

        domain,

        "turn_off",

        entity_id

    )
