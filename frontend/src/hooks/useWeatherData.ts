import { useState, useEffect } from "react";
import type { WeatherReading } from "../types/weather";

interface UseWeatherDataReturn {
    data: WeatherReading[];
    loading: boolean;
    error: string | null;
}


function useWeatherData(): UseWeatherDataReturn {
    const [data, setData] = useState<WeatherReading[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async() => {
            try {
                console.log("Fetching data... ", new Date().toLocaleTimeString());
                setLoading(true);
                const response = await fetch("http://localhost:5000/api/weather/current");
                const json = await response.json();
                setData(json);
                setError(null);
            } catch (error) {
                if (error instanceof Error) {
                    console.error(error);
                    setError(error.message);
                } else {
                    setError("nieznany bład");
                }
            } finally {
                setLoading(false);
            }
        };

        fetchData();

        const interval = setInterval(()=> {
            console.log("Interval triggered!")
            fetchData();
        }, 300000);
        console.log('Interval started, ID:',interval);
        // cleanup -> zatrzymanie intervalu gdy komponent sie odmontuje

        return () => {
            console.log("Cleanup called, clearing interval:", interval);
            clearInterval(interval);
        };
    },[]); // pusta tablica = uruchom raz przy montowaniu

    return { data, loading, error};
}


export default useWeatherData;