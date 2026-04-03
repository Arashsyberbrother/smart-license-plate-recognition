import React, { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  Grid,
  Snackbar,
  TextField,
  Typography,
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import { setApiKey, clearApiKey } from '../services/api';

function Settings() {
  const [apiUrl, setApiUrl] = useState(
    localStorage.getItem('api_url') || process.env.REACT_APP_API_URL || 'http://localhost:8000'
  );
  // API key is intentionally NOT persisted; it is kept in module memory only.
  const [apiKey, setApiKeyState] = useState('');
  const [wsUrl, setWsUrl] = useState(
    localStorage.getItem('ws_url') || process.env.REACT_APP_WS_URL || 'ws://localhost:8000'
  );
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const handleSave = () => {
    localStorage.setItem('api_url', apiUrl);
    localStorage.setItem('ws_url', wsUrl);
    setApiKey(apiKey);
    setSnackbar({ open: true, message: 'تنظیمات با موفقیت ذخیره شد', severity: 'success' });
  };

  const handleReset = () => {
    const defaultApiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    const defaultWsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
    setApiUrl(defaultApiUrl);
    setApiKeyState('');
    setWsUrl(defaultWsUrl);
    localStorage.removeItem('api_url');
    localStorage.removeItem('ws_url');
    clearApiKey();
    setSnackbar({ open: true, message: 'تنظیمات به مقادیر پیش‌فرض بازگردانده شد', severity: 'info' });
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom fontWeight="bold">
        تنظیمات
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                تنظیمات API
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Box display="flex" flexDirection="column" gap={2}>
                <TextField
                  label="آدرس API"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  fullWidth
                  variant="outlined"
                  helperText="آدرس پایه سرور بک‌اند"
                />
                <TextField
                  label="کلید API (اختیاری)"
                  value={apiKey}
                  onChange={(e) => setApiKeyState(e.target.value)}
                  fullWidth
                  variant="outlined"
                  type="password"
                  helperText="در صورت فعال بودن احراز هویت API وارد کنید"
                />
                <TextField
                  label="آدرس WebSocket"
                  value={wsUrl}
                  onChange={(e) => setWsUrl(e.target.value)}
                  fullWidth
                  variant="outlined"
                  helperText="آدرس WebSocket برای اتصال بلادرنگ"
                />

                <Box display="flex" gap={1}>
                  <Button
                    variant="contained"
                    startIcon={<SaveIcon />}
                    onClick={handleSave}
                  >
                    ذخیره تنظیمات
                  </Button>
                  <Button variant="outlined" onClick={handleReset}>
                    بازگردانی
                  </Button>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                اطلاعات سیستم
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">نسخه برنامه</Typography>
                  <Typography variant="body2">1.0.0</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">فریم‌ورک</Typography>
                  <Typography variant="body2">React 18 + FastAPI</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">موتور تشخیص</Typography>
                  <Typography variant="body2">YOLOv8 + EasyOCR</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="textSecondary">پایگاه داده</Typography>
                  <Typography variant="body2">SQLite</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar((s) => ({ ...s, open: false }))}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
}

export default Settings;
