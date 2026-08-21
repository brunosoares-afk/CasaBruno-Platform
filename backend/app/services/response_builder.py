from app.services.expressions import pick


class ResponseBuilder:



    # ======================================================
    # ENTRADA PRINCIPAL
    # ======================================================

    def build(self, result):


        if result is None:

            return {

                "success":
                False,

                "message":
                "Não consegui processar a solicitação."

            }



        if not isinstance(
            result,
            dict
        ):

            return {

                "success":
                False,

                "message":
                str(result)

            }



        if result.get(
            "success"
        ) is False:

            # Sem "message" (ex: call_service devolvendo o dict cru de
            # uma cena que falhou), o Fred ficava sem resposta nenhuma
            # pro usuário — achado 2026-08-21 junto com o detalhe de
            # erro por passo nas cenas (scenes_service._finish). Usa
            # esse detalhe quando existe, em vez de só "não consegui".
            if "message" not in result:

                detail = None

                inner = result.get("result")
                if isinstance(inner, dict):
                    detail = inner.get("error")

                entity = (
                    self.entity_name(result.get("entity_id"))
                    if result.get("entity_id") else None
                )

                if detail and entity:
                    text = f"Não consegui: {entity} — {detail}"
                elif detail:
                    text = f"Não consegui: {detail}"
                else:
                    text = "Não consegui executar o comando."

                return {**result, "message": self.with_personality(text)}

            return result



        return self.format(
            result
        )



    # ======================================================
    # FORMATADOR
    # ======================================================

    def format(self, result):


        # ----------------------------------------------
        # COMANDO EXECUTADO
        # ----------------------------------------------

        if "service" in result:


            entity = self.entity_name(
                result.get(
                    "entity_id"
                )
            )


            action = result.get(
                "service"
            )


            text = {

                "turn_on":
                f"{entity} ligado.",

                "turn_off":
                f"{entity} desligado.",

                "volume_up":
                f"Aumentei o volume do {entity}.",

                "volume_down":
                f"Abaixei o volume do {entity}."

            }.get(

                action,

                "Comando executado."

            )


            return {

                "success":
                True,

                "message":
                self.with_personality(text),

                "data":
                result

            }



        # ----------------------------------------------
        # STATUS DISPOSITIVO
        # ----------------------------------------------

        if "state" in result:


            entity = self.entity_name(

                result.get(
                    "entity_id"
                )

            )

            unit = result.get(
                "attributes",
                {}
            ).get(
                "unit_of_measurement",
                ""
            )

            state_text = (
                f"{result['state']} {unit}".strip()
            )

            return {

                "success":
                True,

                "message":
                f"{entity} está {state_text}.",

                "data":
                result

            }



        # ----------------------------------------------
        # LISTAGEM
        # ----------------------------------------------

        if "devices" in result:


            count = result.get(
                "count",
                len(
                    result["devices"]
                )
            )


            return {

                "success":
                True,

                "message":
                f"Encontrei {count} dispositivos.",

                "data":
                result

            }



        # ----------------------------------------------
        # REGISTRY
        # ----------------------------------------------

        if "registry" in result:


            return {

                "success":
                True,

                "message":
                "Dispositivos atualizados.",

                "data":
                result

            }



        # ----------------------------------------------
        # HOME ASSISTANT
        # ----------------------------------------------

        if "online" in result:


            if result.get(
                "online"
            ):

                return {

                    "success":
                    True,

                    "message":
                    "Home Assistant está online.",

                    "data":
                    result

                }



            return {

                "success":
                False,

                "message":
                "Home Assistant offline.",

                "data":
                result

            }



        # ----------------------------------------------
        # MESSAGE EXISTENTE
        # ----------------------------------------------

        if "message" in result:


            return result



        return result



    # ======================================================
    # NOME AMIGÁVEL
    # ======================================================

    def entity_name(self, entity_id):


        if not entity_id:

            return "Dispositivo"



        try:

            from app.services.device_registry import registry


            entity = registry.by_entity_id(
                entity_id
            )


            if entity:


                return entity.get(
                    "attributes",
                    {}
                ).get(

                    "friendly_name",

                    entity_id

                )


        except Exception:

            pass


        # Cenas (script.cena_*) não existem no snapshot nativo — só HA
        # tinha o friendly_name delas, e HA não existe mais. CENA_LABELS
        # é a mesma lista estática que já alimenta a tela de Cenas.
        if entity_id.startswith("script.cena_"):
            try:
                from app.services.scenes_service import CENA_LABELS
                label = CENA_LABELS.get(entity_id.split(".", 1)[1])
                if label:
                    return f"Cena {label}"
            except Exception:
                pass


        return entity_id

    # ======================================================
    # PERSONALIDADE
    # ======================================================

    def with_personality(self, text):

        prefix = pick("concordancia")

        if not prefix:

            return text

        return f"{prefix} {text}"

    # ======================================================
    # HOUSE AI
    # ======================================================

    def build_house_response(self, context, data):

        if context == "house":

            return {
                "answer": (
                    f"A casa está funcionando normalmente. "
                    f"Temperatura de {data['weather']['temperatura']}°C, "
                    f"CPU em {data['cpu']['cpu_percent']}%, "
                    f"Memória em {data['memory']['memory_percent']}% "
                    f"e {data['online_devices']} dispositivos online."
                )
            }

        if context == "weather":

            return {
                "answer": (
                    f"O clima está {data['weather']['clima']} "
                    f"com temperatura de "
                    f"{data['weather']['temperatura']}°C."
                )
            }

        if context == "temperature":

            return {
                "answer": (
                    f"A temperatura atual é "
                    f"{data['weather']['temperatura']}°C."
                )
            }

        if context == "cpu":

            return {
                "answer": (
                    f"A CPU está utilizando "
                    f"{data['cpu']['cpu_percent']}%."
                )
            }

        if context == "memory":

            return {
                "answer": (
                    f"A memória está utilizando "
                    f"{data['memory']['memory_percent']}%."
                )
            }

        if context == "online":

            return {
                "answer": (
                    f"Existem "
                    f"{data['online_devices']} dispositivos online."
                )
            }

        if context == "offline":

            return {
                "answer": (
                    f"Existem "
                    f"{data['offline_devices']} dispositivos offline."
                )
            }

        if context == "exit":

            if data["offline_devices"] > data["online_devices"]:

                return {
                    "answer": "Sim. A casa aparenta estar estável."
                }

            return {
                "answer": "Ainda existem vários dispositivos ativos."
            }

        if context == "summary":

            return {
                "answer": (
                    f"Resumo da casa: "
                    f"{data['weather']['temperatura']}°C, "
                    f"CPU {data['cpu']['cpu_percent']}%, "
                    f"Memória {data['memory']['memory_percent']}%, "
                    f"{data['online_devices']} dispositivos online."
                )
            }

        return {
            "answer": "Não consegui compreender a pergunta."
        }


response_builder = ResponseBuilder()
