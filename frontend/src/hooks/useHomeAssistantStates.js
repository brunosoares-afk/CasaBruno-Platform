import { useQuery } from "@tanstack/react-query";
import { getStates } from "../api/homeassistantService";

// Dado real chega via WebSocket (useHomeAssistantStatesSocket, montado uma
// vez em App.jsx, escreve direto no cache dessa queryKey) — o poll aqui é
// só rede de segurança caso o socket esteja caído, não o mecanismo
// principal, por isso o intervalo bem mais espaçado.
export function useHomeAssistantStates() {

    return useQuery({

        queryKey: ["homeassistant", "states"],

        queryFn: getStates,

        refetchInterval: 60000,

        staleTime: 30000

    });

}
