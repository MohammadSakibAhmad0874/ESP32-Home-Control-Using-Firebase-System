import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/theme.dart';
import '../models/schedule.dart';
import '../services/api_service.dart';

class SchedulesScreen extends StatefulWidget {
  final String deviceId;
  const SchedulesScreen({super.key, required this.deviceId});

  @override
  State<SchedulesScreen> createState() => _SchedulesScreenState();
}

class _SchedulesScreenState extends State<SchedulesScreen> {
  List<Schedule> _schedules = [];
  bool _loading = true;
  String? _error;

  final _days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final data = await ApiService.getSchedules(widget.deviceId);
      setState(() => _schedules = data.map((j) => Schedule.fromJson(j)).toList());
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _delete(Schedule s) async {
    try {
      await ApiService.deleteSchedule(widget.deviceId, s.id);
      setState(() => _schedules.remove(s));
    } on ApiException catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.message), backgroundColor: AppTheme.red));
    }
  }

  Future<void> _toggleEnabled(Schedule s) async {
    final newVal = !s.enabled;
    try {
      await ApiService.updateSchedule(widget.deviceId, s.id, {'enabled': newVal});
      setState(() => s.enabled = newVal);
    } on ApiException catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.message), backgroundColor: AppTheme.red));
    }
  }

  Future<void> _showAddDialog() async {
    String relayKey = 'relay1';
    String action = 'on';
    TimeOfDay time = TimeOfDay.now();
    Set<String> selectedDays = {'all'};
    bool allDays = true;

    await showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.surface,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => StatefulBuilder(builder: (ctx, setS) {
        return Padding(
          padding: EdgeInsets.only(
              left: 24, right: 24, top: 24,
              bottom: MediaQuery.of(ctx).viewInsets.bottom + 24),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            Text('Add Schedule', style: GoogleFonts.outfit(
                fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.textPrimary)),
            const SizedBox(height: 20),
            // Relay key
            DropdownButtonFormField<String>(
              value: relayKey,
              dropdownColor: AppTheme.card,
              decoration: const InputDecoration(labelText: 'Switch'),
              items: ['relay1','relay2','relay3','relay4','relay5','relay6'].map((k) =>
                  DropdownMenuItem(value: k, child: Text(k.toUpperCase()))).toList(),
              onChanged: (v) => setS(() => relayKey = v!),
            ),
            const SizedBox(height: 12),
            // Action
            DropdownButtonFormField<String>(
              value: action,
              dropdownColor: AppTheme.card,
              decoration: const InputDecoration(labelText: 'Action'),
              items: const [
                DropdownMenuItem(value: 'on', child: Text('Turn ON')),
                DropdownMenuItem(value: 'off', child: Text('Turn OFF')),
              ],
              onChanged: (v) => setS(() => action = v!),
            ),
            const SizedBox(height: 12),
            // Time
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: Text('Time: ${time.format(ctx)}',
                  style: const TextStyle(color: AppTheme.textPrimary)),
              trailing: const Icon(Icons.access_time, color: AppTheme.accent),
              onTap: () async {
                final t = await showTimePicker(context: ctx, initialTime: time);
                if (t != null) setS(() => time = t);
              },
            ),
            // Days
            SwitchListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('Every Day', style: TextStyle(color: AppTheme.textPrimary)),
              value: allDays,
              activeColor: AppTheme.accent,
              onChanged: (v) => setS(() {
                allDays = v;
                selectedDays = v ? {'all'} : {};
              }),
            ),
            if (!allDays) Wrap(
              spacing: 6,
              children: _days.map((d) {
                final sel = selectedDays.contains(d);
                return FilterChip(
                  label: Text(d),
                  selected: sel,
                  onSelected: (v) => setS(() =>
                    v ? selectedDays.add(d) : selectedDays.remove(d)),
                  selectedColor: AppTheme.accent.withOpacity(0.25),
                  checkmarkColor: AppTheme.accentLight,
                  labelStyle: TextStyle(
                      color: sel ? AppTheme.accentLight : AppTheme.textSecondary,
                      fontSize: 12),
                  backgroundColor: AppTheme.card,
                  side: BorderSide(color: sel ? AppTheme.accent : AppTheme.border),
                );
              }).toList(),
            ),
            const SizedBox(height: 20),
            SizedBox(width: double.infinity,
                child: ElevatedButton(
                  onPressed: () async {
                    Navigator.pop(ctx);
                    final h = time.hour.toString().padLeft(2, '0');
                    final m = time.minute.toString().padLeft(2, '0');
                    try {
                      await ApiService.createSchedule(widget.deviceId, {
                        'relay_key': relayKey,
                        'action': action,
                        'time': '$h:$m',
                        'days': allDays ? 'all' : selectedDays.join(','),
                        'enabled': true,
                      });
                      await _load();
                    } on ApiException catch (e) {
                      if (mounted) ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text(e.message), backgroundColor: AppTheme.red));
                    }
                  },
                  child: const Text('Add Schedule'),
                )),
          ]),
        );
      }),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Schedules'),
        actions: [IconButton(onPressed: _load, icon: const Icon(Icons.refresh_rounded))],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showAddDialog,
        backgroundColor: AppTheme.accent,
        child: const Icon(Icons.add_rounded),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.accent))
          : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: AppTheme.textSecondary)))
              : _schedules.isEmpty
                  ? Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                      const Icon(Icons.schedule_rounded, size: 56, color: AppTheme.textTertiary),
                      const SizedBox(height: 16),
                      Text('No schedules yet', style: GoogleFonts.outfit(
                          color: AppTheme.textSecondary, fontSize: 16)),
                      const SizedBox(height: 8),
                      const Text('Tap + to add an automation',
                          style: TextStyle(color: AppTheme.textTertiary, fontSize: 13)),
                    ]))
                  : ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: _schedules.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 10),
                      itemBuilder: (_, i) {
                        final s = _schedules[i];
                        return Dismissible(
                          key: Key(s.id),
                          direction: DismissDirection.endToStart,
                          onDismissed: (_) => _delete(s),
                          background: Container(
                            alignment: Alignment.centerRight,
                            padding: const EdgeInsets.only(right: 20),
                            decoration: BoxDecoration(
                              color: AppTheme.red.withOpacity(0.15),
                              borderRadius: BorderRadius.circular(14),
                            ),
                            child: const Icon(Icons.delete_outline_rounded, color: AppTheme.red),
                          ),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                            decoration: BoxDecoration(
                              color: AppTheme.card,
                              borderRadius: BorderRadius.circular(14),
                              border: Border.all(
                                  color: s.enabled ? AppTheme.border : AppTheme.border.withOpacity(0.4)),
                            ),
                            child: Row(children: [
                              Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: (s.action == 'on' ? AppTheme.green : AppTheme.red)
                                      .withOpacity(0.12),
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: Icon(
                                  s.action == 'on' ? Icons.power_rounded : Icons.power_off_rounded,
                                  color: s.action == 'on' ? AppTheme.green : AppTheme.red,
                                  size: 20,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text('${s.relayKey.toUpperCase()} → ${s.actionLabel}',
                                      style: GoogleFonts.outfit(
                                          color: AppTheme.textPrimary, fontWeight: FontWeight.w600)),
                                  Text('${s.time}  ·  ${s.daysDisplay}',
                                      style: GoogleFonts.outfit(
                                          color: AppTheme.textSecondary, fontSize: 12)),
                                ],
                              )),
                              Switch(value: s.enabled, onChanged: (_) => _toggleEnabled(s)),
                            ]),
                          ),
                        );
                      },
                    ),
    );
  }
}
