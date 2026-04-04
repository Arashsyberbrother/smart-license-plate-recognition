import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  Paper,
  Typography,
  Alert,
  Chip,
  Grid,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import SearchIcon from '@mui/icons-material/Search';
import { detectPlate } from '../services/api';

function PlateDetector() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const selected = acceptedFiles[0];
    if (selected) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
      setResult(null);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpeg', '.jpg', '.png', '.bmp', '.webp'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  });

  const handleDetect = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await detectPlate(formData);
      setResult(response.data);
    } catch (err) {
      setError(err.message || 'خطا در تشخیص پلاک');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  const typeLabel = {
    passenger: 'سواری',
    motorcycle: 'موتورسیکلت',
    government: 'دولتی',
    unknown: 'نامشخص',
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom fontWeight="bold">
        تشخیص پلاک خودرو
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Paper
                {...getRootProps()}
                sx={{
                  p: 4,
                  textAlign: 'center',
                  cursor: 'pointer',
                  border: '2px dashed',
                  borderColor: isDragActive ? 'primary.main' : 'grey.400',
                  backgroundColor: isDragActive ? 'primary.50' : 'grey.50',
                  transition: 'all 0.2s',
                  '&:hover': { borderColor: 'primary.main', backgroundColor: 'primary.50' },
                }}
                elevation={0}
              >
                <input {...getInputProps()} />
                <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
                <Typography variant="body1" color="textSecondary">
                  {isDragActive
                    ? 'فایل را اینجا رها کنید...'
                    : 'تصویر را اینجا بکشید یا کلیک کنید'}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  JPG, PNG, BMP (حداکثر ۱۰ مگابایت)
                </Typography>
              </Paper>

              {preview && (
                <Box mt={2} textAlign="center">
                  <img
                    src={preview}
                    alt="پیش‌نمایش"
                    style={{
                      maxWidth: '100%',
                      maxHeight: 300,
                      borderRadius: 8,
                      objectFit: 'contain',
                    }}
                  />
                </Box>
              )}

              <Box mt={2} display="flex" gap={1}>
                <Button
                  variant="contained"
                  startIcon={loading ? <CircularProgress size={16} color="inherit" /> : <SearchIcon />}
                  onClick={handleDetect}
                  disabled={!file || loading}
                  fullWidth
                >
                  {loading ? 'در حال پردازش...' : 'تشخیص پلاک'}
                </Button>
                {file && (
                  <Button variant="outlined" onClick={handleClear} disabled={loading}>
                    پاک کردن
                  </Button>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {result && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  نتیجه تشخیص
                </Typography>
                <Divider sx={{ mb: 2 }} />

                <Box
                  sx={{
                    background: 'linear-gradient(135deg, #1a237e 0%, #283593 100%)',
                    borderRadius: 2,
                    p: 2,
                    mb: 3,
                    textAlign: 'center',
                    border: '3px solid #ffd700',
                  }}
                >
                  <Typography
                    variant="h4"
                    sx={{
                      color: '#fff',
                      fontFamily: 'monospace',
                      letterSpacing: 4,
                      fontWeight: 'bold',
                    }}
                  >
                    {result.plate_number || '---'}
                  </Typography>
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">
                      نوع پلاک
                    </Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {typeLabel[result.plate_type] || result.plate_type || '---'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">
                      استان
                    </Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {result.province || '---'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">
                      اطمینان
                    </Typography>
                    <Chip
                      label={`${((result.confidence || 0) * 100).toFixed(1)}%`}
                      color={result.confidence > 0.85 ? 'success' : 'warning'}
                      size="small"
                    />
                  </Grid>
                  {result.id && (
                    <Grid item xs={6}>
                      <Typography variant="caption" color="textSecondary">
                        شناسه
                      </Typography>
                      <Typography variant="body2">#{result.id}</Typography>
                    </Grid>
                  )}
                </Grid>
              </CardContent>
            </Card>
          )}

          {!result && !error && (
            <Box
              display="flex"
              alignItems="center"
              justifyContent="center"
              height={200}
              sx={{ color: 'text.secondary' }}
            >
              <Typography variant="body1">
                تصویر را بارگذاری کنید تا نتیجه اینجا نمایش داده شود
              </Typography>
            </Box>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}

export default PlateDetector;
