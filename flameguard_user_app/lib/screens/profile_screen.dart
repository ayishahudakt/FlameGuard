import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _profileData;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchProfile();
  }

  Future<void> _fetchProfile() async {
    final data = await ApiService.getProfile();
    setState(() {
      _profileData = data;
      _isLoading = false;
    });
  }

  Future<void> _pickImage() async {
    try {
      final picker = ImagePicker();
      final pickedFile = await picker.pickImage(source: ImageSource.gallery);

      if (pickedFile != null) {
        setState(() => _isLoading = true);
        
        final response = await ApiService.updateProfilePicture(pickedFile.path);
        
        if (response['success'] == true && mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Profile picture updated successfully!')),
          );
          _fetchProfile(); // Refresh profile to get the new image URL
        } else if (mounted) {
          setState(() => _isLoading = false);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(response['message'] ?? 'Failed to update picture')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
                'Could not open gallery. Please restart the app fully! ($e)'),
            duration: const Duration(seconds: 4),
          ),
        );
      }
    }
  }

  Widget _buildProfileItem(IconData icon, String title, String value, {VoidCallback? onEdit}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12.0),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFE65100).withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: const Color(0xFFE65100), size: 28),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade600,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value.isNotEmpty ? value : 'N/A',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          if (onEdit != null)
            IconButton(
              icon: const Icon(Icons.edit, color: Color(0xFFE65100)),
              onPressed: onEdit,
            ),
        ],
      ),
    );
  }

  Future<void> _editPhoneDialog() async {
    final TextEditingController phoneController =
        TextEditingController(text: _profileData!['phone']);
    bool localLoading = false;

    await showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setStateDialog) {
          return AlertDialog(
            title: const Text('Edit Phone Number'),
            content: localLoading
                ? const SizedBox(
                    height: 50,
                    child: Center(child: CircularProgressIndicator()),
                  )
                : TextField(
                    controller: phoneController,
                    keyboardType: TextInputType.phone,
                    decoration: const InputDecoration(
                      labelText: 'Phone Number',
                      hintText: 'Enter new phone number',
                      border: OutlineInputBorder(),
                    ),
                  ),
            actions: [
              if (!localLoading)
                TextButton(
                  onPressed: () => Navigator.pop(ctx),
                  child: const Text('Cancel'),
                ),
              if (!localLoading)
                ElevatedButton(
                  onPressed: () async {
                    final newPhone = phoneController.text.trim();
                    if (newPhone.isEmpty) {
                      ScaffoldMessenger.of(ctx).showSnackBar(
                        const SnackBar(content: Text('Phone number cannot be empty')),
                      );
                      return;
                    }

                    setStateDialog(() => localLoading = true);
                    final response = await ApiService.updateProfile(newPhone);
                    setStateDialog(() => localLoading = false);

                    if (response['success'] == true) {
                      Navigator.pop(ctx);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Phone number updated successfully!')),
                      );
                      _fetchProfile();
                    } else {
                      ScaffoldMessenger.of(ctx).showSnackBar(
                        SnackBar(content: Text(response['message'] ?? 'Error updating')),
                      );
                    }
                  },
                  style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFE65100), foregroundColor: Colors.white),
                  child: const Text('Save'),
                ),
            ],
          );
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('My Profile'),
          backgroundColor: const Color(0xFFE65100),
          foregroundColor: Colors.white,
        ),
        body: const Center(
          child: CircularProgressIndicator(color: Color(0xFFE65100)),
        ),
      );
    }

    if (_profileData == null) {
      return Scaffold(
         appBar: AppBar(
          title: const Text('My Profile'),
          backgroundColor: const Color(0xFFE65100),
          foregroundColor: Colors.white,
        ),
        body: const Center(
          child: Text('Failed to load profile details.'),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Profile'),
        backgroundColor: const Color(0xFFE65100),
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.only(bottom: 30, top: 20),
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: [Color(0xFFE65100), Color(0xFFBF360C)],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
                borderRadius: BorderRadius.only(
                  bottomLeft: Radius.circular(40),
                  bottomRight: Radius.circular(40),
                ),
              ),
              child: Column(
                children: [
                  GestureDetector(
                    onTap: _pickImage,
                    child: Stack(
                      alignment: Alignment.bottomRight,
                      children: [
                        CircleAvatar(
                          radius: 50,
                          backgroundColor: Colors.white24,
                          backgroundImage: _profileData!['profile_picture'] != null
                              ? NetworkImage(_profileData!['profile_picture'])
                              : null,
                          child: _profileData!['profile_picture'] == null
                              ? const Icon(Icons.person, size: 60, color: Colors.white)
                              : null,
                        ),
                        Container(
                          padding: const EdgeInsets.all(4),
                          decoration: const BoxDecoration(
                            color: Colors.white,
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            Icons.camera_alt,
                            size: 20,
                            color: Color(0xFFE65100),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    _profileData!['username'] ?? 'User',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.white24,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      _profileData!['user_type'] ?? 'USER',
                      style: const TextStyle(
                        fontSize: 14,
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Card(
                elevation: 4,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    children: [
                      _buildProfileItem(Icons.email_outlined, 'Email', _profileData!['email'] ?? ''),
                      const Divider(height: 24),
                      _buildProfileItem(Icons.phone_outlined, 'Phone', _profileData!['phone'] ?? '', onEdit: _editPhoneDialog),
                      const Divider(height: 24),
                      _buildProfileItem(Icons.forest_outlined, 'Division', _profileData!['division'] ?? ''),
                      if (_profileData!['date_joined'] != null && _profileData!['date_joined'].isNotEmpty) ...[
                        const Divider(height: 24),
                        _buildProfileItem(Icons.calendar_today_outlined, 'Joined', _profileData!['date_joined']),
                      ]
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }
}
