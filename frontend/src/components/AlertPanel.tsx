import { useState, useEffect } from 'react';

interface Alert {
  id: number;
  city: string;
  message: string;
  severity: 'info' | 'warning' | 'critical';
  value: number;
  is_read: boolean;
  created_at: string;
}

interface AlertPanelProps {
  city?: string;
}

function AlertPanel({ city }: AlertPanelProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showOnlyUnread, setShowOnlyUnread] = useState(false);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000); // Odświeżaj co 30s
    return () => clearInterval(interval);
  }, [city, showOnlyUnread]);

  const fetchAlerts = async () => {
    try {
      const params = new URLSearchParams();
      if (city) params.append('city', city);
      if (showOnlyUnread) params.append('unread_only', 'true');
      params.append('limit', '20');

      const response = await fetch(`http://localhost:5000/api/alerts?${params}`);
      const data = await response.json();
      
      setAlerts(data.alerts);
      setUnreadCount(data.unread_count);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching alerts:', error);
      setLoading(false);
    }
  };

  const markAsRead = async (alertId: number) => {
    try {
      await fetch(`http://localhost:5000/api/alerts/${alertId}/read`, {
        method: 'PUT',
      });
      fetchAlerts();
    } catch (error) {
      console.error('Error marking alert as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const params = city ? `?city=${city}` : '';
      await fetch(`http://localhost:5000/api/alerts/mark-all-read${params}`, {
        method: 'PUT',
      });
      fetchAlerts();
    } catch (error) {
      console.error('Error marking all alerts as read:', error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 border-red-500 text-red-800';
      case 'warning':
        return 'bg-yellow-100 border-yellow-500 text-yellow-800';
      case 'info':
        return 'bg-blue-100 border-blue-500 text-blue-800';
      default:
        return 'bg-gray-100 border-gray-500 text-gray-800';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '🚨';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return '📢';
    }
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-blue-500 mx-auto"></div>
        <p className="mt-4 text-gray-600">Ładowanie alertów...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">
            🔔 Alerty Pogodowe
          </h2>
          {unreadCount > 0 && (
            <span className="inline-block mt-1 px-3 py-1 bg-red-500 text-white text-sm font-bold rounded-full">
              {unreadCount} nieprzeczytane
            </span>
          )}
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setShowOnlyUnread(!showOnlyUnread)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              showOnlyUnread
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {showOnlyUnread ? 'Pokaż wszystkie' : 'Tylko nieprzeczytane'}
          </button>

          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors"
            >
              Oznacz wszystkie jako przeczytane
            </button>
          )}
        </div>
      </div>

      {alerts.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-xl text-gray-500">
            {showOnlyUnread 
              ? '✅ Brak nieprzeczytanych alertów' 
              : '📭 Brak alertów do wyświetlenia'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`border-l-4 p-4 rounded-lg transition-all ${getSeverityColor(
                alert.severity
              )} ${alert.is_read ? 'opacity-60' : 'opacity-100'}`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">{getSeverityIcon(alert.severity)}</span>
                    <span className="font-bold uppercase text-sm">
                      {alert.severity}
                    </span>
                    <span className="text-sm text-gray-600">
                      • {alert.city}
                    </span>
                  </div>
                  
                  <p className="text-base mb-2">{alert.message}</p>
                  
                  <p className="text-sm text-gray-600">
                    {new Date(alert.created_at).toLocaleString('pl-PL', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>

                {!alert.is_read && (
                  <button
                    onClick={() => markAsRead(alert.id)}
                    className="ml-4 px-3 py-1 bg-white/50 hover:bg-white rounded-lg text-sm font-medium transition-colors"
                  >
                    Oznacz jako przeczytane
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AlertPanel;