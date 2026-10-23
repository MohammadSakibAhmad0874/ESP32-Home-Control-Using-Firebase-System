import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import PrivacyPage from './pages/PrivacyPage';
import TermsPage from './pages/TermsPage';
import ProtectedRoute from './components/ProtectedRoute';
import AdminRoute from './components/AdminRoute';
import { subscribeAuth, getUserRole } from './firebase/auth';

export default function App() {
  const [user, setUser] = useState(null);
  const [role, setRole] = useState('user');
  const [authInitialized, setAuthInitialized] = useState(false);

  useEffect(() => {
    const unsub = subscribeAuth(async (currentUser) => {
      setUser(currentUser);
      if (currentUser) {
        try {
          const userRole = await getUserRole(currentUser.uid);
          setRole(userRole || 'user');
        } catch {
          setRole('user');
        }
      } else {
        setRole('user');
      }
      setAuthInitialized(true);
    });

    return () => unsub();
  }, []);

  if (!authInitialized) {
    return (
      <div className="min-h-screen bg-[#0B0E14] flex flex-col items-center justify-center">
        <div className="w-12 h-12 rounded-full border-2 border-[#00D9FF] border-t-transparent animate-spin mb-4"></div>
        <p className="text-[#8B9BB4] text-xs font-mono tracking-widest uppercase">Initializing ApnaGhar Cloud...</p>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage user={user} role={role} />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        
        {/* Protected User Dashboard */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <UserDashboard user={user} role={role} />
            </ProtectedRoute>
          } 
        />

        {/* Protected Admin Dashboard */}
        <Route 
          path="/admin" 
          element={
            <AdminRoute>
              <AdminDashboard user={user} role={role} />
            </AdminRoute>
          } 
        />

        {/* Legal Pages */}
        <Route path="/privacy" element={<PrivacyPage user={user} role={role} />} />
        <Route path="/terms" element={<TermsPage user={user} role={role} />} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
