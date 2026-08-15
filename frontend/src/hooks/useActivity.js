import { useQuery } from "@tanstack/react-query";
import { getActivity, getWhatsappStatus } from "../api/activityService";

export function useActivity(limit = 10, hours = 24) {

    return useQuery({

        queryKey: ["fred", "activity", limit, hours],

        queryFn: () => getActivity(limit, hours),

        refetchInterval: 15000,

        staleTime: 10000

    });

}

export function useWhatsappStatus() {

    return useQuery({

        queryKey: ["whatsapp", "status"],

        queryFn: getWhatsappStatus,

        refetchInterval: 15000,

        staleTime: 10000

    });

}
