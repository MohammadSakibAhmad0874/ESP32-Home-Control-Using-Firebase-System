import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Lightbulb, Wind, Flame, Fan, Tv, Zap, Shield, Plus, 
  Check, X, Clock, Wifi, AlertTriangle, Cpu, BarChart2,
  Sliders, BatteryCharging, Radio, ChevronRight
} from 'lucide-react';
import { 
  subscribeUserDevices, 
  subscribeUserPending, 
  subscribeDevice, 
  toggleRelayState, 
  requestDeviceAccess 
} from '../firebase/database';
import Header from '../components/Header';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  Cell, AreaChart, Area 
} from 'recharts';

export default function UserDashboard({ user, role }) {
  const [deviceIds, setDeviceIds] = useState([]);
  const [pendingRequests, setPendingRequests] = useState({});
  const [devicesData, setDevicesData] = useState({});
  const [showAddModal, setShowAddModal] = useState(false);
  const [inputDeviceId, setInputDeviceId] = useState('');
  const [modalLoading, setModalLoading] = useState(false);
  const [modalError, setModalError] = useState('');
  const [modalSuccess, setModalSuccess] = useState('');

  // Mock Energy Data matching reference image
  const energyData = [
    { day: 'Mon', kwh: 12.4, color: '#8B5CF6' },
    { day: 'Tue', kwh: 15.8, color: '#A78BFA' },
    { day: 'Wed', kwh: 18.4, color: '#FF2E93' },
    { day: 'Thu', kwh: 22.1, color: '#00D9FF' },
    { day: 'Fri', kwh: 19.3, color: '#00F5FF' },
    { day: 'Sat', kwh: 14.2, color: '#8B5CF6' },
    { day: 'Sun', kwh: 11.5, color: '#6D5DFC' },
  ];

  // Subscribe to user claimed devices
  useEffect(() => {
    if (!user) return;
    const unsubDevices = subscribeUserDevices(user.uid, (ids) => {
      setDeviceIds(ids);
    });

    const unsubPending = subscribeUserPending(user.uid, (pending) => {
      setPendingRequests(pending);
    });

    return () => {
      unsubDevices();
      unsubPending();
    };
  }, [user]);

  // Subscribe to each claimed device's realtime state
  useEffect(() => {
    if (!deviceIds.length) return;
    const unsubscribers = deviceIds.map((id) => {
      return subscribeDevice(id, (data) => {
        setDevicesData((prev) => ({ ...prev, [id]: data }));
      });
    });

    return () => {
      unsubscribers.forEach((unsub) => unsub && unsub());
    };
  }, [deviceIds]);

  const handleToggle = async (deviceId, relayKey, currentState) => {
    try {
      await toggleRelayState(deviceId, relayKey, !currentState);
    } catch (err) {
      console.error('Failed to toggle relay:', err);
    }
  };

  const handleRequestDevice = async (e) => {
    e.preventDefault();
    setModalError('');
    setModalSuccess('');
    setModalLoading(true);

    try {
      await requestDeviceAccess(inputDeviceId, user);
      setModalSuccess(`Request for device "${inputDeviceId.toUpperCase()}" submitted to Admin! Waiting for verification.`);
      setTimeout(() => {
        setShowAddModal(false);
        setInputDeviceId('');
        setModalSuccess('');
      }, 2500);
    } catch (err) {
      setModalError(err.message || 'Failed to submit device request.');
    } finally {
      setModalLoading(false);
    }
  };

  const getRelayIcon = (name = '') => {
    const lower = name.toLowerCase();
    if (lower.includes('fan')) return <Fan className="w-5 h-5" />;
    if (lower.includes('kitchen') || lower.includes('cook')) return <Flame className="w-5 h-5" />;
    if (lower.includes('bed') || lower.includes('lamp')) return <Wind className="w-5 h-5" />;
    return <Lightbulb className="w-5 h-5" />;
  };

  // Helper for dynamic heartbeat
  const isDeviceOnline = (dev) => {
    if (!dev) return false;
    if (dev.online === false) return false;
    if (!dev.lastSeen) return false;
    let ts = dev.lastSeen;
    if (ts > 1000000000000) ts = Math.floor(ts / 1000);
    const nowSec = Math.floor(Date.now() / 1000);
    // Verified online if ping within last 90 seconds
    return ts > 1700000000 && (nowSec - ts < 90);
  };

  return (
    <div className="min-h-screen bg-[#0B0E14] bg-grid-glow flex flex-col selection:bg-[#00D9FF]/20 selection:text-[#00D9FF]">
      <Header user={user} role={role} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-8">
        
        {/* Welcome & Action Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="font-heading text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                Welcome, {user.displayName || user.email.split('@')[0]}
              </h1>
              <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                ACTIVE
              </span>
            </div>
            <p className="text-xs text-[#8B9BB4] mt-1">
              Real-time telemetry, relay switches &amp; power diagnostics
            </p>
          </div>

          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#00D9FF] to-[#FF2E93] text-black font-bold text-xs tracking-wide hover:brightness-110 shadow-[0_0_20px_rgba(0,217,255,0.3)] transition-all"
          >
            <Plus className="w-4 h-4 stroke-[3]" />
            <span>Link New Device ID</span>
          </button>
        </div>

        {/* ── Top Overview Stats Row (Matching Reference Image) ── */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          
          {/* Card 1: Lights */}
          <div className="glass-panel p-5 relative overflow-hidden group">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#8B9BB4]">OVERVIEW</span>
              <div className="w-7 h-7 rounded-lg bg-[#00D9FF]/10 text-[#00D9FF] flex items-center justify-center">
                <Lightbulb className="w-4 h-4" />
              </div>
            </div>
            <div className="font-heading text-2xl font-bold text-white">6 On</div>
            <div className="text-[11px] text-[#8B9BB4] mt-0.5">14 Total Connected</div>
          </div>

          {/* Card 2: Devices Active */}
          <div className="glass-panel p-5 relative overflow-hidden border-[#8B5CF6]/30 shadow-[0_0_20px_rgba(139,92,246,0.15)]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#A78BFA]">DEVICES</span>
              <div className="w-7 h-7 rounded-lg bg-[#8B5CF6]/15 text-[#A78BFA] flex items-center justify-center">
                <Radio className="w-4 h-4" />
              </div>
            </div>
            <div className="font-heading text-2xl font-bold text-white">
              {deviceIds.length > 0 ? `${deviceIds.length} Linked` : '0 Claimed'}
            </div>
            <div className="text-[11px] text-[#A78BFA] mt-0.5">Dual Cloud + AP Sync</div>
          </div>

          {/* Card 3: Security */}
          <div className="glass-panel p-5 relative overflow-hidden border-emerald-500/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400">SECURITY</span>
              <div className="w-7 h-7 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                <Shield className="w-4 h-4" />
              </div>
            </div>
            <div className="font-heading text-2xl font-bold text-white flex items-center gap-2">
              <span>Armed</span>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            </div>
            <div className="text-[11px] text-[#8B9BB4] mt-0.5">TLS 1.3 Active</div>
          </div>

          {/* Card 4: Climate / Telemetry */}
          <div className="glass-panel p-5 relative overflow-hidden border-[#FF2E93]/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#FF2E93]">CLIMATE</span>
              <div className="w-7 h-7 rounded-lg bg-[#FF2E93]/10 text-[#FF2E93] flex items-center justify-center">
                <Zap className="w-4 h-4" />
              </div>
            </div>
            <div className="font-heading text-2xl font-bold text-white">72°F / 22°C</div>
            <div className="text-[11px] text-[#8B9BB4] mt-0.5">Living Room Node</div>
          </div>

        </div>

        {/* ── Pending Device Request Alert Banner ── */}
        {Object.keys(pendingRequests).length > 0 && (
          <div className="mb-8 p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 backdrop-blur-xl flex items-center justify-between gap-4 shadow-[0_0_20px_rgba(245,158,11,0.15)]">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
                <Clock className="w-5 h-5 animate-pulse" />
              </div>
              <div>
                <div className="text-xs font-bold text-white tracking-wide">
                  DEVICE CLAIM PENDING VERIFICATION
                </div>
                <div className="text-[11px] text-amber-300/80 mt-0.5">
                  You requested access for: <code className="font-mono font-bold text-amber-300">{Object.keys(pendingRequests).join(', ')}</code>. 
                  Waiting for administrator review.
                </div>
              </div>
            </div>
            <span className="text-[10px] font-bold uppercase px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 shrink-0">
              In Review
            </span>
          </div>
        )}

        {/* ── Main Content Grid: Devices + Energy Chart ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left: Device Controls (8 Cols) */}
          <div className="lg:col-span-8 space-y-6">
            
            <div className="flex items-center justify-between">
              <h2 className="font-heading text-lg font-bold text-white tracking-tight flex items-center gap-2">
                <span>My Hardware Nodes</span>
                <span className="text-xs font-normal text-[#8B9BB4]">({deviceIds.length})</span>
              </h2>
            </div>

            {deviceIds.length === 0 ? (
              /* Empty State when no devices are claimed */
              <div className="glass-panel p-10 text-center flex flex-col items-center justify-center relative overflow-hidden">
                <div className="w-16 h-16 rounded-2xl bg-[#00D9FF]/10 border border-[#00D9FF]/20 flex items-center justify-center text-[#00D9FF] mb-4 shadow-[0_0_30px_rgba(0,217,255,0.2)]">
                  <Cpu className="w-8 h-8" />
                </div>
                <h3 className="font-heading text-xl font-bold text-white mb-2">No Devices Linked Yet</h3>
                <p className="text-xs text-[#8B9BB4] max-w-md leading-relaxed mb-6">
                  To control appliances, click the button below and enter your ESP32 
                  Device ID (e.g., <code className="text-[#00D9FF] font-mono font-bold">SAKIB7860</code>). 
                  Your request will be submitted to the administrator for verification.
                </p>
                <button
                  onClick={() => setShowAddModal(true)}
                  className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-[#00D9FF] to-[#FF2E93] text-black font-bold text-xs tracking-wide hover:brightness-110 shadow-[0_0_20px_rgba(0,217,255,0.4)] transition-all"
                >
                  <Plus className="w-4 h-4 stroke-[3]" />
                  <span>Enter Device ID (e.g. SAKIB7860)</span>
                </button>
              </div>
            ) : (
              /* Display Claimed Devices and Relay Cards */
              deviceIds.map((deviceId) => {
                const dev = devicesData[deviceId] || {};
                const online = isDeviceOnline(dev);
                const relays = dev.relays || {
                  relay1: { name: 'Living Room', state: false },
                  relay2: { name: 'Bedroom', state: false },
                  relay3: { name: 'Kitchen', state: false },
                  relay4: { name: 'Fan', state: false }
                };

                return (
                  <div key={deviceId} className="glass-panel p-6 relative overflow-hidden">
                    
                    {/* Device Node Header */}
                    <div className="flex flex-wrap items-center justify-between gap-3 pb-5 border-b border-white/10 mb-6">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-[#00D9FF]">
                          <Cpu className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-heading font-bold text-lg text-white font-mono">{deviceId}</span>
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1.5 ${
                              online 
                                ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' 
                                : 'bg-red-500/15 text-red-400 border border-red-500/30'
                            }`}>
                              <span className={`w-1.5 h-1.5 rounded-full ${online ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`}></span>
                              <span>{online ? 'ONLINE' : 'OFFLINE'}</span>
                            </span>
                          </div>
                          <p className="text-[11px] text-[#8B9BB4] mt-0.5">
                            IP: {online ? (dev.ip || '192.168.1.100') : '—'} &bull; 
                            Owner: {dev.claimedBy || user.email}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 text-xs text-[#8B9BB4] bg-white/5 px-3 py-1.5 rounded-lg border border-white/10">
                        <BatteryCharging className="w-3.5 h-3.5 text-emerald-400" />
                        <span>230V Mains Normal</span>
                      </div>
                    </div>

                    {/* 4 Relays Grid (Matching Reference Image Style) */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {Object.entries(relays).map(([relayKey, r], idx) => {
                        const isStateOn = !!r.state;
                        const isMagentaTheme = idx % 2 === 1;

                        return (
                          <div
                            key={relayKey}
                            className={`glass-card p-5 flex items-center justify-between border transition-all ${
                              isStateOn 
                                ? (isMagentaTheme ? 'border-[#FF2E93]/40 bg-[#FF2E93]/10 shadow-[0_0_20px_rgba(255,46,147,0.2)]' : 'border-[#00D9FF]/40 bg-[#00D9FF]/10 shadow-[0_0_20px_rgba(0,217,255,0.2)]')
                                : 'border-white/10 bg-white/5'
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <div className={`w-10 h-10 rounded-xl flex items-center justify-center transition-colors ${
                                isStateOn 
                                  ? (isMagentaTheme ? 'bg-[#FF2E93] text-black' : 'bg-[#00D9FF] text-black shadow-[0_0_15px_rgba(0,217,255,0.5)]') 
                                  : 'bg-white/5 text-[#8B9BB4]'
                              }`}>
                                {getRelayIcon(r.name)}
                              </div>
                              <div>
                                <div className="font-heading font-bold text-sm text-white">{r.name || `Switch ${idx + 1}`}</div>
                                <div className="text-[11px] font-mono text-[#8B9BB4] mt-0.5">
                                  {isStateOn ? (
                                    <span className={isMagentaTheme ? 'text-[#FF2E93] font-bold' : 'text-[#00D9FF] font-bold'}>
                                      ACTIVE &bull; 60W
                                    </span>
                                  ) : (
                                    <span>STANDBY &bull; 0W</span>
                                  )}
                                </div>
                              </div>
                            </div>

                            {/* 3D Glowing Pill Toggle */}
                            <button
                              onClick={() => handleToggle(deviceId, relayKey, isStateOn)}
                              className={`w-14 h-8 rounded-full p-1 transition-all relative ${
                                isStateOn 
                                  ? (isMagentaTheme ? 'neon-toggle-magenta-on' : 'neon-toggle-on') 
                                  : 'bg-[#1E2536] border border-white/15'
                              }`}
                            >
                              <motion.div
                                layout
                                transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                                className={`w-6 h-6 rounded-full shadow-md ${
                                  isStateOn ? 'bg-black ml-auto' : 'bg-[#58677E] mr-auto'
                                }`}
                              />
                            </button>
                          </div>
                        );
                      })}
                    </div>

                  </div>
                );
              })
            )}

          </div>

          {/* Right: Energy Consumption & Quick Telemetry (4 Cols) */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* Daily Consumption Card (Matching Reference Image) */}
            <div className="glass-panel p-6 relative overflow-hidden">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#8B9BB4]">
                    ENERGY USAGE (kWh)
                  </span>
                  <div className="font-heading text-2xl font-bold text-white mt-1">18.4 kWh</div>
                </div>
                <div className="w-8 h-8 rounded-xl bg-[#FF2E93]/15 text-[#FF2E93] flex items-center justify-center">
                  <BarChart2 className="w-4 h-4" />
                </div>
              </div>

              {/* Bar Chart */}
              <div className="h-48 w-full mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={energyData}>
                    <XAxis 
                      dataKey="day" 
                      stroke="#58677E" 
                      fontSize={11} 
                      tickLine={false} 
                      axisLine={false} 
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1A1F2E', 
                        borderColor: 'rgba(255,255,255,0.15)',
                        borderRadius: '12px',
                        fontSize: '12px',
                        color: '#fff'
                      }} 
                    />
                    <Bar dataKey="kwh" radius={[6, 6, 0, 0]}>
                      {energyData.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={index === 2 ? '#FF2E93' : (index === 3 || index === 4 ? '#00D9FF' : '#6D5DFC')} 
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="mt-4 pt-4 border-t border-white/10 flex items-center justify-between text-xs text-[#8B9BB4]">
                <span>Weekly Average: 16.2 kWh</span>
                <span className="text-emerald-400 font-semibold">-8% vs last week</span>
              </div>
            </div>

            {/* Hardware Diagnostics Card */}
            <div className="glass-panel p-6">
              <h3 className="font-heading text-sm font-bold text-white mb-4 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-[#00D9FF]" />
                <span>ESP32 Hardware Diagnostics</span>
              </h3>

              <div className="space-y-3 text-xs">
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-white/5 border border-white/5">
                  <span className="text-[#8B9BB4]">Firmware Core:</span>
                  <span className="font-mono text-white">v2.1 FreeRTOS</span>
                </div>
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-white/5 border border-white/5">
                  <span className="text-[#8B9BB4]">Stream Protocol:</span>
                  <span className="font-mono text-[#00D9FF]">Firebase SSE</span>
                </div>
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-white/5 border border-white/5">
                  <span className="text-[#8B9BB4]">Watchdog Timer (WDT):</span>
                  <span className="text-emerald-400 font-bold">Enabled (8s)</span>
                </div>
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-white/5 border border-white/5">
                  <span className="text-[#8B9BB4]">Hardware Snubber:</span>
                  <span className="text-emerald-400 font-bold">RC Filter Active</span>
                </div>
              </div>
            </div>

          </div>

        </div>

      </main>

      {/* ── Link Device ID Modal ── */}
      <AnimatePresence>
        {showAddModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="glass-panel p-6 sm:p-8 w-full max-w-md relative overflow-hidden"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-xl bg-[#00D9FF]/10 text-[#00D9FF] flex items-center justify-center">
                    <Plus className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-heading text-lg font-bold text-white">Link Device ID</h3>
                    <p className="text-[11px] text-[#8B9BB4]">Enter the ID from your controller packaging</p>
                  </div>
                </div>

                <button
                  onClick={() => setShowAddModal(false)}
                  className="w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 text-[#8B9BB4] flex items-center justify-center"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {modalError && (
                <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-300 flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                  <span>{modalError}</span>
                </div>
              )}

              {modalSuccess && (
                <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-300 flex items-start gap-2">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span>{modalSuccess}</span>
                </div>
              )}

              <form onSubmit={handleRequestDevice} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-[#8B9BB4] uppercase tracking-wider mb-2">
                    Device Identifier (e.g. SAKIB7860 or SH-001)
                  </label>
                  <input
                    type="text"
                    required
                    value={inputDeviceId}
                    onChange={(e) => setInputDeviceId(e.target.value.toUpperCase())}
                    placeholder="SAKIB7860"
                    className="glass-input w-full font-mono text-center tracking-widest text-lg font-bold text-[#00D9FF]"
                  />
                </div>

                <div className="text-[11px] text-[#8B9BB4] bg-white/5 p-3 rounded-xl border border-white/5 leading-relaxed">
                  🛡️ <strong>Security Verification:</strong> Submitting a device ID sends an authorization request to the ApnaGhar Administrator. Once approved, all 4 switch controls will immediately appear on your dashboard.
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="w-1/2 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-[#8B9BB4] text-xs font-semibold border border-white/10"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={modalLoading}
                    className="w-1/2 py-2.5 rounded-xl bg-gradient-to-r from-[#00D9FF] to-[#FF2E93] text-black font-bold text-xs tracking-wide hover:brightness-110 shadow-[0_0_20px_rgba(0,217,255,0.4)] disabled:opacity-50"
                  >
                    {modalLoading ? 'Submitting...' : 'Submit Request'}
                  </button>
                </div>
              </form>

            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
}
