import 'package:flutter/material.dart';
import '../services/api_service.dart';

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

  // Form fields
  final _formKey = GlobalKey<FormState>();
  final _subjectController = TextEditingController();
  final _messageController = TextEditingController();
  String _selectedDivision = 'Division 1';
  bool _isSending = false;

  final List<String> _divisions = [
    'Division 1', 'Division 2', 'Division 3', 'Division 4', 'Division 5'
  ];

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
      _selectedDivision,
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Complaints', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.indigo,
        iconTheme: const IconThemeData(color: Colors.white),
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
            // Division dropdown
            DropdownButtonFormField<String>(
              value: _selectedDivision,
              decoration: InputDecoration(
                labelText: 'Select Division',
                prefixIcon: const Icon(Icons.account_tree_outlined),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
              items: _divisions.map((d) => DropdownMenuItem(value: d, child: Text(d))).toList(),
              onChanged: (v) => setState(() => _selectedDivision = v!),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _subjectController,
              decoration: InputDecoration(
                labelText: 'Subject',
                prefixIcon: const Icon(Icons.subject),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
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
                prefixIcon: const Icon(Icons.message_outlined),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
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
                  backgroundColor: Colors.indigo,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
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

  Widget _buildComplaintsList() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator(color: Colors.indigo));
    }
    if (_complaints.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.inbox_outlined, size: 70, color: Colors.grey),
            SizedBox(height: 12),
            Text('No complaints submitted yet.',
                style: TextStyle(fontSize: 16, color: Colors.grey)),
          ],
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: _fetchComplaints,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _complaints.length,
        itemBuilder: (ctx, i) {
          final c = _complaints[i];
          final hasReply = c['reply'] != null && c['reply'].toString().isNotEmpty;
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
                      const Icon(Icons.report_problem_outlined, color: Colors.indigo, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(c['subject'] ?? '—',
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: hasReply ? Colors.green.shade50 : Colors.orange.shade50,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          hasReply ? 'Replied' : 'Pending',
                          style: TextStyle(
                            fontSize: 11,
                            color: hasReply ? Colors.green : Colors.orange,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
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
