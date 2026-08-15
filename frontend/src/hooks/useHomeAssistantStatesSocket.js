import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";

const RECONNECT_DELAY_MS = 3000;

function wsUrl() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}/casa/api/homeassistant/ws`;
}

// Mantém o cache do react-query (queryKey ["homeassistant","states"], lido
// por useHomeAssistantStates tanto em hooks/ quanto em
// modules/jarvis/services/haApi.js) atualizado via WebSocket em vez de
// polling — cada componente continua chamando useQuery normalmente, só que
// agora o dado chega empurrado. Montar uma única vez perto da raiz (App.jsx).
export function useHomeAssistantStatesSocket() {
    const queryClient = useQueryClient();

    useEffect(() => {
        let stopped = false;
        let socket = null;
        let reconnectTimer = null;

        function applyMessage(msg) {
            if (msg.type === "snapshot") {
                queryClient.setQueryData(["homeassistant", "states"], msg.states);
                return;
            }

            if (msg.type === "state_changed") {
                queryClient.setQueryData(["homeassistant", "states"], (prev) => {
                    if (!prev) return prev;
                    const idx = prev.findIndex((e) => e.entity_id === msg.entity_id);

                    if (!msg.new_state) {
                        return idx === -1 ? prev : prev.filter((e) => e.entity_id !== msg.entity_id);
                    }

                    if (idx === -1) return [...prev, msg.new_state];

                    const next = [...prev];
                    next[idx] = msg.new_state;
                    return next;
                });
            }
        }

        function connect() {
            if (stopped) return;

            socket = new WebSocket(wsUrl());

            socket.onmessage = (event) => {
                try {
                    applyMessage(JSON.parse(event.data));
                } catch {
                    // mensagem inválida — ignora, não derruba a conexão
                }
            };

            socket.onclose = () => {
                if (!stopped) {
                    reconnectTimer = setTimeout(connect, RECONNECT_DELAY_MS);
                }
            };

            socket.onerror = () => {
                socket.close();
            };
        }

        connect();

        return () => {
            stopped = true;
            clearTimeout(reconnectTimer);
            socket?.close();
        };
    }, [queryClient]);
}
