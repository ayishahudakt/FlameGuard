import 'package:flutter/material.dart';
import '../services/api_service.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  List<dynamic> _notifications = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchNotifications();
  }

  Future<void> _fetchNotifications() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final data = await ApiService.getNotifications();
      setState(() { _notifications = data; _isLoading = false; });
    } catch (e) {
      setState(() { _error = 'Failed to load notifications.'; _isLoading = false; });
    }
  }

  IconData _notifIcon(String? type) {
    switch ((type ?? '').toLowerCase()) {
      case 'fire': return Icons.local_fire_department;
      case 'animal': return Icons.pets;
      default: return Icons.notifications_outlined;
    }
  }

  Color _notifColor(String? type) {
    switch ((type ?? '').toLowerCase()) {
      case 'fire': return Colors.deepOrange;
      case 'animal': return Colors.brown;
      default: return Colors.teal;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.teal,
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          IconButton(
              icon: const Icon(Icons.refresh, color: Colors.white),
              onPressed: _fetchNotifications),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.teal))
          : _error != null
              ? _buildError()
              : _notifications.isEmpty
                  ? _buildEmpty()
                  : RefreshIndicator(
                      onRefresh: _fetchNotifications,
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _notifications.length,
                        itemBuilder: (ctx, i) => _buildNotifCard(_notifications[i]),
                      ),
                    ),
    );
  }

  Widget _buildNotifCard(dynamic notif) {
    final type = notif['type'] ?? notif['notification_type'] ?? '';
    final color = _notifColor(type);
    final icon = _notifIcon(type);
    final isRead = notif['is_read'] == true;
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      elevation: isRead ? 1 : 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      color: isRead ? null : color.withOpacity(0.04),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: color.withOpacity(0.15),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: color, size: 22),
        ),
        title: Text(
          notif['title'] ?? notif['message'] ?? 'Notification',
          style: TextStyle(
            fontWeight: isRead ? FontWeight.normal : FontWeight.bold,
            fontSize: 14,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (notif['body'] != null && notif['body'] != notif['title'])
              Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Text(notif['body'],
                    style: const TextStyle(fontSize: 12, color: Colors.black87)),
              ),
            const SizedBox(height: 4),
            Text(
              notif['created_at'] ?? notif['timestamp'] ?? '',
              style: const TextStyle(fontSize: 11, color: Colors.grey),
            ),
          ],
        ),
        trailing: !isRead
            ? Container(
                width: 10, height: 10,
                decoration: BoxDecoration(color: color, shape: BoxShape.circle))
            : null,
      ),
    );
  }

  Widget _buildEmpty() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.notifications_off_outlined, size: 80, color: Colors.grey),
          SizedBox(height: 16),
          Text('No Notifications Yet', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          SizedBox(height: 8),
          Text('You are all caught up!', style: TextStyle(color: Colors.grey)),
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
          ElevatedButton(onPressed: _fetchNotifications, child: const Text('Retry')),
        ],
      ),
    );
  }
}
