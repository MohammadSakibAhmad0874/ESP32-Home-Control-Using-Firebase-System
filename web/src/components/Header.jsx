import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Home, Shield, LogOut, Cpu, LayoutDashboard, ExternalLink } from 'lucide-react';
import { logoutUser } from '../firebase/auth';

export default function Header({ user, role }) {
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logoutUser();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-50 backdrop-blur-xl bg-[#0B0E14]/80 border-b border-white/10 px-4 lg:px-8 py-3.5 transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#00D9FF] to-[#FF2E93] p-[1.5px] transition-transform group-hover:scale-105 shadow-[0_0_20px_rgba(0,217,255,0.3)]">
            <div className="w-full h-full bg-[#0B0E14] rounded-[10px] flex items-center justify-center">
              <Home className="w-5 h-5 text-[#00D9FF]" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-heading font-bold text-xl tracking-tight text-white group-hover:text-[#00D9FF] transition-colors">
                ApnaGhar
              </span>
              <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-[#00D9FF]/10 text-[#00D9FF] border border-[#00D9FF]/20">
                v2.1 IoT
              </span>
            </div>
            <p className="text-[11px] text-[#8B9BB4] hidden sm:block">Smart Home, Your Way</p>
          </div>
        </Link>

        {/* Navigation & User Actions */}
        <div className="flex items-center gap-3 sm:gap-4">
          {user ? (
            <>
              <Link 
                to="/dashboard"
                className="flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-[#DDE3E8] border border-white/10 transition-colors"
              >
                <LayoutDashboard className="w-4 h-4 text-[#00D9FF]" />
                <span className="hidden sm:inline">User Dashboard</span>
              </Link>

              {role === 'admin' && (
                <Link 
                  to="/admin"
                  className="flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-lg bg-[#FF2E93]/15 hover:bg-[#FF2E93]/25 text-[#FF2E93] border border-[#FF2E93]/30 transition-colors shadow-[0_0_15px_rgba(255,46,147,0.2)]"
                >
                  <Shield className="w-4 h-4" />
                  <span>Admin Panel</span>
                </Link>
              )}

              {/* User Identity Chip */}
              <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span className="text-[#8B9BB4] font-mono truncate max-w-[150px]">{user.email}</span>
                {role === 'admin' && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#FF2E93]/20 text-[#FF2E93] font-bold">
                    ADMIN
                  </span>
                )}
              </div>

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 transition-all hover:border-red-500/40"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </>
          ) : (
            <>
              <a 
                href="/ApnaGhar-v2.0-release.apk" 
                download
                className="hidden md:flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 transition-all"
              >
                <Cpu className="w-3.5 h-3.5" />
                <span>APK v2.1</span>
              </a>

              <Link 
                to="/login"
                className="text-xs font-semibold px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-white border border-white/15 transition-all"
              >
                Sign In
              </Link>

              <Link 
                to="/signup"
                className="text-xs font-semibold px-4 py-2 rounded-xl bg-gradient-to-r from-[#00D9FF] to-[#FF2E93] text-black font-bold hover:brightness-110 shadow-[0_0_20px_rgba(0,217,255,0.4)] transition-all"
              >
                Create Account
              </Link>
            </>
          )}
        </div>

      </div>
    </header>
  );
}
