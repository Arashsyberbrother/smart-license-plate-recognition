import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Alert,
} from '@mui/material';
import SpeedIcon from '@mui/icons-material/Speed';
import TodayIcon from '@mui/icons-material/Today';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import AssessmentIcon from '@mui/icons-material/Assessment';
import { getDashboardStats, getPlates } from '../services/api';
import { format } from 'date-fns';

const REFRESH_INTERVAL = 30000;

function StatCard({ title, value, icon, color }) {
  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" fontWeight="bold">
              {value}
            </Typography>
          </Box>
          <Box
            sx={{
              bgcolor: `${color}.light`,
              borderRadius: 2,
              p: 1.5,
              color: `${color}.main`,
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recentPlates, setRecentPlates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const typeLabel = {
    passenger: 'سواری',
    motorcycle: 'موتورسیکلت',
    government: 'دولتی',
    unknown: 'نامشخص',
  };

  const fetchData = useCallback(async () => {
    try {
      const [statsRes, platesRes] = await Promise.all([
        getDashboardStats(),
        getPlates({ limit: 5, skip: 0 }),
      ]);
      setStats(statsRes.data);
      setRecentPlates(platesRes.data?.items || platesRes.data || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchData]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom fontWeight="bold" sx={{ mt: 3 }}>
        داشبورد
      </Typography>

      {error && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="کل تشخیص‌ها"
            value={stats?.total_detections ?? 0}
            icon={<AssessmentIcon fontSize="large" />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="امروز"
            value={stats?.today_detections ?? 0}
            icon={<TodayIcon fontSize="large" />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="نرخ موفقیت"
            value={`${((stats?.success_rate ?? 0) * 100).toFixed(1)}%`}
            icon={<CheckCircleIcon fontSize="large" />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="میانگین اطمینان"
            value={`${((stats?.avg_confidence ?? 0) * 100).toFixed(1)}%`}
            icon={<SpeedIcon fontSize="large" />}
            color="info"
          />
        </Grid>
      </Grid>

      <Typography variant="h6" gutterBottom>
        آخرین تشخیص‌ها
      </Typography>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>پلاک</TableCell>
              <TableCell>نوع</TableCell>
              <TableCell>استان</TableCell>
              <TableCell>اطمینان</TableCell>
              <TableCell>تاریخ</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {recentPlates.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  داده‌ای موجود نیست
                </TableCell>
              </TableRow>
            ) : (
              recentPlates.map((plate) => (
                <TableRow key={plate.id} hover>
                  <TableCell>
                    <Typography fontFamily="monospace" fontWeight="bold">
                      {plate.plate_number}
                    </Typography>
                  </TableCell>
                  <TableCell>{typeLabel[plate.plate_type] || plate.plate_type}</TableCell>
                  <TableCell>{plate.province || '---'}</TableCell>
                  <TableCell>{`${((plate.confidence || 0) * 100).toFixed(1)}%`}</TableCell>
                  <TableCell>
                    {plate.created_at
                      ? format(new Date(plate.created_at), 'yyyy/MM/dd HH:mm')
                      : '---'}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default Dashboard;
