import { useEffect, useState } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const initialForm = {
  locality: 'Andheri West',
  bhk: 2,
  area_sqft: 850,
  furnishing: 'semi_furnished',
  distance_to_station_km: 1.2,
};

function App() {
  const [localities, setLocalities] = useState([]);
  const [status, setStatus] = useState('loading');
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchLocalities = async () => {
      try {
        const response = await fetch(`${API_BASE}/localities`);
        if (!response.ok) throw new Error('Unable to fetch localities');
        const data = await response.json();
        setLocalities(data.localities || []);
        setStatus('ready');
      } catch (err) {
        setStatus('error');
        setError(err.message || 'Could not connect to the API');
      }
    };

    fetchLocalities();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setStatus('loading');

    try {
      const response = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          locality: form.locality,
          bhk: Number(form.bhk),
          area_sqft: Number(form.area_sqft),
          furnishing: form.furnishing,
          distance_to_station_km: Number(form.distance_to_station_km),
        }),
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || 'Prediction request failed');
      }

      setResult(payload);
      setStatus('ready');
    } catch (err) {
      setStatus('error');
      setError(err.message || 'Prediction failed');
    }
  };

  return (
    <div className="page-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Portfolio Project</p>
          <h1>MMR Rental Market Intelligence</h1>
        </div>
        <div className="badge">FastAPI + React</div>
      </header>

      <main className="grid">
        <section className="panel left-panel">
          <h2>Fair Rent Estimator</h2>
          <form onSubmit={handleSubmit} className="form-grid">
            <label>
              Locality
              <select
                value={form.locality}
                onChange={(event) => setForm({ ...form, locality: event.target.value })}
              >
                {localities.map((locality) => (
                  <option key={locality} value={locality}>
                    {locality}
                  </option>
                ))}
              </select>
            </label>

            <label>
              BHK
              <input
                type="number"
                min="1"
                max="5"
                value={form.bhk}
                onChange={(event) => setForm({ ...form, bhk: event.target.value })}
              />
            </label>

            <label>
              Area (sq ft)
              <input
                type="number"
                min="200"
                step="50"
                value={form.area_sqft}
                onChange={(event) => setForm({ ...form, area_sqft: event.target.value })}
              />
            </label>

            <label>
              Furnishing
              <select
                value={form.furnishing}
                onChange={(event) => setForm({ ...form, furnishing: event.target.value })}
              >
                <option value="unfurnished">Unfurnished</option>
                <option value="semi_furnished">Semi Furnished</option>
                <option value="fully_furnished">Fully Furnished</option>
              </select>
            </label>

            <label>
              Distance to station (km)
              <input
                type="number"
                min="0.1"
                step="0.1"
                value={form.distance_to_station_km}
                onChange={(event) => setForm({ ...form, distance_to_station_km: event.target.value })}
              />
            </label>

            <button type="submit" disabled={status === 'loading'}>
              {status === 'loading' ? 'Estimating...' : 'Estimate Rent'}
            </button>
          </form>

          {error && <div className="message error">{error}</div>}
        </section>

        <section className="panel right-panel">
          <h2>Market Snapshot</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <span>Median rent</span>
              <strong>₹43,950</strong>
            </div>
            <div className="stat-card">
              <span>Avg rent/sqft</span>
              <strong>₹77</strong>
            </div>
            <div className="stat-card">
              <span>Model R²</span>
              <strong>0.943</strong>
            </div>
            <div className="stat-card">
              <span>Active regions</span>
              <strong>6</strong>
            </div>
          </div>

          {result && (
            <div className="result-card">
              <p className="result-label">Estimated rent</p>
              <h3>₹{result.predicted_rent_inr.toLocaleString('en-IN')}</h3>
              <div className="range-row">
                <span>Range</span>
                <strong>
                  ₹{result.range_inr.lower.toLocaleString('en-IN')} - ₹{result.range_inr.upper.toLocaleString('en-IN')}
                </strong>
              </div>
              <div className="label-pill">{result.fairness_label}</div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
