import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/theme.dart';
import '../models/device.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'login_screen.dart';

class AdminScreen extends StatefulWidget {
  const AdminScreen({super.key});

  @override
  State<AdminScreen> createState() => _AdminScreenState();
}

class _AdminScreenState extends State<AdminScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabs;
  List<Map<String, dynamic>> _devices = [];
  List<Map<String, dynamic>> _preReg = [];
  bool _loading = true;
  String? _error;
  final _searchCtrl = TextEditingController();

  // Seed form
  final _seedIdCtrl = TextEditingController();
  final _seedLabelCtrl = TextEditingController();
  int _seedSwitches = 4;

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 2, vsync: this);
    _load();
  }

  @override
  void dispose() {
    _tabs.dispose();
    _searchCtrl.dispose();
    _seedIdCtrl.dispose();
    _seedLabelCtrl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final devices = await ApiService.adminGetDevices();
      final preReg = await ApiService.adminGetPreRegistered();
      setState(() {
        _devices = devices.cast<Map<String, dynamic>>();
        _preReg = preReg.cast<Map<String, dynamic>>();
      });
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _adminToggle(String deviceId, String relayKey, bool newState) async {
    try {
      await ApiService.toggleRelay(deviceId, relayKey, newState);
      setState(() {
        final d = _devices.firstWhere((d) => d['device_id'] == deviceId);
        d['relays'][relayKey]['state'] = newState;
      });
    } on ApiException catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.message), backgroundColor: AppTheme.red));
    }
  }

  Future<void> _deleteDevice(String deviceId) async {
    final ok = await showDialog<bool>(context: context, builder: (_) => AlertDialog(
      backgroundColor: AppTheme.card,
      title: const Text('Delete Device?', style: TextStyle(color: AppTheme.textPrimary)),
      content: Text('Remove all data for $deviceId?',
          style: const TextStyle(color: AppTheme.textSecondary)),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel', style: TextStyle(color: AppTheme.textSecondary))),
        TextButton(onPressed: () => Navigator.pop(context, true),
            child: const Text('Delete', style: TextStyle(color: AppTheme.red))),
      ],
    ));
    if (ok != true) return;
    try {
      await ApiService.adminDeleteDevice(deviceId);
      setState(() => _devices.removeWhere((d) => d['device_id'] == deviceId));
    } on ApiException catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.message), backgroundColor: AppTheme.red));
    }
  }

  Future<void> _seedDevice() async {
    final id = _seedIdCtrl.text.trim().toUpperCase();
    if (id.isEmpty) return;
    try {
      await ApiService.adminSeedDevice(id, _seedLabelCtrl.text.trim(), _seedSwitches);
      _seedIdCtrl.clear();
      _seedLabelCtrl.clear();
      await _load();
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('✅ $id registered successfully!'),
              backgroundColor: AppTheme.green));
    } on ApiException catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.message), backgroundColor: AppTheme.red));
    }
  }

  void _logout() async {
    await AuthService.logout();
    if (!mounted) return;
    Navigator.pushReplacement(context,
        MaterialPageRoute(builder: (_) => const LoginScreen()));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(children: [
          const Text('🏠 ', style: TextStyle(fontSize: 20)),
          const Text('Admin Panel'),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: AppTheme.accent.withOpacity(0.2),
              borderRadius: BorderRadius.circular(4),
              border: Border.all(color: AppTheme.accent.withOpacity(0.35)),
            ),
            child: Text('ADMIN', style: GoogleFonts.outfit(
                fontSize: 10, fontWeight: FontWeight.w700,
                color: AppTheme.accentLight, letterSpacing: 1)),
          ),
        ]),
        actions: [
          IconButton(onPressed: _load, icon: const Icon(Icons.refresh_rounded)),
          IconButton(onPressed: _logout, icon: const Icon(Icons.logout_rounded)),
        ],
        bottom: TabBar(
          controller: _tabs,
          labelColor: AppTheme.accentLight,
          unselectedLabelColor: AppTheme.textSecondary,
          indicatorColor: AppTheme.accent,
          tabs: [
            Tab(text: 'Devices (${_devices.length})'),
            Tab(text: 'Pre-Registered (${_preReg.length})'),
          ],
        ),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.accent))
          : _error != null
              ? Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                  const Icon(Icons.lock_outline_rounded, color: AppTheme.red, size: 48),
                  const SizedBox(height: 16),
                  Text(_error!, style: const TextStyle(color: AppTheme.textSecondary),
                      textAlign: TextAlign.center),
                  const SizedBox(height: 24),
                  ElevatedButton(onPressed: _load, child: const Text('Retry')),
                ]))
              : TabBarView(
                  controller: _tabs,
                  children: [
                    _buildDevicesTab(),
                    _buildPreRegTab(),
                  ],
                ),
    );
  }

  Widget _buildDevicesTab() {
    final q = _searchCtrl.text.toLowerCase();
    final filtered = _devices.where((d) {
      if (q.isEmpty) return true;
      return (d['device_id'] ?? '').toLowerCase().contains(q) ||
          (d['owner_name'] ?? '').toLowerCase().contains(q);
    }).toList()
      ..sort((a, b) => (b['online'] == true ? 1 : 0) - (a['online'] == true ? 1 : 0));

    final online = _devices.where((d) => d['online'] == true).length;

    return Column(children: [
      // Stats
      Padding(
        padding: const EdgeInsets.all(16),
        child: Row(children: [
          _statTile('Total', '${_devices.length}', AppTheme.textPrimary),
          const SizedBox(width: 10),
          _statTile('Online', '$online', AppTheme.green),
          const SizedBox(width: 10),
          _statTile('Offline', '${_devices.length - online}', AppTheme.red),
        ]),
      ),
      // Search
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: TextField(
          controller: _searchCtrl,
          onChanged: (_) => setState(() {}),
          decoration: const InputDecoration(
            hintText: 'Search by device ID or owner…',
            prefixIcon: Icon(Icons.search_rounded),
            isDense: true,
          ),
        ),
      ),
      const SizedBox(height: 12),
      // List
      Expanded(
        child: filtered.isEmpty
            ? const Center(child: Text('No devices found',
                style: TextStyle(color: AppTheme.textSecondary)))
            : ListView.separated(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: filtered.length,
                separatorBuilder: (_, __) => const SizedBox(height: 10),
                itemBuilder: (_, i) => _buildDeviceCard(filtered[i]),
              ),
      ),
    ]);
  }

  Widget _buildDeviceCard(Map<String, dynamic> d) {
    final deviceId = d['device_id'] as String;
    final online = d['online'] == true;
    final relays = (d['relays'] as Map<String, dynamic>?) ?? {};

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.card,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
            color: online ? AppTheme.green.withOpacity(0.25) : AppTheme.border),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: AppTheme.accent.withOpacity(0.12),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: AppTheme.accent.withOpacity(0.3)),
            ),
            child: Text(deviceId, style: GoogleFonts.outfit(
                color: AppTheme.accentLight, fontWeight: FontWeight.w700, fontSize: 12)),
          ),
          const SizedBox(width: 8),
          Container(
            width: 7, height: 7,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: online ? AppTheme.green : AppTheme.textTertiary,
            ),
          ),
          Text(' ${online ? "Online" : "Offline"}',
              style: TextStyle(
                  color: online ? AppTheme.green : AppTheme.textTertiary,
                  fontSize: 12)),
          const Spacer(),
          IconButton(
            icon: const Icon(Icons.delete_outline_rounded, color: AppTheme.red, size: 20),
            onPressed: () => _deleteDevice(deviceId),
            visualDensity: VisualDensity.compact,
          ),
        ]),
        const SizedBox(height: 6),
        Text('${d['owner_name']} · ${d['email'] ?? '—'}',
            style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
        if (relays.isNotEmpty) ...[
          const SizedBox(height: 10),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: relays.entries.map((e) {
              final state = e.value['state'] == true;
              return GestureDetector(
                onTap: () => _adminToggle(deviceId, e.key, !state),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: state ? AppTheme.accent.withOpacity(0.2) : AppTheme.surface,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                        color: state
                            ? AppTheme.accent.withOpacity(0.5)
                            : AppTheme.border),
                  ),
                  child: Text(
                    '${e.value['name'] ?? e.key}  ${state ? "ON" : "OFF"}',
                    style: TextStyle(
                        color: state ? AppTheme.accentLight : AppTheme.textTertiary,
                        fontSize: 11,
                        fontWeight: FontWeight.w600),
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ]),
    );
  }

  Widget _buildPreRegTab() => Column(children: [
    // Add form
    Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.card,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.border),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('Register New Device ID', style: GoogleFonts.outfit(
            fontWeight: FontWeight.w600, color: AppTheme.textSecondary,
            fontSize: 12, letterSpacing: 0.5)),
        const SizedBox(height: 12),
        Row(children: [
          Expanded(child: TextField(
            controller: _seedIdCtrl,
            textCapitalization: TextCapitalization.characters,
            decoration: const InputDecoration(
                labelText: 'Device ID', isDense: true,
                contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10)),
          )),
          const SizedBox(width: 8),
          Expanded(child: TextField(
            controller: _seedLabelCtrl,
            decoration: const InputDecoration(
                labelText: 'Label', isDense: true,
                contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10)),
          )),
        ]),
        const SizedBox(height: 10),
        Row(children: [
          DropdownButton<int>(
            value: _seedSwitches,
            dropdownColor: AppTheme.card,
            items: [2,4,6,8].map((n) => DropdownMenuItem(
                value: n, child: Text('$n switches'))).toList(),
            onChanged: (v) => setState(() => _seedSwitches = v!),
          ),
          const Spacer(),
          ElevatedButton(
            onPressed: _seedDevice,
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10)),
            child: const Text('+ Register'),
          ),
        ]),
      ]),
    ),
    // Table
    Expanded(child: _preReg.isEmpty
        ? const Center(child: Text('No pre-registered devices',
            style: TextStyle(color: AppTheme.textSecondary)))
        : ListView.separated(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: _preReg.length,
            separatorBuilder: (_, __) => const SizedBox(height: 6),
            itemBuilder: (_, i) {
              final d = _preReg[i];
              final claimed = d['is_claimed'] == true;
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: AppTheme.card,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppTheme.border),
                ),
                child: Row(children: [
                  Text(d['device_id'] ?? '', style: GoogleFonts.outfit(
                      color: AppTheme.accentLight, fontWeight: FontWeight.w700,
                      fontSize: 13)),
                  const SizedBox(width: 10),
                  Expanded(child: Text(d['label'] ?? '—',
                      style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12))),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: (claimed ? AppTheme.green : AppTheme.textTertiary)
                          .withOpacity(0.12),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(
                          color: (claimed ? AppTheme.green : AppTheme.textTertiary)
                              .withOpacity(0.3)),
                    ),
                    child: Text(claimed ? '✅ Claimed' : '⏳ Unclaimed',
                        style: TextStyle(
                            color: claimed ? AppTheme.green : AppTheme.textTertiary,
                            fontSize: 10, fontWeight: FontWeight.w600)),
                  ),
                  if (!claimed) ...[
                    const SizedBox(width: 6),
                    IconButton(
                      icon: const Icon(Icons.close_rounded,
                          color: AppTheme.red, size: 18),
                      onPressed: () async {
                        await ApiService.adminDeletePreRegistered(d['device_id']);
                        setState(() => _preReg.removeAt(i));
                      },
                      visualDensity: VisualDensity.compact,
                    ),
                  ],
                ]),
              );
            },
          )),
  ]);

  Widget _statTile(String label, String value, Color color) =>
      Expanded(child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: AppTheme.card,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppTheme.border),
        ),
        child: Column(children: [
          Text(value, style: GoogleFonts.outfit(
              fontSize: 24, fontWeight: FontWeight.bold, color: color)),
          Text(label, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
        ]),
      ));
}
