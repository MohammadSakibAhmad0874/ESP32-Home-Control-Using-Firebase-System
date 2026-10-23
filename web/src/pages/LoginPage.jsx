import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lock, Mail, ArrowRight, Shield, AlertCircle, Home, KeyRound } from 'lucide-react';
import { loginWithEmail } from '../firebase/auth';

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const { role } = await loginWithEmail(email, password);
      if (role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      console.error('Login error:', err);
      let msg = err.message || 'Login failed. Please check your credentials.';
      if (err.code === 'auth/invalid-credential' || err.code === 'auth/user-not-found' || err.code === 'auth/wrong-password') {
        msg = 'Invalid email or password. Please verify and try again.';
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0E14] bg-grid-glow flex flex-col justify-center items-center px-4 py-12">
      
      {/* Brand Header */}
      <Link to="/" className="flex items-center gap-3 mb-8 group">
        <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-[#00D9FF] to-[#FF2E93] p-[1.5px] shadow-[0_0_20px_rgba(0,217,255,0.4)] group-hover:scale-105 transition-transform">
          <div className="w-full h-full bg-[#0B0E14] rounded-[10px] flex items-center justify-center">
            <Home className="w-6 h-6 text-[#00D9FF]" />
          </div>
        </div>
        <div>
          <span className="font-heading font-bold text-2xl text-white">ApnaGhar</span>
          <span className="block text-[11px] text-[#8B9BB4]">Smart Home Authentication</span>
        </div>
      </Link>

      {/* Main Glass Login Card */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="glass-panel p-8 sm:p-10 w-full max-w-md relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#00D9FF] via-[#8B5CF6] to-[#FF2E93]"></div>

        <div className="mb-6">
          <h2 className="font-heading text-2xl font-bold text-white tracking-tight">Welcome Back</h2>
          <p className="text-xs text-[#8B9BB4] mt-1">
            Sign in to access your linked devices or management dashboard.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 flex items-start gap-2.5 text-xs text-red-300">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          
          <div>
            <label className="block text-xs font-semibold text-[#8B9BB4] uppercase tracking-wider mb-2">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-[#58677E] absolute left-3.5 top-3.5" />
              <input 
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="glass-input w-full pl-10 text-sm"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#8B9BB4] uppercase tracking-wider mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-[#58677E] absolute left-3.5 top-3.5" />
              <input 
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="glass-input w-full pl-10 text-sm"
              />
            </div>
          </div>

          <motion.button
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 rounded-xl bg-gradient-to-r from-[#00D9FF] to-[#FF2E93] text-black font-bold text-sm tracking-wide hover:brightness-110 shadow-[0_0_25px_rgba(0,217,255,0.4)] transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <div className="w-5 h-5 rounded-full border-2 border-black border-t-transparent animate-spin"></div>
            ) : (
              <>
                <span>Sign In to Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </motion.button>

        </form>

        <div className="mt-8 pt-6 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-[#8B9BB4]">
          <span>Don't have an account?</span>
          <Link 
            to="/signup" 
            className="font-semibold text-[#00D9FF] hover:underline"
          >
            Create Free Account
          </Link>
        </div>

      </motion.div>

      {/* Security notice */}
      <div className="mt-6 flex items-center gap-2 text-xs text-[#58677E]">
        <Shield className="w-3.5 h-3.5 text-[#00D9FF]" />
        <span>TLS 1.3 Encrypted &bull; RBAC Protected</span>
      </div>

    </div>
  );
}
