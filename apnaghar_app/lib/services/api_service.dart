import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import 'auth_service.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  ApiException(this.message, [this.statusCode]);
  @override
  String toString() => message;
}

class ApiService {
  static Future<Map<String, String>> _headers({bool auth = true}) async {
    final headers = {'Content-Type': 'application/json'};
    if (auth) {
      final token = await AuthService.getToken();
      if (token != null && token.isNotEmpty) {
        headers['Authorization'] = 'Bearer $token';
      }
    }
    return headers;
  }

  static Future<dynamic> _handleResponse(http.Response res) async {
    dynamic body;
    try {
      body = jsonDecode(res.body);
    } catch (_) {
      body = {};
    }
    if (res.statusCode >= 200 && res.statusCode < 300) return body;
    final detail = body is Map ? (body['detail'] ?? 'Request failed') : 'Request failed';
    throw ApiException(detail.toString(), res.statusCode);
  }

  static Future<dynamic> get(String path, {bool auth = true}) async {
    final res = await http.get(
      Uri.parse('${ApiConfig.backendUrl}$path'),
      headers: await _headers(auth: auth),
    );
    return _handleResponse(res);
  }

  static Future<dynamic> post(String path, Map<String, dynamic> body,
      {bool auth = true}) async {
    final res = await http.post(
      Uri.parse('${ApiConfig.backendUrl}$path'),
      headers: await _headers(auth: auth),
      body: jsonEncode(body),
    );
    return _handleResponse(res);
  }

  static Future<dynamic> put(String path, Map<String, dynamic> body) async {
    final res = await http.put(
      Uri.parse('${ApiConfig.backendUrl}$path'),
      headers: await _headers(),
      body: jsonEncode(body),
    );
    return _handleResponse(res);
  }

  static Future<dynamic> delete(String path) async {
    final res = await http.delete(
      Uri.parse('${ApiConfig.backendUrl}$path'),
      headers: await _headers(),
    );
    return _handleResponse(res);
  }

  // ── Auth ─────────────────────────────────────────────────────────────────
  static Future<Map<String, dynamic>> login(String deviceId, String password) async {
    return await post(ApiConfig.login, {'device_id': deviceId, 'password': password}, auth: false);
  }

  static Future<Map<String, dynamic>> adminLogin(String email, String password) async {
    return await post(ApiConfig.adminLogin, {'email': email, 'password': password}, auth: false);
  }

  static Future<Map<String, dynamic>> checkDevice(String deviceId) async {
    return await get('${ApiConfig.checkDevice}/$deviceId', auth: false);
  }

  static Future<Map<String, dynamic>> claimDevice(Map<String, dynamic> data) async {
    return await post(ApiConfig.claim, data, auth: false);
  }

  // ── Device ────────────────────────────────────────────────────────────────
  static Future<Map<String, dynamic>> getDevice(String deviceId) async {
    return await get(ApiConfig.device(deviceId));
  }

  static Future<void> toggleRelay(String deviceId, String relayKey, bool state) async {
    await post(ApiConfig.relay(deviceId, relayKey), {'state': state});
  }

  static Future<void> renameRelay(String deviceId, String relayKey, String name) async {
    await put(ApiConfig.renameRelay(deviceId, relayKey), {'name': name});
  }

  // ── Schedules ─────────────────────────────────────────────────────────────
  static Future<List<dynamic>> getSchedules(String deviceId) async {
    return await get(ApiConfig.schedules(deviceId));
  }

  static Future<dynamic> createSchedule(String deviceId, Map<String, dynamic> data) async {
    return await post(ApiConfig.schedules(deviceId), data);
  }

  static Future<void> updateSchedule(String deviceId, String schedId, Map<String, dynamic> data) async {
    final res = await http.put(
      Uri.parse('${ApiConfig.backendUrl}${ApiConfig.schedule(deviceId, schedId)}'),
      headers: await _headers(),
      body: jsonEncode(data),
    );
    _handleResponse(res);
  }

  static Future<void> deleteSchedule(String deviceId, String schedId) async {
    await delete(ApiConfig.schedule(deviceId, schedId));
  }

  // ── Power ─────────────────────────────────────────────────────────────────
  static Future<Map<String, dynamic>> getPowerUsage(String deviceId, {int days = 7}) async {
    return await get('${ApiConfig.power(deviceId)}?days=$days');
  }

  // ── Admin ──────────────────────────────────────────────────────────────────
  static Future<List<dynamic>> adminGetDevices() async {
    return await get(ApiConfig.adminDevices);
  }

  static Future<List<dynamic>> adminGetPreRegistered() async {
    return await get(ApiConfig.adminPreRegistered);
  }

  static Future<void> adminSeedDevice(String deviceId, String label, int numSwitches) async {
    await post(ApiConfig.adminSeedDevices, {
      'device_id': deviceId,
      'label': label,
      'num_switches': numSwitches,
    });
  }

  static Future<void> adminDeleteDevice(String deviceId) async {
    await delete(ApiConfig.adminDeleteDevice(deviceId));
  }

  static Future<void> adminDeletePreRegistered(String deviceId) async {
    await delete(ApiConfig.adminDeletePreRegistered(deviceId));
  }
}
