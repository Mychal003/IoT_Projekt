export interface WeatherReading{
    id: number;
    city: string;
    temperature: number;
    humidity: number;
    pressure: number;
    wind_speed: number;
    weather: string;
    timestamp: number;
    received_at: string | null;
}


export interface AppState {
    data: WeatherReading[];
    error: string | null;
    loading: boolean;
    lastUpdate: Date | null;
}