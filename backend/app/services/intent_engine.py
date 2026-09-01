from app.services.device_registry import registry
from app.services.fred_memory import memory
from app.services import memory_service, scenes_service


class IntentEngine:

    # Dispositivo assumido quando um pronome aparece sem nenhum contexto
    # anterior nessa execução do backend (fred_memory ainda vazio pra
    # "last_entity_id") — a própria TV, mesmo exemplo dado pelo usuário
    # ("liga ela" = a televisão).
    DEFAULT_PRONOUN_ENTITY = "media_player.bruno_s_n65b"

    PRONOUNS = ["ela", "ele", "isso", "aquilo"]

    # Vozes Azure já disponíveis no voice_service.py/VoiceSettingsPanel.jsx
    # (ver [[casa-bruno-whatsapp-fred]]) — nome falado -> nome exato da voz.
    # Nomes das vozes instaladas (Piper + Kokoro, ver voice_service.py) —
    # antes disso apontava pras vozes Azure (AntonioNeural etc.), que não
    # existem mais desde a migração e deixavam esse comando quebrado sem avisar.
    VOICE_NAMES = {
        "alex": "pm_alex",
        "santa": "pm_santa",
        "dora": "pf_dora",
        "cadu": "pt_BR-cadu-medium",
        "faber": "pt_BR-faber-medium",
        "edresson": "pt_BR-edresson-low",
        "jeff": "pt_BR-jeff-medium",
    }

    # Palavras de "lembra que a tv é minha favorita" que não fazem parte
    # do nome do dispositivo em si — sobra só o que precisa bater contra
    # o registry (ex: "tv").
    FAVORITE_STOPWORDS = {
        "favorito", "favorita", "favoritos", "favoritas",
        "minha", "meu", "meus", "minhas", "lembra", "lembre",
        "guarda", "guarde", "salva", "salve", "que", "como",
        "e", "de", "da", "do",
    }

    # Frases fixas do dia a dia — cada uma resolve direto pro mesmo par
    # (action, entity_id) que o device_action genérico já produziria se
    # a conjugação batesse com os gatilhos normais. "Fecha"/"abre" a
    # garagem caem os dois em turn_on porque o relé do portão é por
    # pulso só (sem estado aberto/fechado de verdade — mesmo motivo
    # "abrir o portão" também já é turn_on).
    NATURAL_PHRASES = [
        (["acende a cozinha", "acender a cozinha"], ("turn_on", "light.lampada_cozinha")),
        (["apaga tudo", "apagar tudo"], ("turn_off", "light.lampada_cozinha")),
        (["fecha a garagem", "fechar a garagem", "abre a garagem", "abrir a garagem", "abre o portao", "abre o portão"], ("turn_on", "switch.portao_casa_switch_1")),
        (["quero assistir filme", "vou assistir filme", "assistir filme"], ("turn_on", "script.cena_assistir_tv")),
        (["modo dormir", "boa noite"], ("turn_on", "script.cena_boa_noite")),
        (["vou sair"], ("turn_on", "script.cena_saida_de_casa")),
        # Antes caía em cena_bom_dia por engano (bug — "chegando" não tem
        # nada a ver com "bom dia"). Agora que existe uma cena própria pra
        # chegada de carro (portão + luz + anúncio), faz sentido de verdade.
        (["estou chegando", "ja estou chegando", "já estou chegando", "chegando de carro", "cheguei de carro"], ("turn_on", "script.cena_chegando_de_carro")),
        (["chegando a pe", "chegando a pé", "cheguei a pe", "cheguei a pé"], ("turn_on", "script.cena_chegando_a_pe")),
        (["bom dia"], ("turn_on", "script.cena_bom_dia")),
        (["esta calor", "está calor"], ("turn_on", "script.cena_conforto_ar")),
        (["nao perturbe", "não perturbe", "modo nao perturbe"], ("turn_on", "script.cena_nao_perturbe")),
        (["silencio total", "silêncio total"], ("turn_on", "script.cena_silencio_total")),
        (["fim de cinema", "acabou o filme", "acabou o cinema"], ("turn_on", "script.cena_fim_de_cinema")),
        (["ligar a tv philips", "liga a tv philips", "ligar tv da sala", "liga tv da sala"], ("turn_on", "script.fred_tv_philips_power")),
        (["desligar a tv philips", "desliga a tv philips", "desligar tv da sala", "desliga tv da sala"], ("turn_on", "script.fred_tv_philips_power_off")),
        (["aumentar volume da tv philips", "aumenta volume da tv philips", "aumentar volume da tv da sala"], ("turn_on", "script.fred_tv_philips_volume_up")),
        (["diminuir volume da tv philips", "diminui volume da tv philips", "diminuir volume da tv da sala"], ("turn_on", "script.fred_tv_philips_volume_down")),
        (["mudo na tv philips", "silenciar tv philips", "mudo na tv da sala"], ("turn_on", "script.fred_tv_philips_mute")),
    ]

    # ======================================================
    # ENTRADA PRINCIPAL
    # ======================================================

    def parse(self, command: str, person: str = None):

        if not command:
            return {"type": "unknown"}

        cmd = registry.normalize(command)

        # ==================================================
        # CONFIRMAÇÃO PENDENTE (Fase 8) — quando um aviso proativo
        # pergunta "quer que eu apague?", a resposta "sim"/"não" precisa
        # ser interceptada ANTES de qualquer outro bloco, senão um "sim"
        # solto não bate em nada e cai no LLM sem fazer nada de verdade.
        # Expira sozinha (recall_fresh) pra um "sim" de dias depois não
        # reviver uma pergunta que já passou.
        # ==================================================

        pending = memory.recall_fresh(person, "pending_confirmation", 600) if person else None

        if pending:
            if self.contains_any(cmd, ["sim", "pode", "claro", "manda", "confirma", "confirmado"]):
                memory.forget(person, "pending_confirmation")
                return {
                    "type": "confirmed_action",
                    "action": pending.get("action"),
                    "entity_ids": pending.get("entity_ids", []),
                }
            if self.contains_any(cmd, ["nao", "não", "deixa", "deixa assim", "nada"]):
                memory.forget(person, "pending_confirmation")
                return {"type": "confirmation_declined"}

        # ==================================================
        # NEGAÇÃO ("não liga a luz", "não precisa ligar o ventilador") —
        # contains_any() é substring puro e ignorava o "não" inteiro,
        # batia só no verbo de ação e executava o oposto do pedido. Não
        # tenta inverter a ação sozinho (ambíguo — "não desliga ainda"
        # não quer dizer "liga"), só recusa agir aqui e deixa cair pro
        # bate-papo livre (LLM), que entende negação de verdade em vez
        # de arriscar fazer o contrário do que a pessoa pediu.
        # ==================================================

        if "nao" in cmd.split() and self.contains_any(
            cmd,
            ["ligar", "desligar", "acender", "apagar", "ativar", "desativar", "abrir", "fechar",
             "liga", "desliga", "acende", "apaga"],
        ):
            return {"type": "unknown"}

        # ==================================================
        # "liga a luz" sozinho assume a cozinha (comportamento de sempre),
        # mas a frase também é substring de "liga a luz da sala"/"liga a
        # luz do quarto" — sem essa guarda, qualquer cômodo pedido acabava
        # acendendo a cozinha por engano. Se outro cômodo for mencionado,
        # deixa cair pro registry.search() genérico logo abaixo, que já
        # sabe achar (ou dizer que não achou) o dispositivo do cômodo
        # certo em vez de acender o errado.
        # ==================================================

        OUTROS_COMODOS = ["sala", "quarto", "banheiro", "varanda", "escritorio", "garagem"]

        # "desliga a luz"/"desliga a luz da cozinha" também contêm "liga a
        # luz" como substring ("de-SLIGA A LUZ") — sem essa exclusão, pedir
        # pra desligar acabava ligando por engano.
        if (
            self.contains_any(cmd, ["liga a luz", "esta escuro"])
            and not self.contains_any(cmd, OUTROS_COMODOS)
            and not self.contains_any(cmd, ["desliga", "apaga"])
        ):
            return {"type": "device_action", "action": "turn_on", "entity_id": "light.lampada_cozinha"}

        # ==================================================
        # LINGUAGEM NATURAL (frases fixas do dia a dia que usam
        # conjugação/forma que os gatilhos genéricos abaixo não cobrem —
        # ex: "acende"/"liga"/"apaga" não contêm "acender"/"ligar"/
        # "apagar" como substring, e "modo dormir" bateria no scene_action
        # genérico só que sem achar nada, já que nenhuma cena se chama
        # "dormir". Checado bem no topo, antes de qualquer catch-all.)
        # ==================================================

        for phrases, (action, entity_id) in self.NATURAL_PHRASES:
            if self.contains_any(cmd, phrases):
                return {"type": "device_action", "action": action, "entity_id": entity_id}

        # ==================================================
        # PRONOME ("liga ela", "desliga ele", "aumenta isso") — resolve
        # pro último dispositivo referenciado nessa conversa (gravado em
        # fred_memory por fred_service.py a cada intent que já resolveu
        # um entity_id de verdade), com um favorito fixo de fallback
        # (a TV) pra quando ainda não há nenhum contexto. Checado antes
        # dos gatilhos genéricos de ligar/desligar por nome — "ligar ela"
        # bateria neles primeiro e nunca acharia um dispositivo chamado
        # "ela".
        # ==================================================

        if self.contains_any(cmd, self.PRONOUNS):

            action = None
            if self.contains_any(cmd, ["desligar", "desliga", "apagar", "apaga", "desativar", "desativa", "fechar", "fecha"]):
                action = "turn_off"
            elif self.contains_any(cmd, ["ligar", "liga", "acender", "acende", "ativar", "ativa", "abrir", "abre"]):
                action = "turn_on"

            if action:
                # Prioridade (Fase 6.4): contexto recente da conversa >
                # favorito salvo da pessoa > TV padrão (só quando ninguém
                # nunca salvou nada, mesmo comportamento de antes).
                entity_id = (
                    memory.recall(person, "last_entity_id")
                    or memory_service.get_favorite_device(person)
                    or self.DEFAULT_PRONOUN_ENTITY
                )
                return {"type": "device_action", "action": action, "entity_id": entity_id}

        # ==================================================
        # CASA / CLIMA / CELULAR / SISTEMA HA (consultas fixas,
        # checadas ANTES do catch-all "sist" logo abaixo — "cpu home
        # assistant"/"memoria home assistant" contêm "sist" e cairiam
        # sempre em homeassistant_status se checadas depois)
        # ==================================================

        if self.contains_any(cmd, ["cpu home assistant", "memoria home assistant", "memória home assistant"]):
            return {
                "type": "ha_system_query",
                "context": "memory" if "memoria" in cmd or "memória" in cmd else "cpu",
            }

        # Servidor físico (o host Debian rodando o backend, via psutil em
        # app/services/system.py) — distinto do "home assistant" acima,
        # que só lê o sensor interno do HA Core.
        if self.contains_any(cmd, ["cpu servidor", "cpu do servidor", "memoria servidor", "memoria do servidor", "memória servidor", "memória do servidor"]):
            return {
                "type": "server_system_query",
                "context": "memory" if "memoria" in cmd or "memória" in cmd else "cpu",
            }

        if self.contains_any(cmd, ["que horas", "que hora", "horas sao", "hora atual", "hora agora"]):
            return {"type": "time_query", "context": "time"}

        if self.contains_any(cmd, ["que dia e hoje", "que dia e", "data de hoje", "dia da semana"]):
            return {"type": "time_query", "context": "date"}

        if self.contains_any(cmd, ["clima atual", "tempo agora", "previsao do tempo", "previsão do tempo", "clima", "previsao", "previsão"]):
            return {"type": "weather_query"}

        if self.contains_any(cmd, ["como esta a casa", "como está a casa", "como vai a casa", "resumo da casa"]):
            return {"type": "house_status"}

        if self.contains_any(
            cmd,
            [
                "onde esta o celular", "onde está o celular", "celular esta em casa", "celular está em casa",
                "localizacao", "localização",
                "onde esta bruno", "onde está bruno", "onde esta o bruno", "onde está o bruno",
                "onde esta taiane", "onde está taiane", "onde esta a taiane", "onde está a taiane",
                "onde esta heitor", "onde está heitor", "onde esta o heitor", "onde está o heitor",
                "onde estao todos", "onde estão todos", "quem esta em casa", "quem está em casa",
            ],
        ):
            target = None
            if self.contains_any(cmd, ["taiane"]):
                target = "taiane"
            elif self.contains_any(cmd, ["heitor"]):
                target = "heitor"
            elif self.contains_any(cmd, ["bruno"]):
                target = "bruno"
            elif self.contains_any(cmd, ["todos", "quem esta", "quem está"]):
                target = "todos"
            return {"type": "presence_query", "target": target}

        if self.contains_any(cmd, ["bateria celular", "celular carregando", "temperatura celular"]):
            if "carregando" in cmd:
                context = "charging"
            elif "temperatura" in cmd:
                context = "temperature"
            else:
                context = "battery"
            return {"type": "phone_query", "context": context}

        if self.contains_any(cmd, ["casa bruno online", "casabruno online"]):
            return {"type": "backend_status"}

        # ==================================================
        # PREFERÊNCIAS (Fase 6.3) — checado antes de qualquer bloco que
        # use essas mesmas palavras por outro motivo (nenhum outro bloco
        # usa "voz"/"fahrenheit"/"celsius" hoje, mas melhor deixar cedo
        # já que é uma categoria própria de intent, não uma ação de casa).
        # ==================================================

        if "voz" in cmd:
            for name, azure_voice in self.VOICE_NAMES.items():
                if name in cmd:
                    return {"type": "set_preference", "key": "voice", "value": azure_voice}

        if "fahrenheit" in cmd:
            return {"type": "set_preference", "key": "temp_unit", "value": "fahrenheit"}

        if "celsius" in cmd:
            return {"type": "set_preference", "key": "temp_unit", "value": "celsius"}

        # ==================================================
        # DISPOSITIVO FAVORITO (Fase 6.4) — "favorit" cobre
        # favorito/favorita/favoritos/favoritas depois do normalize.
        # ==================================================

        if "favorit" in cmd:

            if self.contains_any(cmd, ["qual", "quem", "quais"]):
                return {"type": "favorite_device_query"}

            words = [
                word for word in cmd.split()
                if len(word) > 2 and word not in self.FAVORITE_STOPWORDS
            ]

            if not words:
                return {"type": "device_not_found", "query": cmd}

            query = " ".join(words)

            try:
                devices = registry.search(query)
                devices = self._filter_actionable(query, devices)
            except Exception:
                devices = []

            if not devices:
                return {"type": "device_not_found", "query": cmd}

            return {"type": "set_favorite_device", "entity_id": devices[0].get("entity_id")}

        # ==================================================
        # MEMÓRIA / HISTÓRICO (Fase 6.5)
        # ==================================================

        if self.contains_any(
            cmd,
            [
                "o que voce lembra de mim", "o que você lembra de mim",
                "o que voce sabe sobre mim", "o que você sabe sobre mim",
                "meu historico", "meu histórico",
                "conte o que sabe sobre mim",
            ],
        ):
            return {"type": "memory_summary"}

        # ==================================================
        # SISTEMA
        # ==================================================

        # "home assistant" falado sai embaralhado do Whisper de formas
        # imprevisíveis (ex: "romero-sistente", "romero assistante",
        # "homework assisting" — até "status" vira "está-lo"/"start" às
        # vezes, então não dá pra exigir a palavra "status" junto). O
        # único pedaço que sobrevive em todas as variações observadas é o
        # miolo "sist" (as-SIST-ente/as-SIST-ant/as-SIST-ing) — raro
        # aparecer por acaso numa frase sobre a casa, e o pior caso de
        # falso positivo é só responder "Home Assistant está online"
        # fora de contexto. Exceto que "sist" também aparece embutido no
        # verbo "assistir" (as-SIST-ir) — "vou assistir uma série" batia
        # aqui e respondia status do HA em vez de qualquer coisa sobre o
        # pedido real. Excluído explicitamente, sem enfraquecer o match
        # solto de "sist" pros outros casos de STT embaralhado.
        _FORMAS_ASSISTIR = ["assistir", "assisto", "assiste", "assistem", "assistimos", "assistindo", "assisti"]

        if self.contains_any(cmd, ["home assistant", "status home assistant"]) or (
            "sist" in cmd and not self.contains_any(cmd, _FORMAS_ASSISTIR)
        ):
            return {
                "type": "homeassistant_status"
            }

        # ==================================================
        # REGISTRY
        # ==================================================

        if self.contains_any(
            cmd,
            [
                "atualizar dispositivos",
                "atualizar registry",
                "recarregar dispositivos"
            ]
        ):
            return {
                "type": "registry_refresh"
            }

        # "dispositivos" sozinho lista tudo, mas "ligar dispositivos"/
        # "desligar dispositivos" não é um pedido de lista — sem essa
        # exclusão, esse "dispositivos" batia aqui primeiro e o verbo
        # de ação nunca chegava no bloco de ligar/desligar lá embaixo,
        # sempre devolvendo os 300+ entities em vez de agir (ou de
        # honestamente dizer "não encontrado" pra uma ação em massa
        # que não existe — não implementamos liga/desliga-tudo aqui de
        # propósito: um comando desses ligaria portão/ar/tudo junto,
        # risco físico demais pra um match por substring).
        if "dispositivos" in cmd and not self.contains_any(
            cmd,
            ["ligar", "desligar", "acender", "apagar", "ativar", "desativar", "abrir", "fechar"]
        ):
            return {
                "type": "device_list"
            }

        # ==================================================
        # CENAS E MODOS (checar antes do ligar/desligar genérico,
        # senão "ativar cena bom dia" cai na busca ampla e pode
        # perder pra outro dispositivo com nome parecido)
        # ==================================================

        if self.contains_any(cmd, ["cena", "modo"]):
            return self.scene_action(cmd)

        # ==================================================
        # MÍDIA
        # ==================================================

        media_service = self.match_media_service(cmd)

        if media_service:
            return self.media_action(cmd, media_service)

        # ==================================================
        # AÇÕES DE DISPOSITIVOS
        #
        # "desligar"/"desativar" precisam ser checados ANTES de
        # ligar/ativar — "ligar" é substring de "desligar" e "ativar"
        # é substring de "desativar", então checar ligar primeiro faz
        # todo comando de desligar cair (sempre) no turn_on por engano.
        # ==================================================

        if self.contains_any(
            cmd,
            [
                "desligar",
                "apagar",
                "desativar",
                "fechar"
            ]
        ):
            return self.device_action(cmd, "turn_off")

        if self.contains_any(
            cmd,
            [
                "ligar",
                "acender",
                "ativar",
                "abrir"
            ]
        ):
            return self.device_action(cmd, "turn_on")

        # ==================================================
        # PERGUNTA DE SENSOR
        # ==================================================

        if self.contains_any(
            cmd,
            [
                "temperatura",
                "umidade",
                "humidade",
                "bateria",
                "luminosidade",
                "pressao",
                "pressão"
            ]
        ):
            return self.sensor_query(cmd)

        # ==================================================
        # REDE (MikroTik, direto — sem passar pelo HA)
        #
        # Precisa vir ANTES do bloco STATUS genérico: "status da
        # rede" contém a palavra "status", que bateria primeiro no
        # device_status() e nunca chegaria aqui (não existe entidade
        # "rede" no HA pra achar).
        # ==================================================

        if self.contains_any(
            cmd,
            [
                "rede",
                "internet"
            ]
        ):
            return {
                "type": "network_status"
            }

        # ==================================================
        # STATUS
        # ==================================================

        if self.contains_any(
            cmd,
            [
                "status",
                "estado",
                "situacao",
                "situação"
            ]
        ):
            return self.device_status(cmd)

        # ==================================================
        # CONHECIMENTO GERAL (busca externa tipo Wikipedia,
        # ver knowledge_service.py) — checado por último, antes
        # do fallback pra unknown/LLM, pra não roubar nenhum
        # comando estruturado de cima.
        # ==================================================

        if self.contains_any(
            cmd,
            self.KNOWLEDGE_TRIGGERS
        ):
            return self.knowledge_search(command)

        return {
            "type": "unknown",
            "text": command
        }

    # ======================================================
    # DEVICE ACTION
    # ======================================================

    # Nomes de automação costumam ser frases descritivas ("Presença:
    # Chegada em casa liga a luz") que colidem por palavra com comandos
    # de verdade ("ligar a luz da sala") mesmo sem ter nada a ver com
    # o pedido. Só deixa automação entrar na busca se for isso mesmo
    # que a pessoa pediu.
    AUTOMATION_KEYWORDS = {"automacao", "automação", "rotina"}

    # Domínios que realmente têm serviço turn_on/turn_off. Sem essa
    # lista, um match de palavra podia cair num button/update/sensor
    # (ex: um botão de rotina do Google Home chamado "luzes ligadas ao
    # pôr do sol" batendo com "ligar a luz da sala") — e chamar
    # turn_on num domínio que só tem "press" só dá erro.
    TURN_ON_OFF_DOMAINS = {
        "light", "switch", "cover", "fan", "climate", "lock",
        "scene", "script", "input_boolean", "media_player", "automation",
    }

    def _filter_automations(self, cmd, devices):

        if self.contains_any(cmd, self.AUTOMATION_KEYWORDS):
            return devices

        return [
            d for d in devices
            if d.get("entity_id", "").split(".")[0] != "automation"
        ]

    def _filter_actionable(self, cmd, devices):

        devices = [
            d for d in devices
            if d.get("entity_id", "").split(".")[0] in self.TURN_ON_OFF_DOMAINS
        ]

        return self._filter_automations(cmd, devices)

    def device_action(self, cmd, action):

        try:
            devices = registry.search(cmd)
            devices = self._filter_actionable(cmd, devices)
        except Exception:
            return {"type": "unknown"}

        if not devices:
            return {"type": "device_not_found", "query": cmd}

        top = devices[0]
        tied = self._tied_by_name(devices, top)

        if len(tied) > 1:
            return {"type": "multiple_devices", "devices": tied}

        return {
            "type": "device_action",
            "action": action,
            "entity_id": top.get("entity_id")
        }

    # ======================================================
    # DEVICE STATUS
    # ======================================================

    def device_status(self, cmd):

        try:
            devices = registry.search(cmd)
            devices = self._filter_automations(cmd, devices)
        except Exception:
            return {"type": "unknown"}

        if not devices:
            return {"type": "device_not_found", "query": cmd}

        entity = devices[0]

        return {
            "type": "device_status",
            "entity_id": entity.get("entity_id")
        }

    def _tied_by_name(self, devices, top):
        """Só flags ambiguidade quando há dispositivos DIFERENTES com o
        mesmo nome amigável — não para qualquer lista de resultados
        (a maioria dos matches de score baixo tem nomes diferentes e
        não deve virar 'vários encontrados')."""

        top_name = registry.normalize(
            top.get("attributes", {}).get("friendly_name", top.get("entity_id", ""))
        )

        return [
            d for d in devices
            if registry.normalize(
                d.get("attributes", {}).get("friendly_name", d.get("entity_id", ""))
            ) == top_name
        ]

    # ======================================================
    # CENAS E MODOS
    # ======================================================

    SCENE_STOPWORDS = {"cena", "modo", "ativar", "ligar", "iniciar", "de", "da", "do"}

    def scene_action(self, cmd):

        try:
            candidates = registry.by_domain("scene") + registry.by_domain("script")
        except Exception:
            candidates = []

        # As cenas nem sempre têm uma entidade real registrada no HA (a
        # execução é 100% local desde a Fase 3 — o registro do HA é só um
        # resto que pode ficar desatualizado, ex: cena_chegando_de_carro
        # não existia lá quando foi criada 2026-08-20). Sem isso, dizer o
        # nome certinho de uma cena nova simplesmente não achava nada.
        known_ids = {c.get("entity_id") for c in candidates}
        for name, label in scenes_service.CENA_LABELS.items():
            entity_id = f"script.{name}"
            if entity_id not in known_ids:
                candidates.append({"entity_id": entity_id, "attributes": {"friendly_name": label}})

        if not candidates:
            return {"type": "device_not_found", "query": cmd}

        words = [
            word for word in cmd.split()
            if len(word) > 2 and word not in self.SCENE_STOPWORDS
        ]

        if not words:
            return {"type": "device_not_found", "query": cmd}

        best = None
        best_score = 0

        for entity in candidates:

            friendly = registry.normalize(
                entity.get("attributes", {}).get("friendly_name", "")
            )
            entity_id = registry.normalize(entity.get("entity_id", ""))

            score = sum(2 for w in words if w in friendly)
            score += sum(1 for w in words if w in entity_id)

            if score > best_score:
                best_score = score
                best = entity

        if not best:
            return {"type": "device_not_found", "query": cmd}

        return {
            "type": "device_action",
            "action": "turn_on",
            "entity_id": best.get("entity_id")
        }

    # ======================================================
    # MÍDIA
    #
    # Só volume — testado ao vivo contra o media_player real da casa
    # (Alexa Taiane). media_play/media_pause/next/previous via serviço
    # genérico dão 500 nessa integração (Alexa Media Player não
    # implementa esses serviços do jeito padrão do HA); melhor não
    # oferecer um comando que parece funcionar mas falha sempre.
    # ======================================================

    def match_media_service(self, cmd):

        if "volume" not in cmd:
            return None

        if self.contains_any(
            cmd,
            ["aumentar", "aumenta", "sobe", "sobre", "mais alto", "alto"]
        ):
            return "volume_up"

        if self.contains_any(
            cmd,
            ["diminuir", "diminui", "abaixar", "abaixa", "baixa", "baixo", "mais baixo"]
        ):
            return "volume_down"

        return None

    def media_action(self, cmd, service):

        try:
            players = registry.by_domain("media_player")
        except Exception:
            return {"type": "device_not_found", "query": cmd}

        if not players:
            return {"type": "device_not_found", "query": cmd}

        if len(players) == 1:
            entity = players[0]
        else:
            entity = self._best_media_match(cmd, players)
            if not entity:
                available = [p for p in players if p.get("state") not in ("unavailable", "unknown")]
                entity = (available or players)[0]

        return {
            "type": "device_action",
            "action": service,
            "entity_id": entity.get("entity_id")
        }

    def _best_media_match(self, cmd, players):

        words = [word for word in cmd.split() if len(word) > 2]

        best = None
        best_score = 0

        for entity in players:

            friendly = registry.normalize(
                entity.get("attributes", {}).get("friendly_name", "")
            )
            score = sum(1 for w in words if w in friendly)

            if score > best_score:
                best_score = score
                best = entity

        return best

    # ======================================================
    # SENSOR QUERY
    # ======================================================

    SENSOR_STOPWORDS = {
        "qual", "quais", "quanto", "quanta", "quantos", "quantas",
        "esta", "está", "de", "da", "do", "das", "dos",
        "no", "na", "nos", "nas", "um", "uma", "e", "o", "a"
    }

    SENSOR_SYNONYMS = {
        "temperatura": ["temperature", "temp"],
        "umidade": ["humidity"],
        "humidade": ["humidity"],
        "bateria": ["battery"],
        "luminosidade": ["illuminance", "lux"],
        "pressao": ["pressure"],
    }

    def sensor_query(self, cmd):

        not_found = {"type": "sensor_query", "entity_id": None}

        try:
            sensors = registry.by_domain("sensor")
        except Exception:
            return not_found

        words = [
            word
            for word in cmd.split()
            if len(word) > 2 and word not in self.SENSOR_STOPWORDS
        ]

        if not words:
            return not_found

        needed_matches = min(2, len(words))

        best = None
        best_score = 0

        for entity in sensors:

            friendly = registry.normalize(
                entity.get("attributes", {}).get("friendly_name", "")
            )
            entity_id = registry.normalize(entity.get("entity_id", ""))

            score = 0
            matched_words = 0

            for word in words:

                terms = [word] + self.SENSOR_SYNONYMS.get(word, [])
                word_matched = False

                for term in terms:

                    if term in friendly:
                        score += 2
                        word_matched = True

                    if term in entity_id:
                        score += 1
                        word_matched = True

                if word_matched:
                    matched_words += 1

            if matched_words < needed_matches:
                continue

            if score > best_score:
                best_score = score
                best = entity

        if not best:
            return not_found

        return {
            "type": "sensor_query",
            "entity_id": best.get("entity_id")
        }

    # ======================================================
    # CONHECIMENTO GERAL
    # ======================================================

    # Sem acento — `cmd` já passou por registry.normalize() antes de
    # chegar aqui, que remove acentuação (ver device_registry.normalize).
    # Sem "me" no início — command_parser.FILLER_WORDS já remove "me"
    # (palavra inteira, \b) antes do texto chegar aqui, então "me fala
    # sobre X" vira "fala sobre X" bem antes do intent_engine ver o comando.
    KNOWLEDGE_TRIGGERS = [
        "quem foi",
        "quem era",
        "quem e",
        "o que e",
        "o que significa",
        "pesquisar sobre",
        "pesquisa sobre",
        "pesquisar",
        "fala sobre",
    ]

    def knowledge_search(self, command):

        return {
            "type": "knowledge_search",
            "query": self.extract_knowledge_topic(command)
        }

    def extract_knowledge_topic(self, text):
        """Remove a frase-gatilho ('quem foi', 'o que e', ...) do texto,
        deixando só o tópico a pesquisar. Aceita tanto texto já tratado
        (`cmd`, minúsculo/sem acento) quanto o texto original bruto —
        casa o gatilho numa versão normalizada, mas fatia o texto de
        entrada (`registry.normalize` só faz troca 1-por-1 de caractere
        + strip, então os índices continuam alinhados). Reaproveitado
        por fred_service.py pra extrair o tópico a partir do comando
        original (preserva acento/maiúscula de nomes próprios), mesmo
        princípio já usado ali pro fallback do intent 'unknown'."""

        stripped = text.strip() if text else ""
        normalized = registry.normalize(stripped)

        # Mais longo primeiro: "pesquisar sobre" tem que vencer
        # "pesquisar" sozinho, senão sobra um "sobre" solto no tópico.
        for trigger in sorted(self.KNOWLEDGE_TRIGGERS, key=len, reverse=True):
            idx = normalized.find(trigger)
            if idx != -1:
                topic = stripped[idx + len(trigger):].strip(" ?.!")
                if topic:
                    return topic

        return stripped

    # ======================================================
    # UTIL
    # ======================================================

    def contains_any(self, text, words):

        if not text:
            return False

        for word in words:
            if word in text:
                return True

        return False


intent_engine = IntentEngine()
