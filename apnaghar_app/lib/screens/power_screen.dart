import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import '../config/theme.dart';
import '../services/api_service.dart';

class PowerScreen extends StatefulWidget {
  final String deviceId;
  const PowerScreen({super.key, required this.deviceId});

  @override
  State<PowerScreen> createState() => _PowerScreenState();
}

class _PowerScreenState extends State<PowerScreen> {
  Map<String, dynamic>? _data;
  bool _loading = true;
  String? _error;
  int _days = 7;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final data = await ApiService.getPowerUsage(widget.deviceId, days: _days);
      setState(() => _data = data);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Power Usage'),
        actions: [
          DropdownButton<int>(
            value: _days,
            dropdownColor: AppTheme.card,
            underline: const SizedBox(),
            style: GoogleFonts.outfit(color: AppTheme.textSecondary, fontSize: 13),
            items: const [
              DropdownMenuItem(value: 7, child: Text('7 days')),
              DropdownMenuItem(value: 14, child: Text('14 days')),
              DropdownMenuItem(value: 30, child: Text('30 days')),
            ],
            onChanged: (v) => setState(() { _days = v!; _load(); }),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.accent))
          : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: AppTheme.textSecondary)))
              : _data == null
                  ? const Center(child: Text('No data'))
                  : _buildContent(),
    );
  }

  Widget _buildContent() {
    final summary = _data!['summary'] as Map<String, dynamic>? ?? {};
    final perRelay = _data!['per_relay'] as Map<String, dynamic>? ?? {};
    final totalKwh = (summary['total_kwh'] ?? 0.0).toDouble();
    final totalCost = (summary['total_cost'] ?? 0.0).toDouble();

    final relayKeys = perRelay.keys.toList();
    final bars = relayKeys.asMap().entries.map((e) {
      final kwh = (perRelay[e.value]['kwh'] ?? 0.0).toDouble();
      return BarChartGroupData(x: e.key, barRods: [
        BarChartRodData(
          toY: kwh,
          gradient: const LinearGradient(
              colors: [AppTheme.accent, AppTheme.accentLight],
              begin: Alignment.bottomCenter,
              end: Alignment.topCenter),
          width: 22,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(6)),
        ),
      ]);
    }).toList();

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Summary cards
        Row(children: [
          _summaryCard('Total kWh', '${totalKwh.toStringAsFixed(2)} kWh',
              Icons.bolt_rounded, AppTheme.accent),
          const SizedBox(width: 12),
          _summaryCard('Est. Cost', '₹${totalCost.toStringAsFixed(2)}',
              Icons.currency_rupee_rounded, AppTheme.amber),
        ]),
        const SizedBox(height: 24),
        // Bar Chart
        if (bars.isNotEmpty) ...[
          Text('Per Switch Usage',
              style: GoogleFonts.outfit(
                  color: AppTheme.textSecondary,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 1)),
          const SizedBox(height: 12),
          Container(
            height: 220,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.card,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppTheme.border),
            ),
            child: BarChart(BarChartData(
              gridData: FlGridData(
                  drawHorizontalLine: true,
                  horizontalInterval: 1,
                  getDrawingHorizontalLine: (_) =>
                      FlLine(color: AppTheme.border, strokeWidth: 1)),
              borderData: FlBorderData(show: false),
              titlesData: FlTitlesData(
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    getTitlesWidget: (v, _) {
                      final k = relayKeys[v.toInt()];
                      return Padding(
                        padding: const EdgeInsets.only(top: 4),
                        child: Text(k.toUpperCase(),
                            style: const TextStyle(
                                color: AppTheme.textTertiary, fontSize: 10)),
                      );
                    },
                  ),
                ),
                leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 36,
                        getTitlesWidget: (v, _) => Text(
                            v.toStringAsFixed(1),
                            style: const TextStyle(
                                color: AppTheme.textTertiary, fontSize: 10)))),
                topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
              ),
              barGroups: bars,
            )),
          ),
          const SizedBox(height: 20),
        ],
        // Per-relay detail list
        Text('Details',
            style: GoogleFonts.outfit(
                color: AppTheme.textSecondary,
                fontSize: 12,
                fontWeight: FontWeight.w600,
                letterSpacing: 1)),
        const SizedBox(height: 12),
        ...relayKeys.map((k) {
          final r = perRelay[k] as Map<String, dynamic>;
          final kwh = (r['kwh'] ?? 0.0).toDouble();
          final cost = (r['cost'] ?? 0.0).toDouble();
          final hours = (r['hours_on'] ?? 0.0).toDouble();
          return Container(
            margin: const EdgeInsets.only(bottom: 10),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: AppTheme.card,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: AppTheme.border),
            ),
            child: Row(children: [
              const Text('⚡', style: TextStyle(fontSize: 22)),
              const SizedBox(width: 12),
              Expanded(child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(k.toUpperCase(),
                      style: GoogleFonts.outfit(
                          fontWeight: FontWeight.w600, color: AppTheme.textPrimary)),
                  Text('${hours.toStringAsFixed(1)}h on  ·  ${kwh.toStringAsFixed(3)} kWh',
                      style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
                ],
              )),
              Text('₹${cost.toStringAsFixed(2)}',
                  style: GoogleFonts.outfit(
                      color: AppTheme.amber,
                      fontWeight: FontWeight.w700,
                      fontSize: 15)),
            ]),
          );
        }),
      ],
    );
  }

  Widget _summaryCard(String label, String value, IconData icon, Color color) =>
      Expanded(child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppTheme.card,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.25)),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Icon(icon, color: color, size: 22),
          const SizedBox(height: 8),
          Text(value,
              style: GoogleFonts.outfit(
                  color: color, fontWeight: FontWeight.bold, fontSize: 18)),
          Text(label,
              style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
        ]),
      ));
}
