import { useQuery } from "@tanstack/react-query";
import { getWeather } from "../api/weatherService";

export function useWeather() {

    return useQuery({

        queryKey: ["weather", "open-meteo"],

        queryFn: getWeather,

        refetchInterval: 10 * 60 * 1000,

        staleTime: 5 * 60 * 1000

    });

}
