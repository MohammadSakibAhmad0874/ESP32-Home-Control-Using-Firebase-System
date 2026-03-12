import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/theme.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'dashboard_screen.dart';
import 'admin_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabs;
  bool _loading = false;
  String? _error;

  // Login
  final _loginDeviceCtrl = TextEditingController();
  final _loginPassCtrl = TextEditingController();

  // Admin
  final _adminEmailCtrl = TextEditingController();
  final _adminPassCtrl = TextEditingController();

  // Claim step 1
  final _claimIdCtrl = TextEditingController();
  String? _claimMsg;
  int? _claimSwitches;
  bool _claimChecked = false;

  // Claim step 2
  final _claimNameCtrl = TextEditingController();
  final _claimEmailCtrl = TextEditingController();
  final _claimPassCtrl = TextEditingController();
  final List<TextEditingController> _swNameCtrls = [];

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 3, vsync: this);
    _tabs.addListener(() => setState(() => _error = null));
  }

  @override
  void dispose() {
    _tabs.dispose();
    _loginDeviceCtrl.dispose();
    _loginPassCtrl.dispose();
    _adminEmailCtrl.dispose();
    _adminPassCtrl.dispose();
    _claimIdCtrl.dispose();
    _claimNameCtrl.dispose();
    _claimEmailCtrl.dispose();
    _claimPassCtrl.dispose();
    for (final c in _swNameCtrls) c.dispose();
    super.dispose();
  }

  void _showError(String msg) => setState(() => _error = msg);
  void _clearError() => setState(() => _error = null);

  Future<void> _handleLogin() async {
    _clearError();
    setState(() => _loading = true);
    try {
      final data = await ApiService.login(
        _loginDeviceCtrl.text.trim().toUpperCase(),
        _loginPassCtrl.text,
      );
      await AuthService.saveAuth(
        token: data['token'],
        deviceId: data['device_id'],
        name: data['name'],
        isAdmin: data['is_admin'] ?? false,
      );
      if (!mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) =>
              data['is_admin'] == true ? const AdminScreen() : const DashboardScreen(),
        ),
      );
    } on ApiException catch (e) {
      _showError(e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _handleAdminLogin() async {
    _clearError();
    setState(() => _loading = true);
    try {
      final data = await ApiService.adminLogin(
        _adminEmailCtrl.text.trim(),
        _adminPassCtrl.text,
      );
      await AuthService.saveAuth(
        token: data['token'],
        deviceId: data['device_id'],
        name: data['name'],
        isAdmin: true,
      );
      if (!mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const AdminScreen()),
      );
    } on ApiException catch (e) {
      _showError(e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _checkDeviceId() async {
    _clearError();
    setState(() => _loading = true);
    try {
      final id = _claimIdCtrl.text.trim().toUpperCase();
      final data = await ApiService.checkDevice(id);
      final n = data['num_switches'] as int? ?? 4;
      setState(() {
        _claimSwitches = n;
        _claimChecked = true;
        _swNameCtrls.clear();
        final defaults = ['Living Room', 'Bedroom', 'Kitchen', 'Fan',
          'Switch 5', 'Switch 6', 'Switch 7', 'Switch 8'];
        for (int i = 0; i < n; i++) {
          _swNameCtrls.add(TextEditingController(
              text: i < defaults.length ? defaults[i] : 'Switch ${i + 1}'));
        }
      });
    } on ApiException catch (e) {
      _showError(e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _handleClaim() async {
    _clearError();
    setState(() => _loading = true);
    try {
      final switchNames = _swNameCtrls.map((c) => c.text.trim()).toList();
      final data = await ApiService.claimDevice({
        'device_id': _claimIdCtrl.text.trim().toUpperCase(),
        'name': _claimNameCtrl.text.trim(),
        'email': _claimEmailCtrl.text.trim(),
        'password': _claimPassCtrl.text,
        'switch_names': switchNames,
      });
      await AuthService.saveAuth(
        token: data['token'],
        deviceId: data['device_id'],
        name: data['name'],
        isAdmin: false,
      );
      if (!mounted) return;
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const DashboardScreen()),
      );
    } on ApiException catch (e) {
      _showError(e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Widget _buildErrorBanner() => _error == null
      ? const SizedBox.shrink()
      : Container(
          margin: const EdgeInsets.only(bottom: 16),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: AppTheme.red.withOpacity(0.12),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: AppTheme.red.withOpacity(0.3)),
          ),
          child: Row(children: [
            const Icon(Icons.error_outline, color: AppTheme.red, size: 18),
            const SizedBox(width: 8),
            Expanded(child: Text(_error!,
                style: const TextStyle(color: AppTheme.red, fontSize: 13))),
          ]),
        );

  Widget _buildLoginTab() => Column(children: [
        const SizedBox(height: 8),
        _buildErrorBanner(),
        TextField(
          controller: _loginDeviceCtrl,
          textCapitalization: TextCapitalization.characters,
          decoration: const InputDecoration(
            labelText: 'Device ID',
            hintText: 'e.g. MICK345',
            prefixIcon: Icon(Icons.devices_rounded),
          ),
        ),
        const SizedBox(height: 14),
        TextField(
          controller: _loginPassCtrl,
          obscureText: true,
          decoration: const InputDecoration(
            labelText: 'Password',
            prefixIcon: Icon(Icons.lock_outline_rounded),
          ),
          onSubmitted: (_) => _handleLogin(),
        ),
        const SizedBox(height: 20),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: _loading ? null : _handleLogin,
            icon: const Icon(Icons.login_rounded),
            label: _loading
                ? const SizedBox(
                    width: 18, height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                : const Text('Login to Dashboard'),
          ),
        ),
      ]);

  Widget _buildAdminTab() => Column(children: [
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          margin: const EdgeInsets.only(bottom: 16),
          decoration: BoxDecoration(
            color: AppTheme.accent.withOpacity(0.08),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: AppTheme.accent.withOpacity(0.25)),
          ),
          child: Row(children: [
            const Text('👑', style: TextStyle(fontSize: 20)),
            const SizedBox(width: 10),
            Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('Admin Access',
                  style: GoogleFonts.outfit(
                      color: AppTheme.accentLight, fontWeight: FontWeight.w600, fontSize: 13)),
              const Text('Full control over all devices',
                  style: TextStyle(color: AppTheme.textTertiary, fontSize: 11)),
            ]),
          ]),
        ),
        _buildErrorBanner(),
        TextField(
          controller: _adminEmailCtrl,
          keyboardType: TextInputType.emailAddress,
          decoration: const InputDecoration(
            labelText: 'Admin Email',
            hintText: 'admin@apnaghar.com',
            prefixIcon: Icon(Icons.email_outlined),
          ),
        ),
        const SizedBox(height: 14),
        TextField(
          controller: _adminPassCtrl,
          obscureText: true,
          decoration: const InputDecoration(
            labelText: 'Password',
            prefixIcon: Icon(Icons.lock_outline_rounded),
          ),
          onSubmitted: (_) => _handleAdminLogin(),
        ),
        const SizedBox(height: 20),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.accent,
            ),
            onPressed: _loading ? null : _handleAdminLogin,
            icon: const Text('👑', style: TextStyle(fontSize: 16)),
            label: _loading
                ? const SizedBox(width: 18, height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                : const Text('Login as Admin'),
          ),
        ),
      ]);

  Widget _buildClaimTab() {
    if (_claimChecked) {
      return Column(children: [
        Container(
          padding: const EdgeInsets.all(12),
          margin: const EdgeInsets.only(bottom: 16),
          decoration: BoxDecoration(
            color: AppTheme.green.withOpacity(0.1),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: AppTheme.green.withOpacity(0.3)),
          ),
          child: Row(children: [
            const Icon(Icons.check_circle, color: AppTheme.green, size: 20),
            const SizedBox(width: 8),
            Expanded(child: Text(
              '✅ Device ${_claimIdCtrl.text.trim().toUpperCase()} is available! Set up your account.',
              style: const TextStyle(color: AppTheme.green, fontSize: 13),
            )),
          ]),
        ),
        _buildErrorBanner(),
        TextField(controller: _claimNameCtrl,
            decoration: const InputDecoration(labelText: 'Your Name',
                prefixIcon: Icon(Icons.person_outline_rounded))),
        const SizedBox(height: 12),
        TextField(controller: _claimEmailCtrl,
            keyboardType: TextInputType.emailAddress,
            decoration: const InputDecoration(labelText: 'Email',
                prefixIcon: Icon(Icons.email_outlined))),
        const SizedBox(height: 12),
        TextField(controller: _claimPassCtrl, obscureText: true,
            decoration: const InputDecoration(labelText: 'Choose a Password (min 6)',
                prefixIcon: Icon(Icons.lock_outline_rounded))),
        const SizedBox(height: 16),
        Align(alignment: Alignment.centerLeft,
            child: Text('Switch Names', style: GoogleFonts.outfit(
                color: AppTheme.textSecondary, fontWeight: FontWeight.w600))),
        const SizedBox(height: 8),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _swNameCtrls.length,
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2, mainAxisSpacing: 8, crossAxisSpacing: 8, childAspectRatio: 3.5),
          itemBuilder: (_, i) => TextField(
            controller: _swNameCtrls[i],
            decoration: InputDecoration(
              labelText: 'Switch ${i + 1}',
              isDense: true,
              contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            ),
          ),
        ),
        const SizedBox(height: 20),
        SizedBox(width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _loading ? null : _handleClaim,
              icon: const Icon(Icons.home_rounded),
              label: _loading
                  ? const SizedBox(width: 18, height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Text('Activate My Device'),
            )),
        TextButton(
          onPressed: () => setState(() { _claimChecked = false; }),
          child: const Text('← Use a different Device ID',
              style: TextStyle(color: AppTheme.textTertiary, fontSize: 13)),
        ),
      ]);
    }

    return Column(children: [
      const SizedBox(height: 8),
      Text('Enter the Device ID provided to you by the admin.',
          style: GoogleFonts.outfit(color: AppTheme.textSecondary, fontSize: 13, height: 1.5)),
      const SizedBox(height: 16),
      _buildErrorBanner(),
      TextField(
        controller: _claimIdCtrl,
        textCapitalization: TextCapitalization.characters,
        decoration: const InputDecoration(
          labelText: 'Device ID',
          hintText: 'e.g. USER001',
          prefixIcon: Icon(Icons.qr_code_rounded),
        ),
      ),
      const SizedBox(height: 16),
      SizedBox(width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: _loading ? null : _checkDeviceId,
            icon: const Icon(Icons.search_rounded),
            label: _loading
                ? const SizedBox(width: 18, height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                : const Text('Check ID'),
          )),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
          child: Column(children: [
            const SizedBox(height: 20),
            // Brand
            Container(
              width: 70,
              height: 70,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: const LinearGradient(
                    colors: [AppTheme.accent, AppTheme.accentLight]),
                boxShadow: [BoxShadow(
                    color: AppTheme.accent.withOpacity(0.4),
                    blurRadius: 24,
                    spreadRadius: 4)],
              ),
              child: const Icon(Icons.home_rounded, size: 36, color: Colors.white),
            ),
            const SizedBox(height: 16),
            Text('ApnaGhar', style: GoogleFonts.outfit(
                fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white)),
            const SizedBox(height: 4),
            Text('Apna Ghar, Apna Control',
                style: GoogleFonts.outfit(fontSize: 13, color: AppTheme.textSecondary)),
            const SizedBox(height: 32),
            // Tabs
            Container(
              decoration: BoxDecoration(
                color: AppTheme.surface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppTheme.border),
              ),
              child: TabBar(
                controller: _tabs,
                indicator: BoxDecoration(
                  borderRadius: BorderRadius.circular(10),
                  color: AppTheme.accent.withOpacity(0.2),
                  border: Border.all(color: AppTheme.accent.withOpacity(0.4)),
                ),
                tabs: const [
                  Tab(text: 'Login'),
                  Tab(text: 'Claim Device'),
                  Tab(text: '👑 Admin'),
                ],
                labelStyle: GoogleFonts.outfit(fontWeight: FontWeight.w600),
                unselectedLabelStyle: GoogleFonts.outfit(),
                labelColor: AppTheme.accentLight,
                unselectedLabelColor: AppTheme.textSecondary,
                dividerColor: Colors.transparent,
              ),
            ),
            const SizedBox(height: 24),
            // Tab content
            TabBarView(
              controller: _tabs,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                _buildLoginTab(),
                _buildClaimTab(),
                _buildAdminTab(),
              ],
            ),
          ]),
        ),
      ),
    );
  }
}
