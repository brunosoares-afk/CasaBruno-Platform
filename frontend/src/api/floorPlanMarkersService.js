import api from "../services/api";

export async function getFloorPlanMarkers() {
    const { data } = await api.get("/api/uploads/floor-plan/markers");
    return data.markers;
}

export async function saveFloorPlanMarkers(markers) {
    const { data } = await api.put("/api/uploads/floor-plan/markers", { markers });
    return data.markers;
}
