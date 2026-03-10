import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // ============================================================
  // IMPORTANT: Change this to your Django server IP address!
  // When running on a physical phone, use your PC's local IPiiiiiiiiiiiii                    
  // e.g. http://192.168.1.5:8000
  // Find your IP by running "ipconfig" in PowerShell
  // ============================================================
  static const String BASE_URL = 'http://172.20.10.2:8000';


  // Get the stored authentication token
  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('token');
  }

  // Build authorization headers
  static Future<Map<String, String>> getHeaders() async {
    final token = await getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Token $token',
    };
  }

  // ---- LOGIN ----
  static Future<Map<String, dynamic>> login(
      String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$BASE_URL/api/user/login/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'password': password}),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        // Save token and username locally
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('token', data['token']);
        await prefs.setString('username', data['username'] ?? username);
        return {'success': true, 'data': data};
      } else {
        final data = jsonDecode(response.body);
        return {
          'success': false,
          'message': data['error'] ?? 'Invalid credentials'
        };
      }
    } catch (e) {
      print('====== LOGIN ERROR ======');
      print(e);
      print('=========================');
      return {
        'success': false,
        'message': 'Cannot connect to server. Check your internet connection.'
      };
    }
  }

  // ---- REGISTER ----
  static Future<Map<String, dynamic>> register(Map<String, String> data) async {
    try {
      final response = await http.post(
        Uri.parse('$BASE_URL/api/user/register/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(data),
      );
      if (response.statusCode == 201) {
        return {'success': true};
      } else {
        final resp = jsonDecode(response.body);
        return {'success': false, 'message': resp['error'] ?? resp.toString()};
      }
    } catch (e) {
      return {'success': false, 'message': 'Connection error: $e'};
    }
  }

  // ---- DIVISIONS (public, no auth needed) ----
  static Future<List<Map<String, dynamic>>> getDivisions() async {
    try {
      final response = await http.get(
        Uri.parse('$BASE_URL/api/divisions/'),
        headers: {'Content-Type': 'application/json'},
      );
      if (response.statusCode == 200) {
        final List<dynamic> raw = jsonDecode(response.body);
        return List<Map<String, dynamic>>.from(raw);
      }
      print('====== DIVISIONS API ERROR ======: Status Code ${response.statusCode}, Body: ${response.body}');
      return [];
    } catch (e) {
      print('====== DIVISIONS EXCEPTION ======: $e');
      return [];
    }
  }

  // ---- LOGOUT ----
  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    await prefs.remove('username');
  }

  // ---- FIRE ALERTS ----
  static Future<List<dynamic>> getFireAlerts() async {
    try {
      final headers = await getHeaders();
      final response = await http.get(
        Uri.parse('$BASE_URL/api/fire-alerts/'),
        headers: headers,
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  // ---- ANIMAL ALERTS ----
  static Future<List<dynamic>> getAnimalAlerts() async {
    try {
      final headers = await getHeaders();
      final response = await http.get(
        Uri.parse('$BASE_URL/api/animal-alerts/'),
        headers: headers,
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  // ---- NOTIFICATIONS ----
  static Future<List<dynamic>> getNotifications() async {
    try {
      final headers = await getHeaders();
      final response = await http.get(
        Uri.parse('$BASE_URL/api/notifications/'),
        headers: headers,
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  // ---- ANIMALS (Division-wise) ----
  static Future<List<dynamic>> getAnimals({String? division}) async {
    try {
      final headers = await getHeaders();
      final url = division != null
          ? '$BASE_URL/api/animals/?division=$division'
          : '$BASE_URL/api/animals/';
      final response = await http.get(Uri.parse(url), headers: headers);
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  // ---- SEND COMPLAINT ----
  static Future<Map<String, dynamic>> sendComplaint(
      String subject, String message) async {
    try {
      final headers = await getHeaders();
      final response = await http.post(
        Uri.parse('$BASE_URL/api/complaints/'),
        headers: headers,
        body: jsonEncode({
          'subject': subject,
          'message': message,
        }),
      );
      if (response.statusCode == 201) {
        return {'success': true};
      }
      return {'success': false, 'message': 'Failed to send complaint'};
    } catch (e) {
      return {'success': false, 'message': 'Connection error'};
    }
  }

  // ---- VIEW MY COMPLAINTS ----
  static Future<List<dynamic>> getComplaints() async {
    try {
      final headers = await getHeaders();
      final response = await http.get(
        Uri.parse('$BASE_URL/api/complaints/'),
        headers: headers,
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  // ---- CONTACT DETAILS ----
  static Future<List<dynamic>> getContacts() async {
    try {
      final headers = await getHeaders();
      final response = await http.get(
        Uri.parse('$BASE_URL/api/contacts/'),
        headers: headers,
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  // ---- USER PROFILE ----
  static Future<Map<String, dynamic>?> getProfile() async {
    try {
      final headers = await getHeaders();
      final response = await http.get(
        Uri.parse('$BASE_URL/api/user/profile/'),
        headers: headers,
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  static Future<Map<String, dynamic>> updateProfile(String phone) async {
    try {
      final headers = await getHeaders();
      final response = await http.post(
        Uri.parse('$BASE_URL/api/user/profile/'),
        headers: headers,
        body: jsonEncode({'phone': phone}),
      );
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      }
      final err = jsonDecode(response.body);
      return {'success': false, 'message': err['error'] ?? 'Failed to update profile'};
    } catch (e) {
      return {'success': false, 'message': 'Connection error'};
    }
  }

  static Future<Map<String, dynamic>> updateProfilePicture(String filepath) async {
    try {
      final token = await getToken();
      var request = http.MultipartRequest(
          'POST', Uri.parse('$BASE_URL/api/user/profile/'));
      
      if (token != null) {
        request.headers['Authorization'] = 'Token $token';
      }

      request.files.add(await http.MultipartFile.fromPath(
        'profile_picture',
        filepath,
      ));

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      }
      final err = jsonDecode(response.body);
      return {'success': false, 'message': err['error'] ?? 'Failed to update profile picture'};
    } catch (e) {
      return {'success': false, 'message': 'Connection error'};
    }
  }
}
