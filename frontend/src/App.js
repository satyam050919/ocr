import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import DocumentValidation from './pages/DocumentValidation';
import DocumentTagging from './pages/DocumentTagging';
import AttributeExtraction from './pages/AttributeExtraction';
import DocumentSplitting from './pages/DocumentSplitting';
import Settings from './pages/Settings';

function App() {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Navigation />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          pt: 8,
          px: 2,
          pb: 4,
        }}
      >
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/validation" element={<DocumentValidation />} />
            <Route path="/tagging" element={<DocumentTagging />} />
            <Route path="/extraction" element={<AttributeExtraction />} />
            <Route path="/splitting" element={<DocumentSplitting />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
}

export default App;
