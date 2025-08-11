/**
 * Main App Component
 * 
 * Root component that sets up routing, theme provider, and global state
 * Provides the main structure for the AI Floor Plan Compliance Checker
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Import contexts and providers
import { ThemeProvider } from './utils/ThemeContext';
import { AnalysisProvider } from './utils/AnalysisContext';

// Import main layout components
import Layout from './components/Layout/Layout';

// Import page components
import HomePage from './pages/HomePage';
import AnalysisPage from './pages/AnalysisPage';
import ResultsPage from './pages/ResultsPage';

// Import utility components
import ErrorBoundary from './components/Common/ErrorBoundary';
import LoadingProvider from './components/Common/LoadingProvider';

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <LoadingProvider>
          <AnalysisProvider>
            <Router>
              <Layout>
                <Routes>
                  {/* Home page - upload and start analysis */}
                  <Route path="/" element={<HomePage />} />
                  
                  {/* Analysis page - show processing status */}
                  <Route path="/analysis" element={<AnalysisPage />} />
                  
                  {/* Results page - show analysis results */}
                  <Route path="/results" element={<ResultsPage />} />
                  
                  {/* Redirect any unknown routes to home */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Layout>
            </Router>
          </AnalysisProvider>
        </LoadingProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
