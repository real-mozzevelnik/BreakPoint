import 'package:shared_preferences/shared_preferences.dart';

class Storage {
  final _key = "token";

  Future<bool> isHaveToken() async {
    final _storage = await SharedPreferences.getInstance();
    final result = _storage.get(_key);
    return result == null ? false : true;
  }

  Future<String?> getTokenInStorage() async {
    final _storage = await SharedPreferences.getInstance();
    final result = _storage.getString(_key);
    return result;
  }

  Future<void> putTokenInStorage(String token) async {
    final _storage = await SharedPreferences.getInstance();
    _storage.setString(_key, token);
  }

  Future<void> deleteToken() async {
    final _storage = await SharedPreferences.getInstance();
    _storage.clear();
  }

  Future<void> saveUser(String _email, String _name) async {
    final _storage = await SharedPreferences.getInstance();
    _storage.setString("email", _email);
    _storage.setString("name", _name);
  }

  Future<Map<String, String?>> getUser() async {
    final _storage = await SharedPreferences.getInstance();
    Map<String, String?> result = {
      "email": _storage.getString("email"),
      "name": _storage.getString("name"),
    };
    return result;
  }
}
