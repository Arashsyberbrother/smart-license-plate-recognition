import React from 'react';
import { Box, Divider } from '@mui/material';
import PlateDetector from '../components/PlateDetector';
import Dashboard from '../components/Dashboard';

function Home() {
  return (
    <Box>
      <PlateDetector />
      <Divider sx={{ my: 4 }} />
      <Dashboard />
    </Box>
  );
}

export default Home;
