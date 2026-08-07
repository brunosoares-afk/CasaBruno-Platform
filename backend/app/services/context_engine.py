class ContextEngine:

    def __init__(self):

        self.contexts = {

            "house": [

                "como esta a casa",
                "como está a casa",
                "status da casa",
                "estado da casa",
                "casa",
                "resumo da casa"

            ],

            "weather": [

                "clima",
                "tempo",
                "previsao",
                "previsão",
                "vai chover",
                "temperatura externa"

            ],

            "temperature": [

                "temperatura",
                "quantos graus",
                "graus",
                "frio",
                "calor"

            ],

            "cpu": [

                "cpu",
                "processador",
                "uso da cpu",
                "consumo da cpu"

            ],

            "memory": [

                "memoria",
                "memória",
                "ram",
                "uso da memoria",
                "uso da memória"

            ],
            "online": [

                "online",
                "ativos",
                "conectados",
                "quem esta online",
                "quem está online",
                "dispositivos online"

            ],

            "offline": [

                "offline",
                "desconectados",
                "quem esta offline",
                "quem está offline",
                "dispositivos offline"

            ],

            "exit": [

                "posso sair",
                "vou sair",
                "a casa esta segura",
                "a casa está segura",
                "esta tudo desligado",
                "está tudo desligado"

            ],

            "summary": [

                "resumo",
                "resumo geral",
                "status geral",
                "situacao geral",
                "situação geral"

            ]

        }
    # ======================================================
    # DETECÇÃO
    # ======================================================

    def detect(self, question):

        if not question:
            return None

        text = self.normalize(question)

        best_context = None
        best_score = 0

        for context, keywords in self.contexts.items():

            score = 0

            for keyword in keywords:

                keyword = self.normalize(keyword)

                if keyword == text:
                    score += 100

                elif keyword in text:
                    score += 20

                else:

                    words = keyword.split()

                    for word in words:

                        if word in text:
                            score += 5

            if score > best_score:

                best_score = score
                best_context = context

        return best_context
    # ======================================================
    # NORMALIZAÇÃO
    # ======================================================

    @staticmethod
    def normalize(text):

        return (
            str(text)
            .lower()
            .replace("á", "a")
            .replace("à", "a")
            .replace("â", "a")
            .replace("ã", "a")
            .replace("ä", "a")
            .replace("é", "e")
            .replace("ê", "e")
            .replace("ë", "e")
            .replace("í", "i")
            .replace("ï", "i")
            .replace("ó", "o")
            .replace("ô", "o")
            .replace("õ", "o")
            .replace("ö", "o")
            .replace("ú", "u")
            .replace("ü", "u")
            .replace("ç", "c")
            .replace("_", " ")
            .replace("-", " ")
            .replace(",", " ")
            .replace(".", " ")
            .replace("?", "")
            .replace("!", "")
            .strip()
        )
# ======================================================
# INSTÂNCIA GLOBAL
# ======================================================

context_engine = ContextEngine()
