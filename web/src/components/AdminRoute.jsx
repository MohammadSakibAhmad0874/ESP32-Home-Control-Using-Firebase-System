import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { subscribeAuth, getUserRole } from '../firebase/auth';

export default function AdminRoute({ children }) {
  const [isAdmin, setIsAdmin] = useState(undefined);

  useEffect(() => {
    const unsub = subscribeAuth(async (currentUser) => {
      if (!currentUser) {
        setIsAdmin(false);
        return;
      }
      try {
        const role = await getUserRole(currentUser.uid);
        setIsAdmin(role === 'admin');
      } catch (e) {
        setIsAdmin(false);
      }
    });

    return () => unsub();
  }, []);

  if (isAdmin === undefined) {
    return (
      <div className="min-h-screen bg-[#0B0E14] flex flex-col items-center justify-center">
        <div className="w-12 h-12 rounded-full border-2 border-[#FF2E93] border-t-transparent animate-spin mb-4"></div>
        <p className="text-[#8B9BB4] text-sm tracking-wider uppercase">Verifying Admin Credentials...</p>
      </div>
    );
  }

  if (isAdmin === false) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}
