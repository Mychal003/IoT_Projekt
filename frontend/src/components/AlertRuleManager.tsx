import { useState, useEffect } from 'react';

interface AlertRule {
  id: number;
  name: string;
  city: string;
  condition_type: string;
  operator: string;
  threshold: number;
  is_active: boolean;
  created_at: string;
}

interface AlertRuleManagerProps {
  cities: string[];
}

function AlertRuleManager({ cities }: AlertRuleManagerProps) {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    city: cities[0] || '',
    condition_type: 'temperature',
    operator: '>',
    threshold: 30,
  });

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/alert-rules');
      const data = await response.json();
      setRules(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching alert rules:', error);
      setLoading(false);
    }
  };

  const createRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await fetch('http://localhost:5000/api/alert-rules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      fetchRules();
      setShowForm(false);
      setFormData({
        name: '',
        city: cities[0] || '',
        condition_type: 'temperature',
        operator: '>',
        threshold: 30,
      });
    } catch (error) {
      console.error('Error creating alert rule:', error);
    }
  };

  const toggleRule = async (ruleId: number) => {
    try {
      await fetch(`http://localhost:5000/api/alert-rules/${ruleId}/toggle`, {
        method: 'PUT',
      });
      fetchRules();
    } catch (error) {
      console.error('Error toggling rule:', error);
    }
  };

  const deleteRule = async (ruleId: number) => {
    if (!confirm('Czy na pewno chcesz usunąć tę regułę?')) return;
    
    try {
      await fetch(`http://localhost:5000/api/alert-rules/${ruleId}`, {
        method: 'DELETE',
      });
      fetchRules();
    } catch (error) {
      console.error('Error deleting rule:', error);
    }
  };

  const conditionLabels: Record<string, string> = {
    temperature: 'Temperatura',
    humidity: 'Wilgotność',
    pressure: 'Ciśnienie',
    wind_speed: 'Prędkość wiatru',
  };

  const conditionUnits: Record<string, string> = {
    temperature: '°C',
    humidity: '%',
    pressure: 'hPa',
    wind_speed: 'm/s',
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-blue-500 mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">⚙️ Zarządzanie Regułami Alertów</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          {showForm ? '✕ Anuluj' : '+ Dodaj regułę'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={createRule} className="mb-6 p-6 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">Nowa reguła alertu</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nazwa reguły
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
                placeholder="np. Ekstremalna temperatura"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Miasto
              </label>
              <select
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {cities.map((city) => (
                  <option key={city} value={city}>
                    {city}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Warunek
              </label>
              <select
                value={formData.condition_type}
                onChange={(e) => setFormData({ ...formData, condition_type: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {Object.entries(conditionLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Operator
              </label>
              <select
                value={formData.operator}
                onChange={(e) => setFormData({ ...formData, operator: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value=">">{'>'} większy niż</option>
                <option value="<">{'<'} mniejszy niż</option>
                <option value=">=">{'>='} większy lub równy</option>
                <option value="<=">{'<='} mniejszy lub równy</option>
                <option value="==">{'=='} równy</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Próg ({conditionUnits[formData.condition_type]})
              </label>
              <input
                type="number"
                step="0.1"
                value={formData.threshold}
                onChange={(e) =>
                  setFormData({ ...formData, threshold: parseFloat(e.target.value) })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="mt-4 px-6 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors"
          >
            Utwórz regułę
          </button>
        </form>
      )}

      <div className="space-y-4">
        {rules.length === 0 ? (
          <p className="text-center text-gray-500 py-8">
            Brak zdefiniowanych reguł. Dodaj pierwszą regułę!
          </p>
        ) : (
          rules.map((rule) => (
            <div
              key={rule.id}
              className={`p-4 rounded-lg border-2 transition-all ${
                rule.is_active
                  ? 'bg-white border-green-300'
                  : 'bg-gray-50 border-gray-300 opacity-60'
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-bold text-gray-800">{rule.name}</h3>
                    <span
                      className={`px-2 py-1 rounded text-xs font-semibold ${
                        rule.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-200 text-gray-600'
                      }`}
                    >
                      {rule.is_active ? '✓ Aktywna' : '✕ Nieaktywna'}
                    </span>
                  </div>
                  
                  <p className="text-gray-700">
                    📍 {rule.city} • {conditionLabels[rule.condition_type]} {rule.operator}{' '}
                    {rule.threshold}
                    {conditionUnits[rule.condition_type]}
                  </p>
                  
                  <p className="text-sm text-gray-500 mt-1">
                    Utworzona: {new Date(rule.created_at).toLocaleDateString('pl-PL')}
                  </p>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => toggleRule(rule.id)}
                    className={`px-3 py-1 rounded-lg font-medium transition-colors ${
                      rule.is_active
                        ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
                        : 'bg-green-100 text-green-800 hover:bg-green-200'
                    }`}
                  >
                    {rule.is_active ? '⏸ Wyłącz' : '▶ Włącz'}
                  </button>
                  
                  <button
                    onClick={() => deleteRule(rule.id)}
                    className="px-3 py-1 bg-red-100 text-red-800 rounded-lg font-medium hover:bg-red-200 transition-colors"
                  >
                    🗑 Usuń
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default AlertRuleManager;