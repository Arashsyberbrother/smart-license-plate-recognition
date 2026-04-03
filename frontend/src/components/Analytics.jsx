import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CircularProgress,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Typography,
  Alert,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  ResponsiveContainer,
} from 'recharts';
import { getAnalyticsDaily, getAnalyticsDistribution } from '../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

function Analytics() {
  const [dailyData, setDailyData] = useState([]);
  const [distribution, setDistribution] = useState(null);
  const [days, setDays] = useState(7);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [dailyRes, distRes] = await Promise.all([
          getAnalyticsDaily(days),
          getAnalyticsDistribution(),
        ]);
        setDailyData(dailyRes.data || []);
        setDistribution(distRes.data || {});
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [days]);

  const typeLabel = {
    passenger: 'سواری',
    motorcycle: 'موتورسیکلت',
    government: 'دولتی',
    unknown: 'نامشخص',
  };

  const plateTypePieData = distribution?.by_type
    ? Object.entries(distribution.by_type).map(([key, value]) => ({
        name: typeLabel[key] || key,
        value,
      }))
    : [];

  const provinceBarData = distribution?.by_province
    ? Object.entries(distribution.by_province)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10)
        .map(([key, value]) => ({ province: key, count: value }))
    : [];

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={300}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {error && <Alert severity="warning" sx={{ mb: 2 }}>{error}</Alert>}

      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">تشخیص‌های روزانه</Typography>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>بازه</InputLabel>
          <Select value={days} label="بازه" onChange={(e) => setDays(e.target.value)}>
            <MenuItem value={7}>۷ روز</MenuItem>
            <MenuItem value={14}>۱۴ روز</MenuItem>
            <MenuItem value={30}>۳۰ روز</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                نمودار تشخیص‌های روزانه
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="#1976d2"
                    strokeWidth={2}
                    name="تعداد تشخیص"
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={5}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                توزیع نوع پلاک
              </Typography>
              {plateTypePieData.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={plateTypePieData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, percent }) =>
                        `${name} ${(percent * 100).toFixed(0)}%`
                      }
                    >
                      {plateTypePieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Box display="flex" justifyContent="center" alignItems="center" height={250}>
                  <Typography color="textSecondary">داده‌ای موجود نیست</Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={7}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                توزیع استان‌ها (۱۰ استان برتر)
              </Typography>
              {provinceBarData.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={provinceBarData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="province" type="category" width={80} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#1976d2" name="تعداد" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Box display="flex" justifyContent="center" alignItems="center" height={250}>
                  <Typography color="textSecondary">داده‌ای موجود نیست</Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Analytics;
