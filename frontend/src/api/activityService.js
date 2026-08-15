import api from "../services/api";

export async function getActivity(limit = 10, hours = 24) {
    const { data } = await api.get("/activity", { params: { limit, hours } });
    return data;
}

export async function getWhatsappStatus() {
    const { data } = await api.get("/whatsapp/status");
    return data;
}
