import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  static const _storage = FlutterSecureStorage();
  static const _tokenKey = 'hc_token';
  static const _deviceKey = 'hc_device_id';
  static const _nameKey = 'hc_name';
  static const _adminKey = 'hc_is_admin';

  static Future<void> saveAuth({
    required String token,
    required String? deviceId,
    required String name,
    required bool isAdmin,
  }) async {
    await _storage.write(key: _tokenKey, value: token);
    await _storage.write(key: _deviceKey, value: deviceId ?? '');
    await _storage.write(key: _nameKey, value: name);
    await _storage.write(key: _adminKey, value: isAdmin ? '1' : '0');
  }

  static Future<String?> getToken() => _storage.read(key: _tokenKey);
  static Future<String?> getDeviceId() => _storage.read(key: _deviceKey);
  static Future<String?> getName() => _storage.read(key: _nameKey);
  static Future<bool> isAdmin() async =>
      (await _storage.read(key: _adminKey)) == '1';

  static Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }

  static Future<void> logout() async {
    await _storage.deleteAll();
  }
}
