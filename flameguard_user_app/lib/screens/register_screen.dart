import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'login_screen.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _phoneController = TextEditingController();

  bool _isLoading = false;
  bool _obscurePassword = true;
  String? _errorMessage;

  // Division state
  List<Map<String, dynamic>> _divisions = [];
  int? _selectedDivisionId;
  bool _divisionsLoading = true;

  @override
  void initState() {
    super.initState();
    _loadDivisions();
  }

  Future<void> _loadDivisions() async {
    final result = await ApiService.getDivisions();
    if (mounted) {
      setState(() {
        _divisions = result;
        _divisionsLoading = false;
      });
    }
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final result = await ApiService.register({
      'username': _usernameController.text.trim(),
      'email': _emailController.text.trim(),
      'password': _passwordController.text,
      'phone': _phoneController.text.trim(),
      'division_id': _selectedDivisionId.toString(),
    });

    setState(() => _isLoading = false);

    if (result['success']) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Registration successful! Please login.'),
          backgroundColor: Colors.green,
        ),
      );
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const LoginScreen()),
      );
    } else {
      setState(() => _errorMessage = result['message']);
    }
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    bool obscure = false,
    TextInputType keyboardType = TextInputType.text,
    String? Function(String?)? validator,
    Widget? suffixIcon,
  }) {
    return TextFormField(
      controller: controller,
      obscureText: obscure,
      keyboardType: keyboardType,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon),
        suffixIcon: suffixIcon,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      ),
      validator: validator,
    );
  }

  Widget _buildDivisionDropdown() {
    if (!_divisionsLoading && _divisions.isEmpty) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
            decoration: BoxDecoration(
              border: Border.all(color: Colors.red.shade300),
              borderRadius: BorderRadius.circular(12),
              color: Colors.red.shade50,
            ),
            child: Row(
              children: [
                const Icon(Icons.error_outline, color: Colors.red),
                const SizedBox(width: 8),
                const Expanded(
                  child: Text('Failed to load divisions. Check connection.',
                      style: TextStyle(color: Colors.red)),
                ),
                TextButton(
                  onPressed: () {
                    setState(() {
                      _divisionsLoading = true;
                    });
                    _loadDivisions();
                  },
                  child: const Text('Retry'),
                ),
              ],
            ),
          ),
        ],
      );
    }

    return DropdownButtonFormField<int>(
      value: _selectedDivisionId,
      decoration: InputDecoration(
        labelText: 'Select Division',
        prefixIcon: const Icon(Icons.forest_outlined),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
      ),
      hint: _divisionsLoading
          ? const Row(
              children: [
                SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
                SizedBox(width: 8),
                Text('Loading divisions...'),
              ],
            )
          : const Text('Select Division'),
      items: _divisions.map((division) {
        return DropdownMenuItem<int>(
          value: division['id'] as int,
          child: Text(division['name'] as String),
        );
      }).toList(),
      onChanged: _divisionsLoading
          ? null
          : (value) {
              setState(() => _selectedDivisionId = value);
            },
      validator: (value) {
        if (value == null) return 'Please select a division';
        return null;
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFFBF360C), Color(0xFFE65100), Color(0xFFFF8F00)],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                const SizedBox(height: 20),
                Row(
                  children: [
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.arrow_back, color: Colors.white),
                    ),
                    const Text(
                      'Create Account',
                      style: TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                          color: Colors.white),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Center(
                  child: Icon(Icons.local_fire_department,
                      size: 50, color: Colors.white),
                ),
                const SizedBox(height: 20),
                Card(
                  elevation: 8,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20)),
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        children: [
                          if (_errorMessage != null)
                            Container(
                              padding: const EdgeInsets.all(12),
                              margin: const EdgeInsets.only(bottom: 16),
                              decoration: BoxDecoration(
                                color: Colors.red.shade50,
                                borderRadius: BorderRadius.circular(10),
                                border:
                                    Border.all(color: Colors.red.shade200),
                              ),
                              child: Row(
                                children: [
                                  const Icon(Icons.error_outline,
                                      color: Colors.red, size: 20),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(_errorMessage!,
                                        style: const TextStyle(
                                            color: Colors.red)),
                                  ),
                                ],
                              ),
                            ),
                          _buildTextField(
                            controller: _usernameController,
                            label: 'Username',
                            icon: Icons.person_outline,
                            validator: (v) {
                              if (v == null || v.isEmpty) return 'Username is required';
                              if (v.length > 15) return 'Username cannot exceed 15 characters';
                              if (!RegExp(r'^[a-zA-Z0-9]+$').hasMatch(v)) return 'Username can only contain letters and numbers';
                              int numberCount = RegExp(r'[0-9]').allMatches(v).length;
                              if (numberCount > 4) return 'Username cannot have more than 4 numbers';
                              return null;
                            },
                          ),
                          const SizedBox(height: 14),
                          _buildTextField(
                            controller: _emailController,
                            label: 'Email Address',
                            icon: Icons.email_outlined,
                            keyboardType: TextInputType.emailAddress,
                            validator: (v) {
                              if (v == null || v.isEmpty) return 'Email is required';
                              // This regex checks for a standard email format ending in .com
                              if (!RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.com$').hasMatch(v)) {
                                return 'Enter a valid email ending with .com';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 14),
                          _buildTextField(
                            controller: _phoneController,
                            label: 'Phone Number',
                            icon: Icons.phone_outlined,
                            keyboardType: TextInputType.phone,
                            validator: (v) {
                              if (v == null || v.isEmpty) return 'Phone number is required';
                              // This regex checks if the phone number is exactly 10 digits
                              if (!RegExp(r'^\d{10}$').hasMatch(v)) return 'Phone number must be exactly 10 digits';
                              return null;
                            },
                          ),
                          const SizedBox(height: 14),
                          // ── Division Dropdown ──
                          _buildDivisionDropdown(),
                          const SizedBox(height: 14),
                          _buildTextField(
                            controller: _passwordController,
                            label: 'Password',
                            icon: Icons.lock_outline,
                            obscure: _obscurePassword,
                            suffixIcon: IconButton(
                              icon: Icon(_obscurePassword
                                  ? Icons.visibility_off
                                  : Icons.visibility),
                              onPressed: () => setState(
                                  () => _obscurePassword = !_obscurePassword),
                            ),
                            validator: (v) {
                              if (v == null || v.isEmpty) return 'Password is required';
                              if (v.length < 8) return 'Password must be at least 8 characters';
                              if (!RegExp(r'[A-Z]').hasMatch(v)) return 'Must contain at least one uppercase letter';
                              if (!RegExp(r'[a-z]').hasMatch(v)) return 'Must contain at least one lowercase letter';
                              if (!RegExp(r'[0-9]').hasMatch(v)) return 'Must contain at least one number';
                              if (!RegExp(r'[!@#\$&*~%]').hasMatch(v)) return 'Must contain at least one special character';
                              return null;
                            },
                          ),
                          const SizedBox(height: 14),
                          _buildTextField(
                            controller: _confirmPasswordController,
                            label: 'Confirm Password',
                            icon: Icons.lock_outline,
                            obscure: true,
                            validator: (v) {
                              if (v != _passwordController.text) {
                                return 'Passwords do not match';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 24),
                          SizedBox(
                            width: double.infinity,
                            height: 50,
                            child: ElevatedButton(
                              onPressed: _isLoading ? null : _register,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFFE65100),
                                foregroundColor: Colors.white,
                                shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12)),
                              ),
                              child: _isLoading
                                  ? const SizedBox(
                                      width: 24,
                                      height: 24,
                                      child: CircularProgressIndicator(
                                          color: Colors.white, strokeWidth: 2),
                                    )
                                  : const Text('Create Account',
                                      style: TextStyle(
                                          fontSize: 16,
                                          fontWeight: FontWeight.bold)),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text(
                    'Already have an account? Login',
                    style: TextStyle(color: Colors.white, fontSize: 15),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
