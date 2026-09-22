import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'package:intl/intl.dart';

class AnimalAlertsScreen extends StatefulWidget {
  const AnimalAlertsScreen({super.key});

  @override
  State<AnimalAlertsScreen> createState() => _AnimalAlertsScreenState();
}

class _AnimalAlertsScreenState extends State<AnimalAlertsScreen> {
  List<dynamic> _alerts = [];
  bool _isLoading = true;
  String? _error;
  DateTime? _selectedDate;

  List<dynamic> get _filteredAlerts {
    if (_selectedDate == null) return _alerts;
    
    // API returns dates like "19 Mar 2026, 05:10 PM"
    final targetDateStr = DateFormat('dd MMM yyyy').format(_selectedDate!);
    
    return _alerts.where((alert) {
      final dateStr = alert['detected_at'] ?? alert['created_at'];
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

  @override
  void initState() {
    super.initState();
    _fetchAlerts();
  }

  Future<void> _fetchAlerts() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final data = await ApiService.getAnimalAlerts();
      setState(() { _alerts = data; _isLoading = false; });
    } catch (e) {
      setState(() { _error = 'Failed to load animal alerts. Please try again.'; _isLoading = false; });
    }
  }

  Color _statusColor(String status) {
    switch (status.toUpperCase()) {
      case 'ACTIVE': return Colors.red;
      case 'RESOLVED': return Colors.green;
      default: return Colors.orange;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Animal Alerts', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.brown,
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
          IconButton(
              icon: const Icon(Icons.refresh, color: Colors.white),
              onPressed: _fetchAlerts),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.brown))
          : _error != null
              ? _buildError()
              : _filteredAlerts.isEmpty
                  ? _buildEmpty()
                  : RefreshIndicator(
                      onRefresh: _fetchAlerts,
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _filteredAlerts.length,
                        itemBuilder: (ctx, i) => _buildCard(_filteredAlerts[i]),
                      ),
                    ),
    );
  }

  Widget _buildCard(dynamic alert) {
    final status = alert['status'] ?? 'UNKNOWN';
    final statusColor = _statusColor(status);
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(14),
          border: Border(left: BorderSide(color: statusColor, width: 5)),
        ),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.pets, color: Colors.brown, size: 22),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      alert['animal_type'] ?? alert['animal'] ?? 'Unknown Animal',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: statusColor.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(status,
                        style: TextStyle(color: statusColor, fontWeight: FontWeight.bold, fontSize: 12)),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              _infoRow(Icons.location_on_outlined, 'Location', alert['location'] ?? '—'),
              const SizedBox(height: 4),
              _infoRow(Icons.access_time, 'Date & Time', alert['detected_at'] ?? alert['created_at'] ?? '—'),
              const SizedBox(height: 4),
              _infoRow(Icons.account_tree_outlined, 'Division', alert['division'] ?? alert['station'] ?? '—'),
            ],
          ),
        ),
      ),
    );
  }

  Widget _infoRow(IconData icon, String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 15, color: Colors.grey),
        const SizedBox(width: 6),
        Text('$label: ', style: const TextStyle(color: Colors.grey, fontSize: 12)),
        Expanded(child: Text(value, style: const TextStyle(fontSize: 12))),
      ],
    );
  }

  Widget _buildEmpty() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.pets, size: 80, color: Colors.brown.shade200),
          const SizedBox(height: 16),
          const Text('No Animal Alerts', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const Text('No animal detections at this time.', style: TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }

  Widget _buildError() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 60, color: Colors.red),
          const SizedBox(height: 16),
          Text(_error!, textAlign: TextAlign.center),
          const SizedBox(height: 16),
          ElevatedButton(onPressed: _fetchAlerts, child: const Text('Retry')),
        ],
      ),
    );
  }
}
