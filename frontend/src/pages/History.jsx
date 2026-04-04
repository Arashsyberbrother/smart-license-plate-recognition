import React from 'react';
import { Box, Divider } from '@mui/material';
import PlateHistory from '../components/PlateHistory';
import Analytics from '../components/Analytics';

function History() {
  return (
    <Box>
      <PlateHistory />
      <Divider sx={{ my: 4 }} />
      <Analytics />
    </Box>
  );
}

export default History;
