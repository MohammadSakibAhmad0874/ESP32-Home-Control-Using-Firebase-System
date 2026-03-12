// ApnaGhar — API Configuration
// Update BACKEND_URL if your Railway URL changes.

class ApiConfig {
  static const String backendUrl =
      'https://esp32-home-control-using-firebase-system-production.up.railway.app';

  // REST endpoints
  static const String login = '/api/auth/login';
  static const String adminLogin = '/api/auth/admin-login';
  static const String claim = '/api/auth/claim';
  static const String checkDevice = '/api/devices/check';
  static const String me = '/api/auth/me';
  static String device(String id) => '/api/devices/$id';
  static String relay(String deviceId, String relayKey) =>
      '/api/devices/$deviceId/relay/$relayKey';
  static String renameRelay(String deviceId, String relayKey) =>
      '/api/devices/$deviceId/relay/$relayKey/rename';
  static String schedules(String deviceId) =>
      '/api/devices/$deviceId/schedules';
  static String schedule(String deviceId, String schedId) =>
      '/api/devices/$deviceId/schedules/$schedId';
  static String power(String deviceId) => '/api/devices/$deviceId/power';

  // Admin endpoints
  static const String adminDevices = '/api/admin/devices';
  static const String adminPreRegistered = '/api/admin/pre-registered';
  static const String adminSeedDevices = '/api/admin/seed-devices';
  static String adminDeleteDevice(String id) => '/api/admin/devices/$id';
  static String adminDeletePreRegistered(String id) =>
      '/api/admin/pre-registered/$id';

  // WebSocket
  static String dashboardWs(String deviceId, String token) {
    final base = backendUrl.replaceFirst('https://', 'wss://');
    return '$base/ws/dashboard/$deviceId?token=$token';
  }
}
