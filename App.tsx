import React from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

// Layouts
import DashboardLayout from './components/Layout/DashboardLayout';

// Pages
import LoginPage from './pages/auth/LoginPage';
import SignupPage from './pages/auth/SignupPage';
import UploadSection from './pages/dashboard/UploadSection';
import AnalysisResults from './pages/dashboard/AnalysisResults';
import QASection from './pages/dashboard/QASection';

const ProtectedRoute = ({ children }: { children: React.ReactElement }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        
        {/* Protected Dashboard Routes */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/dashboard/upload" replace />} />
          <Route path="upload" element={<UploadSection />} />
          <Route path="results" element={<AnalysisResults />} />
          <Route path="qa" element={<QASection />} />
        </Route>

        <Route path="/" element={<Navigate to="/dashboard/upload" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

export default App;