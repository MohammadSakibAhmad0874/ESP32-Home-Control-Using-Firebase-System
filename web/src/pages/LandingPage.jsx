import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Zap, ShieldCheck, Wifi, Activity, Cpu, Lock, 
  Smartphone, ArrowRight, CheckCircle2, ChevronRight 
} from 'lucide-react';
import Header from '../components/Header';

export default function LandingPage({ user, role }) {
  return (
    <div className="min-h-screen bg-[#0B0E14] bg-grid-glow flex flex-col selection:bg-[#00D9FF]/20 selection:text-[#00D9FF]">
      <Header user={user} role={role} />

      {/* Hero Section */}
      <main className="flex-1 max-w-7xl mx-auto px-4 lg:px-8 py-12 lg:py-20 flex flex-col justify-center">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          
          {/* Hero Left Content */}
          <motion.div 
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            className="lg:col-span-7 flex flex-col items-start"
          >
            {/* Pill Badge */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/5 border border-white/10 backdrop-blur-md mb-6 shadow-[0_0_20px_rgba(0,217,255,0.15)]">
              <span className="w-2 h-2 rounded-full bg-[#00D9FF] animate-ping"></span>
              <span className="text-xs font-semibold text-[#00D9FF] tracking-wide">
                NEXT-GEN SMART HOME PLATFORM v2.1
              </span>
            </div>

            {/* Title */}
            <h1 className="font-heading text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.1] mb-6">
              Control Your Home <br className="hidden sm:inline" />
              <span className="text-gradient-neon">From Anywhere.</span>
            </h1>

            {/* Subtitle */}
            <p className="text-base sm:text-lg text-[#8B9BB4] max-w-2xl leading-relaxed mb-8">
              Engineered with dual-channel ESP32 firmware, instant Firebase Realtime streaming, 
              and precision electrical relays. Control appliances, monitor energy consumption, 
              and automate schedules with enterprise-grade security.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap items-center gap-4 w-full sm:w-auto">
              {user ? (
                <Link
                  to="/dashboard"
                  className="w-full sm:w-auto flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-gradient-to-r from-[#00D9FF] to-[#FF2E93] text-black font-bold text-sm tracking-wide hover:brightness-110 shadow-[0_0_30px_rgba(0,217,255,0.4)] transition-all"
                >
                  <span>Go to My Dashboard</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              ) : (
                <>
                  <Link
                    to="/signup"
                    className="w-full sm:w-auto flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-gradient-to-r from-[#00D9FF] to-[#FF2E93] text-black font-bold text-sm tracking-wide hover:brightness-110 shadow-[0_0_30px_rgba(0,217,255,0.4)] transition-all"
                  >
                    <span>Get Started Free</span>
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                  <Link
                    to="/login"
                    className="w-full sm:w-auto flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-white/5 hover:bg-white/10 text-white font-semibold text-sm tracking-wide border border-white/15 transition-all"
                  >
                    <span>Sign In</span>
                  </Link>
                </>
              )}
              <a
                href="https://github.com/MohammadSakibAhmad0874/ESP32-Home-Control-Using-Firebase-System"
                target="_blank"
                rel="noreferrer"
                className="w-full sm:w-auto flex items-center justify-center gap-2 px-5 py-3.5 rounded-xl bg-white/5 hover:bg-white/10 text-[#8B9BB4] hover:text-white text-xs font-semibold border border-white/10 transition-colors"
              >
                <span>GitHub Repository</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </a>
            </div>

            {/* Metrics Pills */}
            <div className="grid grid-cols-3 gap-4 sm:gap-6 mt-12 pt-8 border-t border-white/10 w-full max-w-xl">
              <div>
                <div className="font-heading text-2xl font-bold text-white tracking-tight">40ms</div>
                <div className="text-xs text-[#8B9BB4] mt-0.5">Firebase Stream Latency</div>
              </div>
              <div>
                <div className="font-heading text-2xl font-bold text-[#00D9FF] tracking-tight">4 Relays</div>
                <div className="text-xs text-[#8B9BB4] mt-0.5">Optocoupler Isolated</div>
              </div>
              <div>
                <div className="font-heading text-2xl font-bold text-[#FF2E93] tracking-tight">100%</div>
                <div className="text-xs text-[#8B9BB4] mt-0.5">Offline Fallback (AP)</div>
              </div>
            </div>

          </motion.div>

          {/* Hero Right 3D Mockup Display */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1 }}
            className="lg:col-span-5 flex justify-center relative"
          >
            {/* Background Radial Glow */}
            <div className="absolute -inset-4 bg-gradient-to-tr from-[#00D9FF]/20 via-[#FF2E93]/20 to-transparent blur-3xl rounded-full pointer-events-none"></div>

            {/* Floating 3D Device Component */}
            <div className="relative w-full max-w-[480px] floating-mockup">
              <img 
                src="/hero-3d-mockup.png" 
                alt="ApnaGhar 3D Glassmorphism Mobile & Tablet Interface" 
                className="w-full h-auto object-contain rounded-2xl drop-shadow-2xl"
              />

              {/* Live Pill Overlay */}
              <div className="absolute top-4 right-4 glass-card px-3.5 py-1.5 flex items-center gap-2 border border-[#00D9FF]/40 shadow-[0_0_20px_rgba(0,217,255,0.4)]">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span className="text-xs font-bold text-white font-mono tracking-wider">LIVE 3D UI</span>
              </div>
            </div>
          </motion.div>

        </div>

        {/* Feature Cards Grid */}
        <section className="mt-24">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-bold uppercase tracking-widest text-[#00D9FF]">ENGINEERED FOR RESILIENCE</span>
            <h2 className="font-heading text-3xl font-extrabold text-white mt-2">
              Next-Generation IoT Hardware & Security
            </h2>
            <p className="text-sm text-[#8B9BB4] mt-2">
              Every switch, connection, and request is verified with enterprise security and instant synchronization.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            
            {/* Card 1 */}
            <div className="glass-card p-6 flex flex-col">
              <div className="w-12 h-12 rounded-xl bg-[#00D9FF]/10 border border-[#00D9FF]/30 flex items-center justify-center mb-5 text-[#00D9FF] shadow-[0_0_15px_rgba(0,217,255,0.2)]">
                <Zap className="w-6 h-6" />
              </div>
              <h3 className="font-heading text-lg font-bold text-white mb-2">Live Cloud Streaming</h3>
              <p className="text-xs text-[#8B9BB4] leading-relaxed flex-1">
                Zero polling delay. Uses persistent Server-Sent Events (SSE) so light toggles respond in under 50 milliseconds worldwide.
              </p>
              <div className="mt-4 flex items-center gap-1.5 text-xs text-[#00D9FF] font-semibold">
                <span>Direct Firebase RTDB</span>
              </div>
            </div>

            {/* Card 2 */}
            <div className="glass-card p-6 flex flex-col">
              <div className="w-12 h-12 rounded-xl bg-[#FF2E93]/10 border border-[#FF2E93]/30 flex items-center justify-center mb-5 text-[#FF2E93] shadow-[0_0_15px_rgba(255,46,147,0.2)]">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="font-heading text-lg font-bold text-white mb-2">Admin Approval Guard</h3>
              <p className="text-xs text-[#8B9BB4] leading-relaxed flex-1">
                New users cannot access or tamper with hardware without explicit verification. Device claims trigger admin review pipelines.
              </p>
              <div className="mt-4 flex items-center gap-1.5 text-xs text-[#FF2E93] font-semibold">
                <span>Role-Based Auth Guard</span>
              </div>
            </div>

            {/* Card 3 */}
            <div className="glass-card p-6 flex flex-col">
              <div className="w-12 h-12 rounded-xl bg-[#8B5CF6]/10 border border-[#8B5CF6]/30 flex items-center justify-center mb-5 text-[#8B5CF6] shadow-[0_0_15px_rgba(139,92,246,0.2)]">
                <Wifi className="w-6 h-6" />
              </div>
              <h3 className="font-heading text-lg font-bold text-white mb-2">Offline Dual AP Mode</h3>
              <p className="text-xs text-[#8B9BB4] leading-relaxed flex-1">
                Internet down? The ESP32 creates an autonomous local hotspot (<code className="text-[#8B5CF6]">SmartHome_Control</code>) for continuous local control.
              </p>
              <div className="mt-4 flex items-center gap-1.5 text-xs text-[#8B5CF6] font-semibold">
                <span>192.168.4.1 Direct Portal</span>
              </div>
            </div>

            {/* Card 4 */}
            <div className="glass-card p-6 flex flex-col">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mb-5 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                <Activity className="w-6 h-6" />
              </div>
              <h3 className="font-heading text-lg font-bold text-white mb-2">PZEM Power Metering</h3>
              <p className="text-xs text-[#8B9BB4] leading-relaxed flex-1">
                Precision voltage, current, and energy consumption telemetry directly integrated with high-contrast glowing charts.
              </p>
              <div className="mt-4 flex items-center gap-1.5 text-xs text-emerald-400 font-semibold">
                <span>Real-Time kWh Telemetry</span>
              </div>
            </div>

          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-[#0B0E14]/90 py-10 px-4 lg:px-8 mt-20">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6 text-xs text-[#8B9BB4]">
          <div className="flex items-center gap-3">
            <span className="font-heading font-bold text-white">ApnaGhar IoT Platform</span>
            <span>&copy; {new Date().getFullYear()} All rights reserved.</span>
          </div>

          <div className="flex items-center gap-6">
            <Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
            <Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
            <a 
              href="/ApnaGhar-v2.0-release.apk" 
              download 
              className="hover:text-[#00D9FF] transition-colors"
            >
              Download Android APK
            </a>
            <a 
              href="https://github.com/MohammadSakibAhmad0874/ESP32-Home-Control-Using-Firebase-System" 
              target="_blank" 
              rel="noreferrer" 
              className="hover:text-white transition-colors"
            >
              GitHub Source
            </a>
          </div>
        </div>
      </footer>

    </div>
  );
}
