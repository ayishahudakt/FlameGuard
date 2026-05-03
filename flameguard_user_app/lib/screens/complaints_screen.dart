import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'package:intl/intl.dart';

class ComplaintsScreen extends StatefulWidget {
  const ComplaintsScreen({super.key});

  @override
  State<ComplaintsScreen> createState() => _ComplaintsScreenState();
}

class _ComplaintsScreenState extends State<ComplaintsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<dynamic> _complaints = [];
  bool _isLoading = true;
  DateTime? _selectedDate;

  List<dynamic> get _filteredComplaints {
    if (_selectedDate == null) return _complaints;
    
    // API returns dates like "19 Mar 2026, 05:10 PM"
    final targetDateStr = DateFormat('dd MMM yyyy').format(_selectedDate!);
    
    return _complaints.where((complaint) {
      final dateStr = complaint['created_at'];
      if (dateStr == null) return false;
      return dateStr.toString().startsWith(targetDateStr);
    }).toList();
  }

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate ?? DateTime.now(),
      firstDate: DateTime(2000),
      lastDate: DateTime(2101),
    );
    if (picked != null && picked != _selectedDate) {
      setState(() {
        _selectedDate = picked;
      });
    }
  }

  // Form fields
  final _formKey = GlobalKey<FormState>();
  final _subjectController = TextEditingController();
  final _messageController = TextEditingController();
  bool _isSending = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _fetchComplaints();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _subjectController.dispose();
    _messageController.dispose();
    super.dispose();
  }

  Future<void> _fetchComplaints() async {
    setState(() => _isLoading = true);
    final data = await ApiService.getComplaints();
    setState(() { _complaints = data; _isLoading = false; });
  }

  Future<void> _sendComplaint() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isSending = true);
    final result = await ApiService.sendComplaint(
      _subjectController.text.trim(),
      _messageController.text.trim(),
    );
    setState(() => _isSending = false);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(result['success']
            ? 'Complaint sent successfully!'
            : result['message'] ?? 'Failed to send complaint'),
        backgroundColor: result['success'] ? Colors.green : Colors.red,
      ),
    );
    if (result['success']) {
      _subjectController.clear();
      _messageController.clear();
      _fetchComplaints();
      _tabController.animateTo(1); // Switch to 'My Complaints' tab
    }
  }

  Future<void> _deleteComplaint(int id) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.delete_outline, color: Colors.red),
            SizedBox(width: 8),
            Text('Delete Complaint'),
          ],
        ),
        content: const Text('Are you sure you want to delete this complaint? This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      final result = await ApiService.deleteComplaint(id);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result['success'] ? 'Complaint deleted successfully!' : result['message'] ?? 'Error deleting'),
          backgroundColor: result['success'] ? Colors.green : Colors.red,
        ),
      );
      if (result['success']) {
        _fetchComplaints();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Complaints', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFFE65100),
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          if (_selectedDate != null)
            IconButton(
              icon: const Icon(Icons.clear, color: Colors.white),
              onPressed: () {
                setState(() {
                  _selectedDate = null;
                });
              },
            ),
          IconButton(
            icon: const Icon(Icons.filter_list, color: Colors.white),
            onPressed: () => _selectDate(context),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          tabs: const [
            Tab(icon: Icon(Icons.add_comment_outlined), text: 'Send Complaint'),
            Tab(icon: Icon(Icons.list_alt), text: 'My Complaints'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [_buildSendForm(), _buildComplaintsList()],
      ),
    );
  }

  Widget _buildSendForm() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Send Complaint to Forest Officer',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 6),
            const Text('Your complaint will be sent to the relevant officer.',
                style: TextStyle(color: Colors.grey, fontSize: 13)),
            const SizedBox(height: 20),
            TextFormField(
              controller: _subjectController,
              decoration: InputDecoration(
                labelText: 'Subject',
                prefixIcon: const Icon(Icons.subject, color: Color(0xFFE65100)),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: Color(0xFFE65100), width: 2),
                ),
              ),
              validator: (v) => v == null || v.isEmpty ? 'Subject is required' : null,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _messageController,
              maxLines: 5,
              decoration: InputDecoration(
                labelText: 'Message',
                alignLabelWithHint: true,
                prefixIcon: const Icon(Icons.message_outlined, color: Color(0xFFE65100)),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: Color(0xFFE65100), width: 2),
                ),
              ),
              validator: (v) => v == null || v.isEmpty ? 'Message is required' : null,
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton.icon(
                onPressed: _isSending ? null : _sendComplaint,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFE65100),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  elevation: 4,
                ),
                icon: _isSending
                    ? const SizedBox(
                        width: 20, height: 20,
                        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                    : const Icon(Icons.send),
                label: Text(_isSending ? 'Sending...' : 'Send Complaint',
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _statusBadge(String status) {
    switch (status.toUpperCase()) {
      case 'IN_PROGRESS':
        return _badge('In Progress', Colors.blue);
      case 'RESOLVED':
        return _badge('Resolved', Colors.teal);
      case 'PENDING':
      default:
        return _badge('Pending', Colors.orange);
    }
  }

  Widget _badge(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.4)),
      ),
      child: Text(
        label,
        style: TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.bold),
      ),
    );
  }

  Widget _buildComplaintsList() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFFE65100)));
    }
    if (_filteredComplaints.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.inbox_outlined, size: 70, color: Colors.grey),
            SizedBox(height: 12),
            Text('No complaints match given criteria.',
                style: TextStyle(fontSize: 16, color: Colors.grey)),
          ],
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: _fetchComplaints,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _filteredComplaints.length,
        itemBuilder: (ctx, i) {
          final c = _filteredComplaints[i];
          final hasReply = c['reply'] != null && c['reply'].toString().isNotEmpty;
          final status = c['status']?.toString() ?? 'PENDING';
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            elevation: 3,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.report_problem_outlined, color: Color(0xFFE65100), size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(c['subject'] ?? '—',
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                      ),
                      _statusBadge(status),
                      if (!hasReply) ...[
                        const SizedBox(width: 4),
                        IconButton(
                          icon: const Icon(Icons.delete_outline, color: Colors.grey, size: 20),
                          padding: EdgeInsets.zero,
                          constraints: const BoxConstraints(),
                          onPressed: () => _deleteComplaint(c['id']),
                          tooltip: 'Delete Complaint',
                        ),
                      ],
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    c['created_at'] ?? '',
                    style: const TextStyle(fontSize: 11, color: Colors.grey),
                  ),
                  const SizedBox(height: 8),
                  Text(c['message'] ?? '—', style: const TextStyle(color: Colors.black87, fontSize: 13)),
                  if (hasReply) ...[
                    const Divider(height: 20),
                    Row(
                      children: [
                        const Icon(Icons.reply, color: Colors.green, size: 16),
                        const SizedBox(width: 6),
                        const Text('Officer Reply:',
                            style: TextStyle(fontWeight: FontWeight.bold, color: Colors.green, fontSize: 13)),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(c['reply'],
                        style: TextStyle(color: Colors.green.shade700, fontSize: 13)),
                  ],
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
