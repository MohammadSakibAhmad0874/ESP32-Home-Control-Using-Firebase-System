import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../config/api_config.dart';
import '../models/device.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  StreamController<Map<String, dynamic>>? _controller;
  Timer? _reconnectTimer;
  String? _deviceId;
  String? _token;
  bool _disposed = false;

  Stream<Map<String, dynamic>>? get stream => _controller?.stream;

  void connect(String deviceId, String token) {
    _deviceId = deviceId;
    _token = token;
    _disposed = false;
    _controller ??= StreamController<Map<String, dynamic>>.broadcast();
    _doConnect();
  }

  void _doConnect() {
    if (_disposed || _deviceId == null || _token == null) return;
    try {
      final url = ApiConfig.dashboardWs(_deviceId!, _token!);
      _channel = WebSocketChannel.connect(Uri.parse(url));
      _channel!.stream.listen(
        (raw) {
          try {
            final data = jsonDecode(raw as String) as Map<String, dynamic>;
            if (!_disposed) _controller?.add(data);
          } catch (_) {}
        },
        onDone: _scheduleReconnect,
        onError: (_) => _scheduleReconnect(),
      );
    } catch (_) {
      _scheduleReconnect();
    }
  }

  void _scheduleReconnect() {
    if (_disposed) return;
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 5), _doConnect);
  }

  void send(Map<String, dynamic> data) {
    try {
      _channel?.sink.add(jsonEncode(data));
    } catch (_) {}
  }

  void disconnect() {
    _disposed = true;
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _controller?.close();
    _controller = null;
  }
}
