def normalize(text):

    return (
        text.lower()
        .replace("á", "a")
        .replace("à", "a")
        .replace("â", "a")
        .replace("ã", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ô", "o")
        .replace("õ", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )


def interpret(command):

    cmd = normalize(command)

    aliases = {

        "acender": "ligar",
        "acende": "ligar",
        "liga": "ligar",

        "apagar": "desligar",
        "apaga": "desligar",

        "abre o portao": "abrir portao",
        "abre portao": "abrir portao",

        "como esta tudo": "como esta a casa",
        "situacao da casa": "como esta a casa",

        "tempo agora": "clima atual",
        "como esta o tempo": "clima atual",

        "onde esta bruno": "localizacao celular",

        "bruno esta em casa": "celular esta em casa"
    }

    for key, value in aliases.items():

        if key in cmd:
            return value

    return cmd
