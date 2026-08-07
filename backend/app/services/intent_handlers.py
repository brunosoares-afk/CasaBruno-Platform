from app.services.automation_engine import automation_engine
from app.services.homeassistant_service import (
    get_homeassistant_status,
    get_states,
)

from app.services.device_registry import registry



class IntentHandlers:



    # ======================================================
    # DEVICE ACTION
    # ======================================================

    def device_action(self, intent):

        return automation_engine.execute(
            intent
        )



    # ======================================================
    # DEVICE STATUS
    # ======================================================

    def device_status(self, intent):

        return automation_engine.execute(
            intent
        )



    # ======================================================
    # LISTA DISPOSITIVOS
    # ======================================================

    def device_list(self, intent):

        devices = []


        for entity in registry.all():

            devices.append({

                "entity_id":
                entity.get(
                    "entity_id"
                ),


                "name":
                entity.get(
                    "attributes",
                    {}
                ).get(

                    "friendly_name",

                    entity.get(
                        "entity_id"
                    )

                ),


                "state":
                entity.get(
                    "state"
                )

            })


        return {

            "success":
            True,


            "count":
            len(devices),


            "devices":
            devices

        }



    # ======================================================
    # ATUALIZAR REGISTRY
    # ======================================================

    def registry_refresh(self, intent):


        result = registry.refresh()


        return {

            "success":
            True,


            "message":
            "Registry atualizado.",


            "registry":
            result

        }



    # ======================================================
    # HOME ASSISTANT STATUS
    # ======================================================

    def homeassistant_status(self, intent):

        return get_homeassistant_status()



    # ======================================================
    # BUSCA DE DOMÍNIO
    # ======================================================

    def domain_search(self, intent):

        domain = intent.get(
            "domain"
        )


        if not domain:

            return {

                "success":
                False,

                "message":
                "Domínio não informado."

            }



        devices = registry.by_domain(
            domain
        )


        return {

            "success":
            True,

            "domain":
            domain,

            "count":
            len(devices),

            "devices":
            devices

        }



    # ======================================================
    # FALLBACK SENSOR
    # ======================================================

    def sensor_query(self, intent):

        entity_id = intent.get(
            "entity_id"
        )


        entity = registry.by_entity_id(
            entity_id
        )


        if not entity:

            return {

                "success":
                False,

                "message":
                "Sensor não encontrado."

            }



        return {

            "success":
            True,

            "entity_id":
            entity_id,

            "state":
            entity.get(
                "state"
            ),

            "attributes":
            entity.get(
                "attributes",
                {}
            )

        }



handlers = IntentHandlers()
