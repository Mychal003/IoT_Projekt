import WeatherCard from './components/WeatherCard'
import useWeatherData from './hooks/useWeatherData';
import './App.css'

function App() {

  const { data, loading, error} = useWeatherData();


  return (
    <div className="min-h-screen bd-gradient-to-br from-blue-400 via-blue-500 to-blue-600 p-8">
      <h1>Stacja pogodowa</h1>

    {loading && (
      <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-white">
      </div>
    )}

     
    {error && (
      <div>
      <strong>Błąd</strong>
      <p className="text-sm mt-2"> Upewnij się, że Flask API działa na http://localhost:5000</p>
      </div>
    )}



    {!loading && !error && data.length > 0 && (
      <>
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {data.map((weather) => (
        <WeatherCard key={weather.id} weather={weather}/>
      ))}
      </div>

      <div className="fixed bottom-0 left-0 right-0 mx-auto mt-8 py-4">
          <p className="text-lg">
            Ostatnia aktualizacja: {data[0].received_at ? new Date(data[0].received_at).toLocaleTimeString('pl-PL', {
              weekday: 'long',
              year: 'numeric',  
              month: 'long',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            }) : 'Brak danych'}  
          </p>
      </div>
      </>
    )}




    {}
    {!loading && !error && data.length === 0 && (
      <div className="max-w-2xl mx-auto border-red-400 text-red-700 rounded">
          <strong>Brak danych:</strong> Nie znaleziono żadnych odczytów pogodowych.
      </div>
    )}

    </div>
  );
}
export default App;