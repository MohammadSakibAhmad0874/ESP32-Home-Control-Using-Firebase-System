class Relay {
  final String key;
  String name;
  bool state;
  double wattage;

  Relay({
    required this.key,
    required this.name,
    required this.state,
    required this.wattage,
  });

  factory Relay.fromJson(String key, Map<String, dynamic> json) => Relay(
        key: key,
        name: json['name'] ?? key,
        state: json['state'] ?? false,
        wattage: (json['wattage'] ?? 60.0).toDouble(),
      );
}

class Device {
  final String deviceId;
  final String ownerName;
  final String email;
  final int numSwitches;
  bool online;
  int lastSeen;
  String ipAddress;
  Map<String, Relay> relays;

  Device({
    required this.deviceId,
    required this.ownerName,
    required this.email,
    required this.numSwitches,
    required this.online,
    required this.lastSeen,
    required this.ipAddress,
    required this.relays,
  });

  factory Device.fromJson(Map<String, dynamic> json) {
    final relaysRaw = json['relays'] as Map<String, dynamic>? ?? {};
    final relays = relaysRaw.map(
      (k, v) => MapEntry(k, Relay.fromJson(k, v as Map<String, dynamic>)),
    );
    return Device(
      deviceId: json['device_id'] ?? '',
      ownerName: json['owner_name'] ?? '',
      email: json['email'] ?? '',
      numSwitches: json['num_switches'] ?? 4,
      online: json['online'] ?? false,
      lastSeen: json['last_seen'] ?? 0,
      ipAddress: json['ip_address'] ?? '',
      relays: relays,
    );
  }

  List<Relay> get relayList {
    final list = relays.values.toList();
    list.sort((a, b) => a.key.compareTo(b.key));
    return list;
  }
}
