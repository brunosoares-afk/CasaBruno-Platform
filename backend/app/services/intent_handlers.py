from datetime import datetime, timedelta, timezone

from app.services.automation_engine import automation_engine
from app.services.homeassistant_service import (
    get_homeassistant_status,
    get_states,
    get_recognized_person,
    call_service,
)

from app.services.device_registry import registry
from app.services.llm_service import llm_service
from app.services import memory_service, weather_service
from app.services.knowledge_service import search_wikipedia
from app.services.expressions import pick
from app.config.settings import settings
from app.core.mikrotik.client import mikrotik_client
from app.services.system import get_system_status
from app.services import automations_service



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
    # NÃO ENCONTRADO / AMBÍGUO
    # ======================================================

    def device_not_found(self, intent):

        return automation_engine.execute(
            intent
        )

    def multiple_devices(self, intent):

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
    # FALLBACK CONVERSA (LLM)
    # ======================================================

    def llm_fallback(self, intent):

        text = intent.get(
            "text"
        )

        # Fase 6: usa a pessoa já resolvida por canal (fred_service.py,
        # via people_service — WhatsApp resolve pelo remetente). Só cai
        # no reconhecimento facial da câmera se não tiver isso (voz/web,
        # ou uma chamada direta ao intent_router sem passar por FredCore).
        person = intent.get("person") or get_recognized_person()

        message = llm_service.ask(
            text,
            person=person,
            # CPU sem AVX (ver memória casa-bruno-cpu-no-avx) já mede ~57-60s
            # de ponta a ponta pra uma resposta curta com contexto real —
            # 60s estava sempre no limite. Ver memória casa-bruno-fred-fala-timeout.
            timeout=intent.get("llm_timeout", 100)
        )

        return {

            "success":
            True,

            "message":
            message

        }



    # ======================================================
    # CONHECIMENTO GERAL (busca externa tipo Wikipedia)
    # ======================================================

    def knowledge_search(self, intent):

        query = (intent.get("query") or "").strip()

        if not query:
            return {
                "success": False,
                "message": pick("incerteza_honesta", default="Não entendi o que você quer saber.")
            }

        # Cache local primeiro — sem ida à rede se já perguntaram isso
        # antes (ver knowledge_service.search_wikipedia pra latência).
        cached = memory_service.search_knowledge(query, limit=1)

        if cached:
            return {
                "success": True,
                "message": cached[0]["content"]
            }

        extract = search_wikipedia(query)

        if not extract:
            return {
                "success": False,
                "message": pick("incerteza_honesta", default=f"Não encontrei nada sobre {query}.")
            }

        expires_at = (
            datetime.now(timezone.utc) + timedelta(days=settings.KNOWLEDGE_CACHE_DAYS)
        ).isoformat()

        memory_service.add_knowledge(
            category="externo_busca",
            content=extract,
            label=query,
            source="api:wikipedia",
            expires_at=expires_at,
        )

        return {
            "success": True,
            "message": extract
        }



    # ======================================================
    # REDE (MikroTik, direto — sem passar pelo HA)
    # ======================================================

    def network_status(self, intent):

        try:
            resource = mikrotik_client.resource()
            leases = mikrotik_client.dhcp_leases()
            interfaces = mikrotik_client.interfaces()
        except Exception:
            return {
                "success": False,
                "message": pick("incerteza_honesta", default="Não consegui checar a rede agora.")
            }

        cpu = resource.get("cpu-load", "?")
        connected = sum(1 for lease in leases if lease.get("status") == "bound")

        wan = next((i for i in interfaces if i.get("name") == "PPPOE-ISP"), None)
        internet_online = bool(wan and wan.get("running") == "true")

        message = (
            f"CPU do roteador em {cpu}%. "
            f"{connected} dispositivos conectados. "
            f"Internet {'online' if internet_online else 'offline'}."
        )

        return {
            "success": True,
            "message": message
        }



    # ======================================================
    # CASA / CLIMA / CELULAR / SISTEMA HA
    # ======================================================

    def _entity_state(self, entity_id):
        entity = registry.by_entity_id(entity_id)
        return entity.get("state") if entity else None

    def _format_temp(self, celsius, person):
        """Formata uma temperatura em °C na unidade preferida da pessoa
        (Fase 6.3) — todo sensor/API da casa reporta em Celsius, a
        conversão pra Fahrenheit acontece só aqui, na saída pro usuário."""

        if celsius is None:
            return None

        unit = memory_service.get_preference(person, "temp_unit", "celsius") if person else "celsius"

        if unit == "fahrenheit":
            return f"{round(celsius * 9 / 5 + 32)}°F"

        return f"{round(float(celsius))}°C"

    _WEEKDAYS_PT = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
    _MONTHS_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

    def time_query(self, intent):
        # Sem isso, "que horas são" caía no llm_fallback e o modelo
        # inventava um horário — ele nunca recebe o relógio real no
        # prompt (ver app/services/llm_service.py:_build_context).
        now = datetime.now(timezone.utc).astimezone()

        if intent.get("context") == "date":
            message = f"Hoje é {self._WEEKDAYS_PT[now.weekday()]}, {now.day} de {self._MONTHS_PT[now.month - 1]}."
        else:
            message = f"Agora são {now.hour}h{now.minute:02d}."

        return {"success": True, "message": message}

    def weather_query(self, intent):
        try:
            weather = weather_service.get_current()
        except Exception:
            return {
                "success": False,
                "message": pick("incerteza_honesta", default="Não consegui checar o clima agora.")
            }

        temp_str = self._format_temp(weather["temperature"], intent.get("person"))
        message = f"Está {weather['label']}"
        message += f", {temp_str}" if temp_str else ""

        # Só menciona sensação térmica quando faz diferença real (>=2°) —
        # senão vira ruído repetindo o mesmo número duas vezes.
        feels_like = weather.get("feels_like")
        temperature = weather.get("temperature")
        if feels_like is not None and temperature is not None and abs(feels_like - temperature) >= 2:
            feels_str = self._format_temp(feels_like, intent.get("person"))
            message += f", mas a sensação é de {feels_str}"

        message += "."

        return {"success": True, "message": message}

    def house_status(self, intent):
        parts = []

        try:
            weather = weather_service.get_current()
            temp_str = self._format_temp(weather["temperature"], intent.get("person"))
            parts.append(f"tempo {weather['label']}" + (f" a {temp_str}" if temp_str else ""))
        except Exception:
            pass

        cpu = self._entity_state("sensor.home_assistant_core_cpu_percent")
        if cpu is not None:
            parts.append(f"CPU do Home Assistant em {cpu}%")

        memory = self._entity_state("sensor.home_assistant_core_memory_percent")
        if memory is not None:
            parts.append(f"memória em {memory}%")

        try:
            leases = mikrotik_client.dhcp_leases()
            connected = sum(1 for lease in leases if lease.get("status") == "bound")
            parts.append(f"{connected} dispositivos conectados na rede")
        except Exception:
            pass

        # Fase 8 — status real das automações (não é uma frase fixa, o
        # contador vem de automations_service._run_tracked, que pega
        # exceções que antes só sumiam num "Task exception never
        # retrieved" no log, sem virar erro visível pra ninguém).
        error_count = automations_service.get_automation_error_count()
        if not error_count:
            parts.append("nenhuma automação apresentou erro")
        elif error_count == 1:
            parts.append("1 automação apresentou erro")
        else:
            parts.append(f"{error_count} automações apresentaram erro")

        if not parts:
            return {"success": False, "message": "Não consegui montar um resumo da casa agora."}

        return {"success": True, "message": "Resumo da casa: " + ", ".join(parts) + "."}

    def presence_query(self, intent):
        state = self._entity_state("person.casa_inteligente")

        if state == "home":
            message = "Bruno está em casa."
        elif state == "not_home":
            message = "Bruno não está em casa no momento."
        else:
            message = "Não sei dizer onde o celular está agora."

        return {"success": True, "message": message}

    def phone_query(self, intent):
        context = intent.get("context")

        if context == "battery":
            level = self._entity_state("sensor.poco_x8_battery_level")
            if level is None:
                return {"success": False, "message": "Não consegui ler a bateria do celular agora."}
            return {"success": True, "message": f"A bateria do celular está em {level}%."}

        if context == "charging":
            state = self._entity_state("binary_sensor.poco_x8_is_charging")
            if state is None:
                return {"success": False, "message": "Não consegui checar se o celular está carregando."}
            message = "Sim, o celular está carregando." if state == "on" else "Não, o celular não está carregando."
            return {"success": True, "message": message}

        if context == "temperature":
            temp = self._entity_state("sensor.poco_x8_battery_temperature")
            if temp is None:
                return {"success": False, "message": "Não consegui ler a temperatura do celular agora."}
            temp_str = self._format_temp(float(temp), intent.get("person"))
            return {"success": True, "message": f"A temperatura do celular está em {temp_str}."}

        return {"success": False, "message": "Não entendi qual informação do celular você quer."}

    # ======================================================
    # PREFERÊNCIAS (Fase 6.3)
    # ======================================================

    def set_preference(self, intent):
        person = intent.get("person")
        key = intent.get("key")
        value = intent.get("value")

        if not person or not key or not value:
            return {"success": False, "message": "Não consegui identificar essa preferência."}

        memory_service.set_preference(person, key, value)

        if key == "voice":
            return {"success": True, "message": f"Combinado, {person}. Vou usar essa voz com você a partir de agora."}

        if key == "temp_unit":
            label = "Fahrenheit" if value == "fahrenheit" else "Celsius"
            return {"success": True, "message": f"Combinado, {person}. Vou responder temperatura em {label} pra você."}

        return {"success": True, "message": "Preferência salva."}

    # ======================================================
    # DISPOSITIVO FAVORITO (Fase 6.4)
    # ======================================================

    def _friendly_name(self, entity_id):
        entity = registry.by_entity_id(entity_id)
        if not entity:
            return entity_id
        return entity.get("attributes", {}).get("friendly_name", entity_id)

    def set_favorite_device(self, intent):
        person = intent.get("person")
        entity_id = intent.get("entity_id")

        if not person or not entity_id:
            return {"success": False, "message": "Não consegui identificar esse dispositivo favorito."}

        memory_service.set_favorite_device(person, entity_id)
        name = self._friendly_name(entity_id)

        return {
            "success": True,
            "message": f"Combinado, {person}. {name} agora é seu favorito — pode falar 'liga ela'/'desliga ela' que eu uso ele.",
        }

    def favorite_device_query(self, intent):
        person = intent.get("person")
        entity_id = memory_service.get_favorite_device(person) if person else None

        if not entity_id:
            return {"success": True, "message": "Você ainda não tem um dispositivo favorito salvo."}

        return {"success": True, "message": f"Seu favorito é: {self._friendly_name(entity_id)}."}

    # ======================================================
    # CONFIRMAÇÃO PENDENTE (Fase 8)
    # ======================================================

    def confirmed_action(self, intent):
        action = intent.get("action")
        entity_ids = intent.get("entity_ids") or []

        if not action or not entity_ids:
            return {"success": False, "message": "Não sei mais o que eu tinha perguntado, desculpa."}

        names = []
        all_ok = True

        for entity_id in entity_ids:
            domain = entity_id.split(".")[0]
            result = call_service(domain, action, entity_id)
            all_ok = all_ok and bool(result.get("success"))
            names.append(self._friendly_name(entity_id))

        verbo = "desligado" if action == "turn_off" else "ligado"
        message = f"Combinado, {', '.join(names)} {verbo}."

        return {"success": all_ok, "message": message}

    def confirmation_declined(self, intent):
        return {"success": True, "message": "Combinado, deixo como está."}

    # ======================================================
    # MEMÓRIA / HISTÓRICO (Fase 6.5)
    # ======================================================

    def memory_summary(self, intent):
        person = intent.get("person")

        if not person:
            return {
                "success": True,
                "message": "Ainda não sei quem é você nesse canal, então não tenho nada guardado ainda.",
            }

        profile = memory_service.get_profile(person)
        prefs = memory_service.get_all_preferences(person)
        favorite_id = memory_service.get_favorite_device(person)

        parts = []

        if profile.get("summary"):
            parts.append(profile["summary"])

        if favorite_id:
            parts.append(f"seu dispositivo favorito é {self._friendly_name(favorite_id)}")

        if prefs.get("voice"):
            parts.append(f"prefere a voz {prefs['voice'].replace('Neural', '')}")

        if prefs.get("temp_unit"):
            unit_label = "Fahrenheit" if prefs["temp_unit"] == "fahrenheit" else "Celsius"
            parts.append(f"prefere temperatura em {unit_label}")

        turn_count = profile.get("turn_count") or 0
        if turn_count:
            plural = "s" if turn_count != 1 else ""
            parts.append(f"já trocamos {turn_count} mensagem{plural} em conversa livre")

        if not parts:
            return {"success": True, "message": f"Ainda não tenho nada guardado sobre você, {person}."}

        return {"success": True, "message": f"Sobre você, {person}: " + "; ".join(parts) + "."}

    def ha_system_query(self, intent):
        context = intent.get("context")
        entity_id = (
            "sensor.home_assistant_core_memory_percent" if context == "memory"
            else "sensor.home_assistant_core_cpu_percent"
        )
        value = self._entity_state(entity_id)

        if value is None:
            return {"success": False, "message": "Não consegui ler isso do Home Assistant agora."}

        label = "memória" if context == "memory" else "CPU"
        return {"success": True, "message": f"A {label} do Home Assistant está em {value}%."}

    def server_system_query(self, intent):
        context = intent.get("context")

        try:
            status = get_system_status()
        except Exception:
            return {"success": False, "message": "Não consegui ler os recursos do servidor agora."}

        if context == "memory":
            return {"success": True, "message": f"A memória do servidor está em {status['memory_percent']}%."}

        return {"success": True, "message": f"A CPU do servidor está em {status['cpu_percent']}%."}

    def backend_status(self, intent):
        ha_status = get_homeassistant_status()

        message = "Sim, o backend do Casa Bruno está online"
        if ha_status.get("online"):
            message += " e o Home Assistant também está respondendo."
        else:
            message += ", mas o Home Assistant não está respondendo agora."

        return {"success": True, "message": message}

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
