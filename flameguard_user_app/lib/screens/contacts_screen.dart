import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_service.dart';

class ContactsScreen extends StatefulWidget {
  const ContactsScreen({super.key});

  @override
  State<ContactsScreen> createState() => _ContactsScreenState();
}

class _ContactsScreenState extends State<ContactsScreen> {
  List<dynamic> _contacts = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchContacts();
  }

  Future<void> _fetchContacts() async {
    setState(() => _isLoading = true);
    final data = await ApiService.getContacts();
    // If backend has no contacts, show hardcoded emergency numbers
    if (data.isEmpty) {
      setState(() {
        _contacts = [
          {'name': 'Forest Fire Emergency', 'phone': '1926', 'type': 'emergency'},
          {'name': 'Forest Department Helpline', 'phone': '1800-180-1515', 'type': 'helpline'},
          {'name': 'Police', 'phone': '100', 'type': 'emergency'},
          {'name': 'Ambulance', 'phone': '108', 'type': 'emergency'},
        ];
        _isLoading = false;
      });
    } else {
      setState(() { _contacts = data; _isLoading = false; });
    }
  }

  Color _typeColor(String? type) {
    switch ((type ?? '').toLowerCase()) {
      case 'emergency': return Colors.red;
      case 'helpline': return Colors.blue;
      default: return Colors.purple;
    }
  }

  void _copyNumber(String phone) {
    Clipboard.setData(ClipboardData(text: phone));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Copied: $phone'),
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Contact Details', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.purple,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.purple))
          : Column(
              children: [
                // Emergency Banner
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  color: Colors.red.shade50,
                  child: Row(
                    children: [
                      const Icon(Icons.emergency, color: Colors.red, size: 22),
                      const SizedBox(width: 10),
                      const Expanded(
                        child: Text(
                          'In case of fire or animal attack, call emergency immediately!',
                          style: TextStyle(color: Colors.red, fontWeight: FontWeight.w600, fontSize: 13),
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: RefreshIndicator(
                    onRefresh: _fetchContacts,
                    child: ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _contacts.length,
                      itemBuilder: (ctx, i) => _buildContactCard(_contacts[i]),
                    ),
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildContactCard(dynamic contact) {
    final type = contact['type'] ?? 'station';
    final color = _typeColor(type);
    final phone = contact['phone'] ?? contact['contact_number'] ?? '—';
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity(0.12),
                shape: BoxShape.circle,
              ),
              child: Icon(
                type == 'emergency' ? Icons.emergency : Icons.contact_phone,
                color: color,
                size: 26,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    contact['name'] ?? contact['station_name'] ?? 'Contact',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  if (contact['division'] != null) ...[
                    const SizedBox(height: 2),
                    Text(contact['division'],
                        style: const TextStyle(color: Colors.grey, fontSize: 12)),
                  ],
                  const SizedBox(height: 4),
                  Text(phone,
                      style: TextStyle(
                          color: color, fontWeight: FontWeight.bold, fontSize: 16)),
                ],
              ),
            ),
            Column(
              children: [
                IconButton(
                  icon: Icon(Icons.copy, color: color, size: 20),
                  onPressed: () => _copyNumber(phone),
                  tooltip: 'Copy number',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
