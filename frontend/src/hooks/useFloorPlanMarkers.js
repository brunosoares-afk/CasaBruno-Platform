import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getFloorPlanMarkers, saveFloorPlanMarkers } from "../api/floorPlanMarkersService";

// Marcadores só mudam quando alguém edita em Gerência — mesma convenção de
// dado raramente mutável usada em useHomeAssistantAreas.
export function useFloorPlanMarkers() {
    return useQuery({
        queryKey: ["floor-plan-markers"],
        queryFn: getFloorPlanMarkers,
        staleTime: 5 * 60 * 1000,
    });
}

export function useSaveFloorPlanMarkers() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: saveFloorPlanMarkers,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["floor-plan-markers"] });
        },
    });
}
