import re


class CommandParser:


    # ======================================================
    # ENTRADA PRINCIPAL
    # ======================================================

    def parse(self, command: str):

        if not command:

            return ""


        command = self.normalize(
            command
        )


        command = self.clean(
            command
        )


        return command



    # ======================================================
    # LIMPEZA
    # ======================================================

    # Troca de palavra por índice/posição (\b) em vez de substring solta —
    # um replace ingênuo de "me" quebrava qualquer palavra que contivesse
    # essas letras no meio (ex: "home".replace("me","") virava "ho", e
    # "status home assistant" — o próprio gatilho de status do sistema —
    # nunca mais batia com nada).
    FILLER_WORDS = [
        "por favor",
        "poderia",
        "pode",
        "favor",
        "quero",
        "eu quero",
        "me",
    ]

    def clean(self, text):

        for word in self.FILLER_WORDS:

            text = re.sub(
                r"\b" + re.escape(word) + r"\b",
                "",
                text
            )


        return " ".join(
            text.split()
        )



    # ======================================================
    # NORMALIZAÇÃO
    # ======================================================

    def normalize(self, text):

        return (

            str(text)

            .lower()

            .strip()

            .replace("á", "a")
            .replace("à", "a")
            .replace("â", "a")
            .replace("ã", "a")
            .replace("ä", "a")

            .replace("é", "e")
            .replace("è", "e")
            .replace("ê", "e")
            .replace("ë", "e")

            .replace("í", "i")
            .replace("ì", "i")
            .replace("ï", "i")

            .replace("ó", "o")
            .replace("ò", "o")
            .replace("ô", "o")
            .replace("õ", "o")
            .replace("ö", "o")

            .replace("ú", "u")
            .replace("ù", "u")
            .replace("ü", "u")

            .replace("ç", "c")

        )



    # ======================================================
    # CLASSIFICADORES AUXILIARES
    # ======================================================

    def has_words(
        self,
        text,
        words
    ):


        for word in words:

            if word in text:

                return True


        return False



    def extract_action(self, command):


        if self.has_words(
            command,
            [
                "ligar",
                "acender",
                "ativar"
            ]
        ):

            return "turn_on"


        if self.has_words(
            command,
            [
                "desligar",
                "apagar",
                "desativar"
            ]
        ):

            return "turn_off"


        return None



command_parser = CommandParser()
