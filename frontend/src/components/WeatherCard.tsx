import type { WeatherReading } from "../types/weather";

interface WeatherCardProps{
    weather: WeatherReading;
}


function getWeatherEmoji(description: string): string {
    const desc = description.toLowerCase();

    if (desc.includes('clear sky')) return '☀️';
    if (desc.includes('few clouds')) return '🌤️';
    if (desc.includes('scattered clouds')) return '🌥️';
    if (desc.includes('broken clouds')) return '☁️';
    if (desc.includes('shower rain')) return '☔';
    if (desc.includes('rain')) return '🌧️';
    if (desc.includes('thunderstorm')) return '⛈️';
    if (desc.includes('snow')) return '🌨️';
    if (desc.includes('mist')) return '⛆';

    return '☀️';
}




function WeatherCard({weather}: WeatherCardProps){

    const tempCelsius = (weather.temperature - 273).toFixed(1)
    return (

        <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300">
            
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
                {weather.city}
                <p className="text-4xl">{getWeatherEmoji(weather.weather)}</p>
            </h2>
            
            <div className="grid grid cols-2 gap-4">
            
            
            <div className="flex items-center space-x-2">
            <span className="text-2xl leading-none">🌡️</span>
            <div className="flex items-baseline space-x-2">
                <span className="text-sm text-gray-500">Temperatura:</span>
                <span className="text-lg font-bold text-blue-600">
                {tempCelsius}°C
                </span>
            </div>
            </div> 

            <div className="flex items-center space-x-2">
                <span className="text-2xl leading-none">💧</span>
                <div className="flex items-baseline space-x-2">
                <span className="text-sm text-gray-500">Wilgotność:</span>
                <span className="text-lg font-bold text-blue-600">
                    {weather.humidity}%
                </span>
            </div>
            </div>


            <div className="flex items-center space-x-2">
            <span className="text-2xl leading-none">🌀</span>
            <div className="flex items-baseline space-x-2">
                <span className="text-sm text-gray-500">Ciśnienie:</span>
                <span className="text-lg font-bold text-blue-600">
                {weather.pressure} hPa
                </span>
            </div>
            </div>

            <div className="flex items-center space-x-2">
            <span className="text-2xl leading-none">💨</span>
            <div className="flex items-baseline space-x-2">
                <span className="text-sm text-gray-500">Prędkość wiatru:</span>
                <span className="text-lg font-bold text-blue-600">
                {weather.wind_speed} m/s
                </span>
            </div>
            </div>
            
                
            </div>
            </div>
    );
}


export default WeatherCard