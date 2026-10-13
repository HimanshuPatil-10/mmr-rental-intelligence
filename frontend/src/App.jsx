import { useEffect, useMemo, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ComposedChart,
  Line,
  LineChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const currency = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
});

const initialForm = {
  locality: 'Andheri West',
  bhk: 2,
  area_sqft: 850,
  furnishing: 'semi_furnished',
  distance_to_station_km: 1.2,
};

const formatRupees = (value) => currency.format(Number(value) || 0);

function quantile(values, fraction) {
  const sorted = values.toSorted((left, right) => left - right);
  const position = (sorted.length - 1) * fraction;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  return sorted[lower] + (sorted[upper] - sorted[lower]) * (position - lower);
}

function summarize(values) {
  return {
    q1: quantile(values, 0.25),
    median: quantile(values, 0.5),
    q3: quantile(values, 0.75),
  };
}

const chartTooltipStyle = {
  background: '#101b2b',
  border: '1px solid rgba(148, 163, 184, 0.3)',
  borderRadius: 10,
  color: '#e5eef9',
};

function App() {
  const [localities, setLocalities] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [status, setStatus] = useState('loading');
  const [analyticsStatus, setAnalyticsStatus] = useState('loading');
  const [form, setForm] = useState(initialForm);
  const [filters, setFilters] = useState({ region: 'All', bhk: 'All', furnishing: 'All' });
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

    const fetchAnalytics = async () => {
      try {
        const response = await fetch(`${API_BASE}/analytics`);
        if (!response.ok) throw new Error('Unable to fetch chart data');
        setAnalytics(await response.json());
        setAnalyticsStatus('ready');
      } catch (err) {
        setAnalyticsStatus('error');
        setError(err.message || 'Could not load market analytics');
      }
    };

    fetchLocalities();
    fetchAnalytics();
  }, []);

  const filteredRecords = useMemo(() => {
    if (!analytics) return [];
    return analytics.records.filter((record) => (
      (filters.region === 'All' || record.region === filters.region)
      && (filters.bhk === 'All' || record.bhk === Number(filters.bhk))
      && (filters.furnishing === 'All' || record.furnishing === filters.furnishing)
    ));
  }, [analytics, filters]);

  const localityData = useMemo(() => {
    const groups = new Map();
    filteredRecords.forEach((record) => {
      if (!groups.has(record.locality)) {
        groups.set(record.locality, { locality: record.locality, values: [], listingCount: 0 });
      }
      const group = groups.get(record.locality);
      group.values.push(record.rent_per_sqft_inr);
      group.listingCount += 1;
    });
    return Array.from(groups.values())
      .map((group) => ({
        locality: group.locality,
        median: summarize(group.values).median,
        listingCount: group.listingCount,
      }))
      .sort((left, right) => right.median - left.median)
      .slice(0, 12);
  }, [filteredRecords]);

  const regionData = useMemo(() => {
    const groups = new Map();
    filteredRecords.forEach((record) => {
      if (!groups.has(record.region)) groups.set(record.region, []);
      groups.get(record.region).push(record.rent_per_sqft_inr);
    });
    return Array.from(groups, ([region, values]) => ({
      region,
      ...summarize(values),
      listingCount: values.length,
    })).sort((left, right) => right.median - left.median);
  }, [filteredRecords]);

  const stationData = useMemo(() => {
    const groups = new Map();
    filteredRecords.forEach((record) => {
      const key = Boolean(record.near_station_1km);
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(record.rent_per_sqft_inr);
    });
    return [true, false]
      .filter((nearStation) => groups.has(nearStation))
      .map((nearStation) => ({
        station: nearStation ? 'Within 1 km' : 'Beyond 1 km',
        median: summarize(groups.get(nearStation)).median,
        listingCount: groups.get(nearStation).length,
      }));
  }, [filteredRecords]);

  const scatterData = useMemo(() => {
    const maxPoints = 1800;
    const sample = [];
    let seed = 42;
    filteredRecords.forEach((record, index) => {
      const point = {
        area: record.area_sqft,
        rent: record.rent_inr,
        locality: record.locality,
        region: record.region,
        bhk: record.bhk,
      };
      if (sample.length < maxPoints) {
        sample.push(point);
        return;
      }
      seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
      const replacementIndex = Math.floor((seed / 4294967296) * (index + 1));
      if (replacementIndex < maxPoints) sample[replacementIndex] = point;
    });
    return sample;
  }, [filteredRecords]);

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

      <main>
        <div className="grid">
          <section className="panel left-panel">
            <h2>Fair Rent Estimator</h2>
            <form onSubmit={handleSubmit} className="form-grid">
              <label>
                Locality
                <select
                  value={form.locality}
                  onChange={(event) => setForm({ ...form, locality: event.target.value })}
                  disabled={!localities.length}
                >
                  {localities.map((locality) => (
                    <option key={locality} value={locality}>{locality}</option>
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

              <button type="submit" disabled={status === 'loading' || !localities.length}>
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
                <h3>{formatRupees(result.predicted_rent_inr)}</h3>
                <div className="range-row">
                  <span>Range</span>
                  <strong>
                    {formatRupees(result.range_inr.lower)} - {formatRupees(result.range_inr.upper)}
                  </strong>
                </div>
                <div className="label-pill">{result.fairness_label}</div>
              </div>
            )}
          </section>
        </div>

        <section className="panel analytics-panel">
          <div className="analytics-heading">
            <div>
              <p className="eyebrow">Explore the market</p>
              <h2>Rental Market Analytics</h2>
              <p className="section-intro">
                Compare localities, price spread, property size, and station proximity using
                {` ${filteredRecords.length.toLocaleString('en-IN')} `}processed listings.
              </p>
              <p className="dataset-notice">
                Uses the project’s synthetic/realistic Kaggle dataset; these are not live rental listings.
              </p>
            </div>
            <div className="filter-grid">
              <label>
                Region
                <select
                  value={filters.region}
                  onChange={(event) => setFilters({ ...filters, region: event.target.value })}
                >
                  <option value="All">All regions</option>
                  {(analytics?.regions || []).map((region) => (
                    <option key={region} value={region}>{region}</option>
                  ))}
                </select>
              </label>
              <label>
                BHK
                <select
                  value={filters.bhk}
                  onChange={(event) => setFilters({ ...filters, bhk: event.target.value })}
                >
                  <option value="All">All BHK</option>
                  {(analytics?.bhk_options || []).map((bhk) => (
                    <option key={bhk} value={bhk}>{bhk} BHK</option>
                  ))}
                </select>
              </label>
              <label>
                Furnishing
                <select
                  value={filters.furnishing}
                  onChange={(event) => setFilters({ ...filters, furnishing: event.target.value })}
                >
                  <option value="All">All types</option>
                  {(analytics?.furnishing_options || []).map((furnishing) => (
                    <option key={furnishing} value={furnishing}>
                      {furnishing.replaceAll('_', ' ')}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          </div>

          {analyticsStatus === 'loading' && (
            <div className="message">Loading chart data...</div>
          )}
          {analyticsStatus === 'error' && (
            <div className="message error">Unable to load analytics charts. {error}</div>
          )}
          {analyticsStatus === 'ready' && filteredRecords.length === 0 && (
            <div className="message">No listings match these filters.</div>
          )}

          {analyticsStatus === 'ready' && filteredRecords.length > 0 && (
            <div className="chart-grid">
              <article className="chart-card">
                <div className="chart-title">
                  <h3>Highest median rent per sq ft</h3>
                  <span>Top 12 localities</span>
                </div>
                <ResponsiveContainer width="100%" height={330}>
                  <BarChart data={localityData} layout="vertical" margin={{ left: 12, right: 24 }}>
                    <CartesianGrid stroke="#26364a" strokeDasharray="3 3" horizontal={false} />
                    <XAxis type="number" tickFormatter={(value) => `₹${value}`} stroke="#91a5bb" />
                    <YAxis
                      type="category"
                      dataKey="locality"
                      width={125}
                      tick={{ fill: '#cfe0ef', fontSize: 11 }}
                      interval={0}
                    />
                    <Tooltip
                      contentStyle={chartTooltipStyle}
                      formatter={(value, name) => [
                        name === 'median' ? `${formatRupees(value)} / sq ft` : value,
                        name === 'median' ? 'Median rent / sq ft' : 'Listings',
                      ]}
                      labelFormatter={(label) => label}
                    />
                    <Bar dataKey="median" name="Median rent / sq ft" fill="#48c7e8" radius={[0, 5, 5, 0]} />
                  </BarChart>
                </ResponsiveContainer>
                <p className="chart-note">Median rent per carpet-area sq ft; listing counts reflect the selected filters.</p>
              </article>

              <article className="chart-card">
                <div className="chart-title">
                  <h3>Rent per sq ft spread by region</h3>
                  <span>Q1, median, Q3</span>
                </div>
                <ResponsiveContainer width="100%" height={330}>
                  <LineChart data={regionData} margin={{ top: 12, right: 18, left: 4, bottom: 22 }}>
                    <CartesianGrid stroke="#26364a" strokeDasharray="3 3" />
                    <XAxis
                      dataKey="region"
                      angle={-18}
                      textAnchor="end"
                      interval={0}
                      height={58}
                      tick={{ fill: '#cfe0ef', fontSize: 10 }}
                    />
                    <YAxis tickFormatter={(value) => `₹${value}`} stroke="#91a5bb" />
                    <Tooltip
                      contentStyle={chartTooltipStyle}
                      formatter={(value, name) => [`${formatRupees(value)} / sq ft`, name.toUpperCase()]}
                    />
                    <Line dataKey="q1" name="Q1" stroke="#7894b2" strokeDasharray="4 4" dot={false} />
                    <Line dataKey="median" name="Median" stroke="#54d6bd" strokeWidth={3} />
                    <Line dataKey="q3" name="Q3" stroke="#7894b2" strokeDasharray="4 4" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
                <p className="chart-note">The middle 50% of listings lies between Q1 and Q3. Small samples may be less representative.</p>
              </article>

              <article className="chart-card">
                <div className="chart-title">
                  <h3>Area vs monthly rent</h3>
                  <span>{scatterData.length.toLocaleString('en-IN')} points shown</span>
                </div>
                <ResponsiveContainer width="100%" height={330}>
                  <ScatterChart margin={{ top: 12, right: 20, left: 8, bottom: 12 }}>
                    <CartesianGrid stroke="#26364a" strokeDasharray="3 3" />
                    <XAxis
                      type="number"
                      dataKey="area"
                      name="Area"
                      unit=" sq ft"
                      tick={{ fill: '#cfe0ef', fontSize: 11 }}
                      label={{ value: 'Carpet area (sq ft)', position: 'insideBottom', offset: -8, fill: '#91a5bb' }}
                    />
                    <YAxis
                      type="number"
                      dataKey="rent"
                      name="Monthly rent"
                      tickFormatter={(value) => `₹${Math.round(value / 1000)}k`}
                      tick={{ fill: '#cfe0ef', fontSize: 11 }}
                    />
                    <Tooltip
                      contentStyle={chartTooltipStyle}
                      formatter={(value, name) => [
                        name === 'Area' ? `${Number(value).toLocaleString('en-IN')} sq ft` : formatRupees(value),
                        name,
                      ]}
                      labelFormatter={(_, payload) => {
                        const point = payload?.[0]?.payload;
                        return point ? `${point.locality} · ${point.bhk} BHK` : '';
                      }}
                    />
                    <Scatter data={scatterData} fill="#b68cff" fillOpacity={0.55} />
                  </ScatterChart>
                </ResponsiveContainer>
                <p className="chart-note">A deterministic sample of at most 1,800 filtered observations is plotted for readability.</p>
              </article>

              <article className="chart-card">
                <div className="chart-title">
                  <h3>Station proximity comparison</h3>
                  <span>Median rent per sq ft</span>
                </div>
                <ResponsiveContainer width="100%" height={330}>
                  <BarChart data={stationData} margin={{ top: 18, right: 18, left: 8, bottom: 16 }}>
                    <CartesianGrid stroke="#26364a" strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="station" tick={{ fill: '#cfe0ef', fontSize: 12 }} />
                    <YAxis tickFormatter={(value) => `₹${value}`} stroke="#91a5bb" />
                    <Tooltip
                      contentStyle={chartTooltipStyle}
                      formatter={(value) => [`${formatRupees(value)} / sq ft`, 'Median rent']}
                      labelFormatter={(label, payload) => {
                        const count = payload?.[0]?.payload?.listingCount;
                        return count ? `${label} · ${count.toLocaleString('en-IN')} listings` : label;
                      }}
                    />
                    <Bar dataKey="median" fill="#ffad66" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
                <p className="chart-note">Proximity is an association in this dataset; this comparison does not establish causation.</p>
              </article>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
