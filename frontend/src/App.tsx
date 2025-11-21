import { useState } from 'react';
import WeatherCard from './components/WeatherCard';
import AlertPanel from './components/AlertPanel';
import AlertRuleManager from './components/AlertRuleManager';
import useWeatherData from './hooks/useWeatherData';
import './App.css';

function App() {
  const { data, loading, error } = useWeatherData();
  const [activeTab, setActiveTab] = useState<'weather' | 'alerts' | 'rules'>('weather');

  // Pobierz listę miast z danych pogodowych
  const cities = data.length > 0 ? data.map(w => w.city) : ['Warszawa', 'Yakutsk'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-400 via-blue-500 to-blue-600 p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <h1 className="text-4xl font-bold text-white text-center mb-2">
          🌤️ Stacja Pogodowa
        </h1>
        <p className="text-white/80 text-center">System monitoringu pogody z alertami</p>
      </div>

      {/* Tabs Navigation */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="bg-white/20 backdrop-blur-sm rounded-lg p-1 flex gap-2">
          <button
            onClick={() => setActiveTab('weather')}
            className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'weather'
                ? 'bg-white text-blue-600 shadow-lg'
                : 'text-white hover:bg-white/10'
            }`}
          >
            🌡️ Pogoda
          </button>
          <button
            onClick={() => setActiveTab('alerts')}
            className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'alerts'
                ? 'bg-white text-blue-600 shadow-lg'
                : 'text-white hover:bg-white/10'
            }`}
          >
            🔔 Alerty
          </button>
          <button
            onClick={() => setActiveTab('rules')}
            className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'rules'
                ? 'bg-white text-blue-600 shadow-lg'
                : 'text-white hover:bg-white/10'
            }`}
          >
            ⚙️ Reguły
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto">
        {/* Weather Tab */}
        {activeTab === 'weather' && (
          <>
            {loading && (
              <div className="flex flex-col items-center justify-center py-16">
                <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-white"></div>
                <p className="mt-4 text-white text-lg">Ładowanie danych pogodowych...</p>
              </div>
            )}

            {error && (
              <div className="bg-red-500/90 backdrop-blur-sm text-white rounded-xl p-6 text-center">
                <strong className="text-xl">⚠️ Błąd</strong>
                <p className="text-sm mt-2">
                  Nie można połączyć się z API. Upewnij się, że Flask API działa na
                  http://localhost:5000
                </p>
              </div>
            )}

            {!loading && !error && data.length > 0 && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                  {data.map((weather) => (
                    <WeatherCard key={weather.id} weather={weather} />
                  ))}
                </div>

                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-center">
                  <p className="text-white text-lg">
                    🕐 Ostatnia aktualizacja:{' '}
                    {data[0].received_at
                      ? new Date(data[0].received_at).toLocaleString('pl-PL', {
                          weekday: 'long',
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })
                      : 'Brak danych'}
                  </p>
                </div>
              </>
            )}

            {!loading && !error && data.length === 0 && (
              <div className="bg-yellow-500/90 backdrop-blur-sm text-white rounded-xl p-8 text-center">
                <p className="text-xl font-semibold">📭 Brak danych</p>
                <p className="mt-2">Nie znaleziono żadnych odczytów pogodowych.</p>
                <p className="mt-2 text-sm">
                  Upewnij się, że Weather Collector jest uruchomiony i publikuje dane.
                </p>
              </div>
            )}
          </>
        )}

        {/* Alerts Tab */}
        {activeTab === 'alerts' && <AlertPanel />}

        {/* Rules Tab */}
        {activeTab === 'rules' && <AlertRuleManager cities={cities} />}
      </div>
    </div>
  );
}

export default App;