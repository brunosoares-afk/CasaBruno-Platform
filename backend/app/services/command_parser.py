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

    def clean(self, text):

        replacements = {

            "por favor": "",

            "poderia": "",

            "pode": "",

            "favor": "",

            "quero": "",

            "eu quero": "",

            "me": "",

        }


        for old, new in replacements.items():

            text = text.replace(
                old,
                new
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
