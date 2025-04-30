import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';

// Import pages and layouts
import DashboardLayout from './components/layout/DashboardLayout';
import HomePage from './pages/HomePage';
import MyScenarios from './pages/MyScenarios';
import NewAnalysis from './pages/NewAnalysis';
import KnowledgeBase from './pages/KnowledgeBase';
import NotFound from './pages/NotFound';

// Dark theme with blue accent colors to match UI.png
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#3B82F6', // Blue color from UI.png
    },
    secondary: {
      main: '#10B981', // Green color for positive indicators
    },
    error: {
      main: '#EF4444', // Red color for negative indicators
    },
    warning: {
      main: '#F59E0B', // Amber color for warnings
    },
    background: {
      default: '#111827',
      paper: '#1F2937',
    },
    text: {
      primary: '#F9FAFB',
      secondary: '#D1D5DB',
    },
  },
  typography: {
    fontFamily: "'Inter', 'Roboto', 'Helvetica', 'Arial', sans-serif",
    h1: {
      fontWeight: 700,
    },
    h2: {
      fontWeight: 700,
    },
    h3: {
      fontWeight: 600,
    },
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
          <Routes>
            <Route path="/" element={<DashboardLayout />}>
              <Route index element={<HomePage />} />
              <Route path="scenarios" element={<MyScenarios />} />
              <Route path="new-analysis" element={<NewAnalysis />} />
              <Route path="knowledge-base" element={<KnowledgeBase />} />
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
