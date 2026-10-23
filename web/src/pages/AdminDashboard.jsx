import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, Check, X, Clock, Cpu, Users, Search, 
  Trash2, Plus, AlertCircle, RefreshCw, KeyRound, 
  ExternalLink, CheckCircle, Wifi, Lightbulb
} from 'lucide-react';
import { 
  subscribeAllPendingRequests, 
  approveDeviceRequest, 
  rejectDeviceRequest,
  subscribeAllDevices,
  subscribeAllUsers,
  updateUserRole,
  toggleRelayState
} from '../firebase/database';
import { ref, set, remove, get } from 'firebase/database';
import { db } from '../firebase/firebase-config';
import Header from '../components/Header';

export default function AdminDashboard({ user, role }) {
  const [activeTab, setActiveTab] = useState('pending'); // 'pending' | 'devices' | 'users'
  const [pendingRequests, setPendingRequests] = useState([]);
  const [devices, setDevices] = useState([]);
  const [users, setUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [notification, setNotification] = useState({ type: '', text: '' });

  // New device seeding state
  const [newDeviceId, setNewDeviceId] = useState('');
  const [newDeviceName, setNewDeviceName] = useState('Living Room');
  const [isSeeding, setIsSeeding] = useState(false);

  useEffect(() => {
    const unsubPending = subscribeAllPendingRequests((list) => {
      setPendingRequests(list);
    });

    const unsubDevices = subscribeAllDevices((list) => {
      setDevices(list);
    });

    const unsubUsers = subscribeAllUsers((list) => {
      setUsers(list);
    });

    return () => {
      unsubPending();
      unsubDevices();
      unsubUsers();
    };
  }, []);

  const showNotification = (type, text) => {
    setNotification({ type, text });
    setTimeout(() => setNotification({ type: '', text: '' }), 4000);
  };

  const handleApprove = async (request) => {
    setActionLoading(true);
    try {
      await approveDeviceRequest(request, user.uid);
      showNotification('success', `Approved device "${request.deviceId}" for ${request.userEmail}!`);
    } catch (err) {
      showNotification('error', `Failed to approve: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async (request) => {
    if (!window.confirm(`Reject claim request for ${request.deviceId}?`)) return;
    setActionLoading(true);
    try {
      await rejectDeviceRequest(request);
      showNotification('success', `Rejected claim request for ${request.deviceId}.`);
    } catch (err) {
      showNotification('error', `Failed to reject: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleMakeAdmin = async (targetUser) => {
    if (!window.confirm(`Promote "${targetUser.email}" to Administrator?`)) return;
    try {
      await updateUserRole(targetUser.uid, 'admin');
      showNotification('success', `User ${targetUser.email} is now an Administrator.`);
    } catch (err) {
      showNotification('error', err.message);
    }
  };

  const handleSeedDevice = async (e) => {
    e.preventDefault();
    const id = (newDeviceId || '').trim().toUpperCase();
    if (!id) return;

    setIsSeeding(true);
    try {
      await set(ref(db, `devices/${id}`), {
        deviceId: id,
        ownerName: newDeviceName,
        online: false,
        lastSeen: 0,
        ip: '—',
        numSwitches: 4,
        relays: {
          relay1: { name: `${newDeviceName} Light 1`, state: false },
          relay2: { name: `${newDeviceName} Light 2`, state: false },
          relay3: { name: `${newDeviceName} Socket`, state: false },
          relay4: { name: `${newDeviceName} Fan`, state: false }
        }
      });
      showNotification('success', `Pre-registered Device "${id}" successfully!`);
      setNewDeviceId('');
    } catch (err) {
      showNotification('error', err.message);
    } finally {
      setIsSeeding(false);
    }
  };

  const handleDeleteDevice = async (deviceId) => {
    if (!window.confirm(`Delete device "${deviceId}" completely from Firebase?`)) return;
    try {
      await remove(ref(db, `devices/${deviceId}`));
      showNotification('success', `Device ${deviceId} removed.`);
    } catch (err) {
      showNotification('error', err.message);
    }
  };

  const isDeviceOnline = (dev) => {
    if (!dev) return false;
    if (dev.online === false) return false;
    if (!dev.lastSeen) return false;
    let ts = dev.lastSeen;
    if (ts > 1000000000000) ts = Math.floor(ts / 1000);
    const nowSec = Math.floor(Date.now() / 1000);
    return ts > 1700000000 && (nowSec - ts < 90);
  };

  const formatTimeAgo = (ts) => {
    if (!ts) return 'Just now';
    const diff = Math.floor((Date.now() - ts) / 1000);
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  return (
    <div className="min-h-screen bg-[#0B0E14] bg-grid-glow flex flex-col selection:bg-[#00D9FF]/20 selection:text-[#00D9FF]">
      <Header user={user} role={role} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-8">
        
        {/* Admin Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-[#FF2E93]/20 text-[#FF2E93] flex items-center justify-center">
                <Shield className="w-5 h-5" />
              </div>
              <h1 className="font-heading text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                Administrator Control Center
              </h1>
              <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-[#FF2E93]/15 text-[#FF2E93] border border-[#FF2E93]/30">
                ADMIN ACCESS
              </span>
            </div>
            <p className="text-xs text-[#8B9BB4] mt-1">
              Verify device authorization requests, inspect live hardware, and manage users.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs text-[#8B9BB4] font-mono hidden md:inline">
              Firebase: <span className="text-[#00D9FF]">apnaghar-3f865</span>
            </span>
          </div>
        </div>

        {/* Global Alert Notification */}
        {notification.text && (
          <div className={`mb-6 p-4 rounded-xl flex items-center justify-between text-xs font-semibold backdrop-blur-xl ${
            notification.type === 'success' 
              ? 'bg-emerald-500/15 border border-emerald-500/30 text-emerald-300' 
              : 'bg-red-500/15 border border-red-500/30 text-red-300'
          }`}>
            <span>{notification.text}</span>
            <button onClick={() => setNotification({ type: '', text: '' })}>
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Tab Selector */}
        <div className="flex items-center gap-2 p-1.5 rounded-2xl bg-white/5 border border-white/10 w-fit mb-8">
          <button
            onClick={() => setActiveTab('pending')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold transition-all relative ${
              activeTab === 'pending'
                ? 'bg-[#FF2E93] text-black shadow-[0_0_20px_rgba(255,46,147,0.4)]'
                : 'text-[#8B9BB4] hover:text-white'
            }`}
          >
            <Clock className="w-4 h-4" />
            <span>Pending Requests</span>
            {pendingRequests.length > 0 && (
              <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                activeTab === 'pending' ? 'bg-black text-[#FF2E93]' : 'bg-[#FF2E93] text-black'
              }`}>
                {pendingRequests.length}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('devices')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold transition-all relative ${
              activeTab === 'devices'
                ? 'bg-[#00D9FF] text-black shadow-[0_0_20px_rgba(0,217,255,0.4)]'
                : 'text-[#8B9BB4] hover:text-white'
            }`}
          >
            <Cpu className="w-4 h-4" />
            <span>Hardware Devices ({devices.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('users')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold transition-all relative ${
              activeTab === 'users'
                ? 'bg-emerald-400 text-black shadow-[0_0_20px_rgba(52,211,153,0.4)]'
                : 'text-[#8B9BB4] hover:text-white'
            }`}
          >
            <Users className="w-4 h-4" />
            <span>Registered Users ({users.length})</span>
          </button>
        </div>

        {/* ── TAB 1: PENDING REQUESTS ── */}
        {activeTab === 'pending' && (
          <div className="glass-panel p-6 sm:p-8">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-white/10">
              <div>
                <h2 className="font-heading text-lg font-bold text-white tracking-tight">
                  Authorization Queue
                </h2>
                <p className="text-xs text-[#8B9BB4] mt-0.5">
                  Approve or reject users requesting hardware switch access.
                </p>
              </div>

              <div className="text-xs text-[#8B9BB4]">
                Total Pending: <strong className="text-[#FF2E93]">{pendingRequests.length}</strong>
              </div>
            </div>

            {pendingRequests.length === 0 ? (
              <div className="py-16 text-center">
                <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto mb-3 shadow-[0_0_20px_rgba(16,185,129,0.2)]">
                  <CheckCircle className="w-7 h-7" />
                </div>
                <h3 className="font-heading text-lg font-bold text-white">All Caught Up!</h3>
                <p className="text-xs text-[#8B9BB4] mt-1">There are no pending device claim requests at this time.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-white/10 text-[#8B9BB4] uppercase tracking-wider font-semibold">
                      <th className="pb-3 px-3">User Details</th>
                      <th className="pb-3 px-3">Device ID</th>
                      <th className="pb-3 px-3">Requested At</th>
                      <th className="pb-3 px-3 text-right">Verification Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {pendingRequests.map((req) => (
                      <tr key={req.id} className="hover:bg-white/5 transition-colors">
                        <td className="py-4 px-3">
                          <div className="font-bold text-white">{req.userName || 'User'}</div>
                          <div className="text-[11px] text-[#8B9BB4] font-mono mt-0.5">{req.userEmail}</div>
                        </td>
                        <td className="py-4 px-3">
                          <span className="font-mono font-bold text-[#00D9FF] bg-[#00D9FF]/10 px-2.5 py-1 rounded-lg border border-[#00D9FF]/20 text-xs">
                            {req.deviceId}
                          </span>
                        </td>
                        <td className="py-4 px-3 text-[#8B9BB4]">
                          {formatTimeAgo(req.timestamp)}
                        </td>
                        <td className="py-4 px-3 text-right">
                          <div className="inline-flex items-center gap-2">
                            <button
                              disabled={actionLoading}
                              onClick={() => handleApprove(req)}
                              className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/30 font-bold flex items-center gap-1.5 transition-all shadow-[0_0_15px_rgba(16,185,129,0.2)]"
                            >
                              <Check className="w-3.5 h-3.5 stroke-[3]" />
                              <span>Approve</span>
                            </button>
                            <button
                              disabled={actionLoading}
                              onClick={() => handleReject(req)}
                              className="px-3 py-1.5 rounded-lg bg-red-500/15 hover:bg-red-500/25 text-red-400 border border-red-500/30 font-semibold flex items-center gap-1.5 transition-all"
                            >
                              <X className="w-3.5 h-3.5" />
                              <span>Reject</span>
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* ── TAB 2: HARDWARE DEVICES ── */}
        {activeTab === 'devices' && (
          <div className="space-y-8">
            
            {/* Pre-Register / Seed Device Form */}
            <div className="glass-panel p-6">
              <h3 className="font-heading text-sm font-bold text-white mb-2 flex items-center gap-2">
                <Plus className="w-4 h-4 text-[#00D9FF]" />
                <span>Pre-Register New Hardware Node in Firebase</span>
              </h3>
              <p className="text-xs text-[#8B9BB4] mb-4">
                Define a new Device ID (e.g., <code className="text-[#00D9FF]">SAKIB7860</code>) so users can link it.
              </p>

              <form onSubmit={handleSeedDevice} className="flex flex-wrap items-center gap-3">
                <input
                  type="text"
                  required
                  value={newDeviceId}
                  onChange={(e) => setNewDeviceId(e.target.value.toUpperCase())}
                  placeholder="DEVICE_ID (e.g. SAKIB7860)"
                  className="glass-input text-xs font-mono font-bold tracking-wider w-full sm:w-64"
                />
                <input
                  type="text"
                  required
                  value={newDeviceName}
                  onChange={(e) => setNewDeviceName(e.target.value)}
                  placeholder="Label (e.g. Master Bedroom)"
                  className="glass-input text-xs w-full sm:w-64"
                />
                <button
                  type="submit"
                  disabled={isSeeding}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#00D9FF] to-[#FF2E93] text-black font-bold text-xs hover:brightness-110 shadow-[0_0_20px_rgba(0,217,255,0.3)] disabled:opacity-50"
                >
                  {isSeeding ? 'Registering...' : '+ Add Device Node'}
                </button>
              </form>
            </div>

            {/* Devices Table */}
            <div className="glass-panel p-6 sm:p-8">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-white/10">
                <div>
                  <h2 className="font-heading text-lg font-bold text-white tracking-tight">
                    All Physical Nodes in Realtime DB
                  </h2>
                  <p className="text-xs text-[#8B9BB4] mt-0.5">
                    Live telemetry status and quick management.
                  </p>
                </div>
              </div>

              {devices.length === 0 ? (
                <div className="py-12 text-center text-xs text-[#8B9BB4]">
                  No devices found in Firebase. Register one above.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-white/10 text-[#8B9BB4] uppercase tracking-wider font-semibold">
                        <th className="pb-3 px-3">Device ID</th>
                        <th className="pb-3 px-3">Telemetry Status</th>
                        <th className="pb-3 px-3">Owner / Claimed By</th>
                        <th className="pb-3 px-3">IP Address</th>
                        <th className="pb-3 px-3">Relays</th>
                        <th className="pb-3 px-3 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {devices.map((dev) => {
                        const online = isDeviceOnline(dev);
                        const relayCount = Object.keys(dev.relays || {}).length || 4;

                        return (
                          <tr key={dev.deviceId} className="hover:bg-white/5 transition-colors">
                            <td className="py-4 px-3">
                              <span className="font-mono font-bold text-white text-sm">
                                {dev.deviceId}
                              </span>
                              <div className="text-[11px] text-[#8B9BB4] mt-0.5">{dev.ownerName || 'Smart Node'}</div>
                            </td>
                            <td className="py-4 px-3">
                              <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold ${
                                online 
                                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' 
                                  : 'bg-red-500/15 text-red-400 border border-red-500/30'
                              }`}>
                                <span className={`w-1.5 h-1.5 rounded-full ${online ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`}></span>
                                <span>{online ? 'ONLINE' : 'OFFLINE'}</span>
                              </span>
                            </td>
                            <td className="py-4 px-3 text-[#8B9BB4]">
                              {dev.claimedBy ? (
                                <span className="text-white font-semibold font-mono">{dev.claimedBy}</span>
                              ) : (
                                <span className="text-amber-400 font-mono">Unclaimed</span>
                              )}
                            </td>
                            <td className="py-4 px-3 font-mono text-[#8B9BB4]">
                              {online ? (dev.ip || '192.168.1.100') : '—'}
                            </td>
                            <td className="py-4 px-3 text-[#8B9BB4]">
                              {relayCount} Switches
                            </td>
                            <td className="py-4 px-3 text-right">
                              <button
                                onClick={() => handleDeleteDevice(dev.deviceId)}
                                className="p-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors"
                                title="Delete Device Node"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

          </div>
        )}

        {/* ── TAB 3: REGISTERED USERS ── */}
        {activeTab === 'users' && (
          <div className="glass-panel p-6 sm:p-8">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-white/10">
              <div>
                <h2 className="font-heading text-lg font-bold text-white tracking-tight">
                  User Directory &amp; RBAC Roles
                </h2>
                <p className="text-xs text-[#8B9BB4] mt-0.5">
                  Manage user profiles and elevate accounts to Administrator.
                </p>
              </div>

              <div className="text-xs text-[#8B9BB4]">
                Total Users: <strong className="text-white">{users.length}</strong>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-white/10 text-[#8B9BB4] uppercase tracking-wider font-semibold">
                    <th className="pb-3 px-3">User Profile</th>
                    <th className="pb-3 px-3">Role</th>
                    <th className="pb-3 px-3">Claimed Devices</th>
                    <th className="pb-3 px-3">Registered Date</th>
                    <th className="pb-3 px-3 text-right">Role Elevation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {users.map((u) => {
                    const isAdmin = u.role === 'admin';
                    const devCount = Object.keys(u.devices || {}).length;

                    return (
                      <tr key={u.uid} className="hover:bg-white/5 transition-colors">
                        <td className="py-4 px-3">
                          <div className="font-bold text-white">{u.name || 'User'}</div>
                          <div className="text-[11px] text-[#8B9BB4] font-mono mt-0.5">{u.email}</div>
                        </td>
                        <td className="py-4 px-3">
                          <span className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                            isAdmin 
                              ? 'bg-[#FF2E93]/20 text-[#FF2E93] border border-[#FF2E93]/30' 
                              : 'bg-[#00D9FF]/15 text-[#00D9FF] border border-[#00D9FF]/30'
                          }`}>
                            {u.role || 'user'}
                          </span>
                        </td>
                        <td className="py-4 px-3 text-[#8B9BB4]">
                          {devCount > 0 ? (
                            <span className="font-mono text-white font-bold">{devCount} node(s)</span>
                          ) : (
                            <span>None</span>
                          )}
                        </td>
                        <td className="py-4 px-3 text-[#8B9BB4]">
                          {u.createdAt ? new Date(u.createdAt).toLocaleDateString() : '—'}
                        </td>
                        <td className="py-4 px-3 text-right">
                          {!isAdmin && (
                            <button
                              onClick={() => handleMakeAdmin(u)}
                              className="px-3 py-1.5 rounded-lg bg-purple-500/15 hover:bg-purple-500/25 text-purple-300 border border-purple-500/30 text-[11px] font-bold transition-all"
                            >
                              👑 Make Admin
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

      </main>

    </div>
  );
}
