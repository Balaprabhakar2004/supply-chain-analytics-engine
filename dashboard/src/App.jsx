import { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import api from './api';

const COLORS = ['#3B82C4', '#1B7A43', '#B7791F', '#B91C1C', '#6B7280', '#1E2A38'];

function StatCard({ label, value }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-2xl font-semibold text-gray-900">{value}</p>
    </div>
  );
}

function ChartCard({ title, children }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h3 className="text-sm font-semibold text-gray-900 mb-4">{title}</h3>
      {children}
    </div>
  );
}

function App() {
  const [summary, setSummary] = useState(null);
  const [regions, setRegions] = useState([]);
  const [shippingModes, setShippingModes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/stats/summary'),
      api.get('/stats/regions'),
      api.get('/stats/shipping-modes'),
      api.get('/stats/categories'),
      api.get('/stats/status'),
    ])
      .then(([s, r, sm, c, st]) => {
        setSummary(s.data);
        setRegions(r.data);
        setShippingModes(sm.data);
        setCategories(c.data.slice(0, 8));
        setStatuses(st.data);
      })
      .catch((err) => console.error('Failed to load stats', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-gray-500">Loading analytics...</div>;
  }

  return (
    <div className="min-h-screen bg-[#F4F6F8] p-8">
      <header className="mb-8">
        <h1 className="text-xl font-semibold text-gray-900">Supply Chain Analytics Engine</h1>
        <p className="text-sm text-gray-500 mt-1">
          Pipeline: Pandas cleaning → PySpark aggregation → AWS S3 → PostgreSQL → this dashboard
        </p>
      </header>

      {/* Summary stats */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <StatCard label="Total orders analyzed" value={summary.total_orders?.toLocaleString()} />
        <StatCard label="Total sales value" value={`$${summary.total_sales?.toLocaleString()}`} />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Sales by region */}
        <ChartCard title="Total sales by region">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={regions} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis type="number" fontSize={11} />
              <YAxis type="category" dataKey="order_region" fontSize={11} width={100} />
              <Tooltip />
              <Bar dataKey="total_sales" fill="#3B82C4" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Late delivery risk by shipping mode */}
        <ChartCard title="Late delivery risk % by shipping mode">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={shippingModes}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="shipping_mode" fontSize={11} />
              <YAxis fontSize={11} />
              <Tooltip />
              <Bar dataKey="late_risk_pct" fill="#B7791F" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Top categories */}
        <ChartCard title="Top 8 product categories by sales">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={categories} layout="vertical" margin={{ left: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis type="number" fontSize={11} />
              <YAxis type="category" dataKey="category_name" fontSize={10} width={120} />
              <Tooltip />
              <Bar dataKey="total_sales" fill="#1B7A43" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Order status breakdown */}
        <ChartCard title="Order status breakdown">
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={statuses}
                dataKey="order_count"
                nameKey="order_status"
                cx="50%" cy="50%"
                outerRadius={90}
                label={({ order_status }) => order_status}
                labelLine={false}
                fontSize={10}
              >
                {statuses.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: '11px' }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}

export default App;