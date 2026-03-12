class Schedule {
  final String id;
  final String deviceId;
  String relayKey;
  String action;
  String time;
  String days;
  bool enabled;
  String label;

  Schedule({
    required this.id,
    required this.deviceId,
    required this.relayKey,
    required this.action,
    required this.time,
    required this.days,
    required this.enabled,
    required this.label,
  });

  factory Schedule.fromJson(Map<String, dynamic> json) => Schedule(
        id: json['id'] ?? '',
        deviceId: json['device_id'] ?? '',
        relayKey: json['relay_key'] ?? 'relay1',
        action: json['action'] ?? 'on',
        time: json['time'] ?? '00:00',
        days: json['days'] ?? 'all',
        enabled: json['enabled'] ?? true,
        label: json['label'] ?? '',
      );

  String get daysDisplay {
    if (days == 'all') return 'Every day';
    return days;
  }

  String get actionLabel => action == 'on' ? 'Turn ON' : 'Turn OFF';
}
