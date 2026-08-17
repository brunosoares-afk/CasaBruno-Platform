import api from "../services/api";

export async function getStates() {
    const { data } = await api.get("/homeassistant/states");
    return data;
}

export async function callService(domain, service, data = {}) {
    const { data: result } = await api.post("/homeassistant/service", {
        domain,
        service,
        data
    });
    return result;
}

export function cameraSnapshotUrl(entityId) {
    return `${api.defaults.baseURL}/homeassistant/camera/${entityId}?t=${Date.now()}`;
}

export function entityPictureUrl(entityId) {
    return `${api.defaults.baseURL}/homeassistant/entity_picture/${entityId}`;
}
