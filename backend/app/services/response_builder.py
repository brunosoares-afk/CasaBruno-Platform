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
                f"{entity} desligado."

            }.get(

                action,

                "Comando executado."

            )


            return {

                "success":
                True,

                "message":
                text,

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


            return {

                "success":
                True,

                "message":
                f"{entity} está {result['state']}.",

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



        return entity_id

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
