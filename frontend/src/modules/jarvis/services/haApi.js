import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../../../services/api";
import { useHomeAssistantStates } from "../../../hooks/useHomeAssistantStates";

// Reexportado em vez de duplicado — essa mesma queryKey já é alimentada em
// tempo real pelo useHomeAssistantStatesSocket (montado em App.jsx), então
// só faz sentido ter uma implementação do hook, não duas com intervalos
// de poll diferentes brigando pela mesma queryKey.
export { useHomeAssistantStates };

export async function callHaService(domain, service, entityId, data = {}) {
    const res = await api.post("/homeassistant/service", {
        domain,
        service,
        data: { entity_id: entityId, ...data },
    });
    return res.data;
}

export function indexStates(states) {
    const map = {};
    for (const s of states || []) map[s.entity_id] = s;
    return map;
}

export function useHaServiceCall() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ domain, service, entityId, data }) =>
            callHaService(domain, service, entityId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["homeassistant", "states"] });
        },
    });
}

export function cameraSnapshotUrl(entityId) {
    return `${api.defaults.baseURL}/homeassistant/camera/${entityId}`;
}

export async function getHaAreas() {
    const res = await api.get("/homeassistant/areas");
    return res.data; // [{area_id, name, entity_ids}]
}

// Registry (área/dispositivo/entidade) muda raramente — cache mais longo
// que o de states, e o próprio backend já cacheia por 5min do lado dele.
export function useHomeAssistantAreas() {
    return useQuery({
        queryKey: ["homeassistant", "areas"],
        queryFn: getHaAreas,
        staleTime: 5 * 60 * 1000,
    });
}

export async function getHaScenes() {
    const res = await api.get("/homeassistant/scenes");
    return res.data; // [{entity_id, label}]
}

// Lista fixa no backend (scenes_service.CENA_LABELS), só muda quando uma
// cena nova é criada no código — mesmo cache longo das áreas.
export function useHomeAssistantScenes() {
    return useQuery({
        queryKey: ["homeassistant", "scenes"],
        queryFn: getHaScenes,
        staleTime: 5 * 60 * 1000,
    });
}
