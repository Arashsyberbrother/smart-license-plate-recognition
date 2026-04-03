import React, { useState, useEffect, useCallback } from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Pagination,
  Paper,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';
import RefreshIcon from '@mui/icons-material/Refresh';
import { getPlates, deletePlate } from '../services/api';
import { format } from 'date-fns';

const PAGE_SIZE = 10;

function PlateHistory() {
  const [plates, setPlates] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [deleteId, setDeleteId] = useState(null);

  const typeLabel = {
    passenger: 'سواری',
    motorcycle: 'موتورسیکلت',
    government: 'دولتی',
    unknown: 'نامشخص',
  };

  const fetchPlates = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        skip: (page - 1) * PAGE_SIZE,
        limit: PAGE_SIZE,
      };
      if (search) params.plate_number = search;
      if (filterType) params.plate_type = filterType;
      const response = await getPlates(params);
      const data = response.data;
      setPlates(data?.items || data || []);
      setTotal(data?.total || (Array.isArray(data) ? data.length : 0));
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [page, search, filterType]);

  useEffect(() => {
    fetchPlates();
  }, [fetchPlates]);

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await deletePlate(deleteId);
      setDeleteId(null);
      fetchPlates();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSearch = (e) => {
    setSearch(e.target.value);
    setPage(1);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom fontWeight="bold">
        تاریخچه پلاک‌ها
      </Typography>

      <Box display="flex" gap={2} mb={2} flexWrap="wrap" alignItems="center">
        <TextField
          label="جستجو بر اساس پلاک"
          variant="outlined"
          size="small"
          value={search}
          onChange={handleSearch}
          InputProps={{ startAdornment: <SearchIcon sx={{ mr: 0.5, color: 'text.secondary' }} /> }}
          sx={{ minWidth: 200 }}
        />
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>نوع پلاک</InputLabel>
          <Select
            value={filterType}
            label="نوع پلاک"
            onChange={(e) => { setFilterType(e.target.value); setPage(1); }}
          >
            <MenuItem value="">همه</MenuItem>
            <MenuItem value="passenger">سواری</MenuItem>
            <MenuItem value="motorcycle">موتورسیکلت</MenuItem>
            <MenuItem value="government">دولتی</MenuItem>
          </Select>
        </FormControl>
        <Tooltip title="بارگذاری مجدد">
          <IconButton onClick={fetchPlates} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>#</TableCell>
              <TableCell>پلاک</TableCell>
              <TableCell>نوع</TableCell>
              <TableCell>استان</TableCell>
              <TableCell>اطمینان</TableCell>
              <TableCell>تاریخ</TableCell>
              <TableCell>عملیات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                  <CircularProgress size={24} />
                </TableCell>
              </TableRow>
            ) : plates.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  رکوردی یافت نشد
                </TableCell>
              </TableRow>
            ) : (
              plates.map((plate, idx) => (
                <TableRow key={plate.id} hover>
                  <TableCell>{(page - 1) * PAGE_SIZE + idx + 1}</TableCell>
                  <TableCell>
                    <Typography fontFamily="monospace" fontWeight="bold">
                      {plate.plate_number}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={typeLabel[plate.plate_type] || plate.plate_type}
                      size="small"
                      color={plate.plate_type === 'passenger' ? 'primary' : 'default'}
                    />
                  </TableCell>
                  <TableCell>{plate.province || '---'}</TableCell>
                  <TableCell>
                    <Chip
                      label={`${((plate.confidence || 0) * 100).toFixed(1)}%`}
                      size="small"
                      color={plate.confidence > 0.85 ? 'success' : 'warning'}
                    />
                  </TableCell>
                  <TableCell>
                    {plate.created_at
                      ? format(new Date(plate.created_at), 'yyyy/MM/dd HH:mm')
                      : '---'}
                  </TableCell>
                  <TableCell>
                    <Tooltip title="حذف">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => setDeleteId(plate.id)}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {total > PAGE_SIZE && (
        <Box display="flex" justifyContent="center" mt={2}>
          <Pagination
            count={Math.ceil(total / PAGE_SIZE)}
            page={page}
            onChange={(_, v) => setPage(v)}
            color="primary"
          />
        </Box>
      )}

      <Dialog open={!!deleteId} onClose={() => setDeleteId(null)}>
        <DialogTitle>تأیید حذف</DialogTitle>
        <DialogContent>
          <DialogContentText>
            آیا مطمئن هستید که می‌خواهید این رکورد را حذف کنید؟
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteId(null)}>انصراف</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            حذف
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default PlateHistory;
