import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { subscribeAuth } from '../firebase/auth';

export default function ProtectedRoute({ children }) {
  const [user, setUser] = useState(undefined);

  useEffect(() => {
    const unsub = subscribeAuth((currentUser) => {
      setUser(currentUser);
    });
    return () => unsub();
  }, []);

  if (user === undefined) {
    return (
      <div className="min-h-screen bg-[#0B0E14] flex flex-col items-center justify-center">
        <div className="w-12 h-12 rounded-full border-2 border-[#00D9FF] border-t-transparent animate-spin mb-4"></div>
        <p className="text-[#8B9BB4] text-sm tracking-wider uppercase">Authenticating Session...</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
