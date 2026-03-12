import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/theme.dart';
import '../models/device.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../services/websocket_service.dart';
import 'login_screen.dart';
import 'schedules_screen.dart';
import 'power_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final _ws = WebSocketService();
  Device? _device;
  bool _loading = true;
  String? _error;
  String? _deviceId;
  String? _token;
  StreamSubscription? _wsSub;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    _deviceId = await AuthService.getDeviceId();
    _token = await AuthService.getToken();
    await _loadDevice();
    if (_deviceId != null && _token != null) {
      _ws.connect(_deviceId!, _token!);
      _wsSub = _ws.stream?.listen(_handleWsMessage);
    }
  }

  void _handleWsMessage(Map<String, dynamic> msg) {
    if (!mounted) return;
    final type = msg['type'];
    if (type == 'relay_update') {
      final key = msg['relay_key'] as String?;
      final state = msg['state'] as bool?;
      if (key != null && state != null && _device != null) {
        setState(() => _device!.relays[key]?.state = state);
      }
    } else if (type == 'status') {
      setState(() => _device?.online = msg['online'] ?? _device!.online);
    }
  }

  Future<void> _loadDevice() async {
    if (_deviceId == null) return;
    setState(() { _loading = true; _error = null; });
    try {
      final data = await ApiService.getDevice(_deviceId!);
      setState(() => _device = Device.fromJson(data));
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _toggleRelay(String key, bool newState) async {
    setState(() => _device!.relays[key]!.state = newState);
    try {
      await ApiService.toggleRelay(_deviceId!, key, newState);
    } catch (_) {
      if (mounted) setState(() => _device!.relays[key]!.state = !newState);
    }
  }

  void _logout() async {
    await AuthService.logout();
    if (!mounted) return;
    Navigator.pushReplacement(context,
        MaterialPageRoute(builder: (_) => const LoginScreen()));
  }

  String _timeAgo(int ts) {
    if (ts == 0) return 'Never';
    final diff = DateTime.now().difference(DateTime.fromMillisecondsSinceEpoch(ts * 1000));
    if (diff.inSeconds < 60) return '${diff.inSeconds}s ago';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${diff.inDays}d ago';
  }

  String _icon(String name) {
    final n = name.toLowerCase();
    if (n.contains('fan')) return '🌀';
    if (n.contains('light') || n.contains('bulb')) return '💡';
    if (n.contains('kitchen')) return '🍳';
    if (n.contains('bedroom') || n.contains('bed')) return '🛏️';
    if (n.contains('living')) return '🛋️';
    if (n.contains('pump')) return '💧';
    if (n.contains('ac') || n.contains('air')) return '❄️';
    if (n.contains('tv') || n.contains('tele')) return '📺';
    return '⚡';
  }

  @override
  void dispose() {
    _wsSub?.cancel();
    _ws.disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(children: [
          const Text('🏠 ', style: TextStyle(fontSize: 20)),
          const Text('ApnaGhar'),
        ]),
        actions: [
          IconButton(onPressed: _loadDevice, icon: const Icon(Icons.refresh_rounded)),
          IconButton(onPressed: _logout, icon: const Icon(Icons.logout_rounded)),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.accent))
          : _error != null
              ? _buildError()
              : _device != null ? _buildContent() : const SizedBox(),
      bottomNavigationBar: _device != null ? _buildNavBar() : null,
    );
  }

  Widget _buildError() => Center(child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, color: AppTheme.red, size: 48),
          const SizedBox(height: 16),
          Text(_error!, style: const TextStyle(color: AppTheme.textSecondary)),
          const SizedBox(height: 24),
          ElevatedButton(onPressed: _loadDevice, child: const Text('Retry')),
        ],
      ));

  Widget _buildContent() {
    final d = _device!;
    return RefreshIndicator(
      onRefresh: _loadDevice,
      color: AppTheme.accent,
      backgroundColor: AppTheme.surface,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Status bar
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.card,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                  color: d.online
                      ? AppTheme.green.withOpacity(0.3)
                      : AppTheme.border),
            ),
            child: Row(children: [
              Container(
                width: 10, height: 10,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: d.online ? AppTheme.green : AppTheme.textTertiary,
                  boxShadow: d.online ? [BoxShadow(
                    color: AppTheme.green.withOpacity(0.5), blurRadius: 8)] : null,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(d.ownerName,
                      style: GoogleFonts.outfit(
                          fontWeight: FontWeight.w600, color: AppTheme.textPrimary)),
                  Text(
                    d.online
                        ? 'Online · IP: ${d.ipAddress}'
                        : 'Offline · Last seen ${_timeAgo(d.lastSeen)}',
                    style: GoogleFonts.outfit(
                        fontSize: 12, color: AppTheme.textSecondary),
                  ),
                ],
              )),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: AppTheme.accent.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppTheme.accent.withOpacity(0.3)),
                ),
                child: Text(d.deviceId,
                    style: GoogleFonts.outfit(
                        color: AppTheme.accentLight,
                        fontWeight: FontWeight.w700,
                        fontSize: 12,
                        fontFeatures: const [FontFeature.enable('mono')])),
              ),
            ]),
          ),
          const SizedBox(height: 20),
          Text('Controls',
              style: GoogleFonts.outfit(
                  color: AppTheme.textSecondary,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 1)),
          const SizedBox(height: 12),
          // Relay grid
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              childAspectRatio: 1.4,
            ),
            itemCount: d.relayList.length,
            itemBuilder: (_, i) {
              final relay = d.relayList[i];
              return _buildRelayCard(relay);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildRelayCard(Relay relay) {
    return GestureDetector(
      onTap: () => _toggleRelay(relay.key, !relay.state),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 250),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: relay.state
              ? AppTheme.accent.withOpacity(0.15)
              : AppTheme.card,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: relay.state
                ? AppTheme.accent.withOpacity(0.5)
                : AppTheme.border,
            width: relay.state ? 1.5 : 1,
          ),
          boxShadow: relay.state
              ? [BoxShadow(
                  color: AppTheme.accent.withOpacity(0.2),
                  blurRadius: 16,
                  spreadRadius: 2)]
              : null,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(_icon(relay.name), style: const TextStyle(fontSize: 24)),
                Switch(
                  value: relay.state,
                  onChanged: (v) => _toggleRelay(relay.key, v),
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
              ],
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(relay.name,
                    style: GoogleFonts.outfit(
                        color: relay.state ? AppTheme.textPrimary : AppTheme.textSecondary,
                        fontWeight: FontWeight.w600,
                        fontSize: 14),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis),
                Text(relay.state ? 'ON' : 'OFF',
                    style: GoogleFonts.outfit(
                        color: relay.state ? AppTheme.accent : AppTheme.textTertiary,
                        fontSize: 11,
                        fontWeight: FontWeight.w600)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNavBar() => NavigationBar(
    backgroundColor: AppTheme.surface,
    indicatorColor: AppTheme.accent.withOpacity(0.2),
    selectedIndex: 0,
    onDestinationSelected: (i) {
      if (i == 1) {
        Navigator.push(context, MaterialPageRoute(
            builder: (_) => SchedulesScreen(deviceId: _deviceId!)));
      } else if (i == 2) {
        Navigator.push(context, MaterialPageRoute(
            builder: (_) => PowerScreen(deviceId: _deviceId!)));
      }
    },
    destinations: const [
      NavigationDestination(icon: Icon(Icons.home_rounded), label: 'Home'),
      NavigationDestination(icon: Icon(Icons.schedule_rounded), label: 'Schedules'),
      NavigationDestination(icon: Icon(Icons.bolt_rounded), label: 'Power'),
    ],
  );
}
