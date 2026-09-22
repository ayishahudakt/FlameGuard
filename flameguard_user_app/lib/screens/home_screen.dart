import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'login_screen.dart';
import 'fire_alerts_screen.dart';
import 'animal_alerts_screen.dart';
import 'complaints_screen.dart';
import 'notifications_screen.dart';
import 'animals_screen.dart';
import 'contacts_screen.dart';
import 'profile_screen.dart';
import '../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;
  String _username = 'User';
  String? _profilePicture;

  @override
  void initState() {
    super.initState();
    _loadUsername();
    _fetchProfile();
  }

  Future<void> _fetchProfile() async {
    final data = await ApiService.getProfile();
    if (data != null && mounted) {
      setState(() {
        _profilePicture = data['profile_picture'];
      });
    }
  }

  Future<void> _loadUsername() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() => _username = prefs.getString('username') ?? 'User');
  }

  Future<void> _logout() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Cancel')),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Logout', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
    if (confirm == true) {
      await ApiService.logout();
      if (!mounted) return;
      Navigator.pushReplacement(
          context, MaterialPageRoute(builder: (_) => const LoginScreen()));
    }
  }

  // Dashboard grid items
  final List<_DashboardItem> _dashboardItems = [
    _DashboardItem(
      title: 'Fire Alerts',
      icon: Icons.local_fire_department,
      color: Colors.deepOrange,
      description: 'View active fire alerts',
    ),
    _DashboardItem(
      title: 'Animal Alerts',
      icon: Icons.pets,
      color: Colors.brown,
      description: 'View animal detections',
    ),
    _DashboardItem(
      title: 'Complaints',
      icon: Icons.report_problem_outlined,
      color: Colors.indigo,
      description: 'Send & view complaints',
    ),
    _DashboardItem(
      title: 'Notifications',
      icon: Icons.notifications_outlined,
      color: Colors.teal,
      description: 'View all notifications',
    ),
    _DashboardItem(
      title: 'Animals',
      icon: Icons.eco_outlined,
      color: Colors.green,
      description: 'Forest animals info',
    ),
    _DashboardItem(
      title: 'Contacts',
      icon: Icons.contact_phone_outlined,
      color: Colors.purple,
      description: 'Emergency contacts',
    ),
  ];

  void _onItemTapped(int index) {
    setState(() => _selectedIndex = index);
  }

  void _navigateToDashboardItem(int index) {
    final screens = [
      const FireAlertsScreen(),
      const AnimalAlertsScreen(),
      const ComplaintsScreen(),
      const NotificationsScreen(),
      const AnimalsScreen(),
      const ContactsScreen(),
    ];
    Navigator.push(
        context, MaterialPageRoute(builder: (_) => screens[index]));
  }

  Widget _buildHomeDashboard() {
    return CustomScrollView(
      slivers: [
        SliverToBoxAdapter(
          child: Container(
            margin: const EdgeInsets.only(bottom: 30),
            child: Stack(
              clipBehavior: Clip.none,
              children: [
                // Header Background
                Container(
                  height: 165,
                  width: double.infinity,
                  padding: const EdgeInsets.fromLTRB(24, 20, 24, 20),
                  decoration: const BoxDecoration(
                    gradient: LinearGradient(
                      colors: [Color(0xFFE65100), Color(0xFFFF9800)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.only(
                      bottomLeft: Radius.circular(36),
                      bottomRight: Radius.circular(36),
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Welcome back,',
                            style: TextStyle(
                                color: Colors.white70,
                                fontSize: 16,
                                fontWeight: FontWeight.w500),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _username,
                            style: const TextStyle(
                                color: Colors.white,
                                fontSize: 28,
                                fontWeight: FontWeight.bold,
                                letterSpacing: 0.5),
                          ),
                        ],
                      ),
                      GestureDetector(
                        onTap: () async {
                          await Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => const ProfileScreen()),
                          );
                          _fetchProfile(); // Refresh when coming back
                        },
                        child: Container(
                          padding: const EdgeInsets.all(3),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            shape: BoxShape.circle,
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.1),
                                blurRadius: 8,
                                offset: const Offset(0, 4),
                              ),
                            ],
                          ),
                          child: CircleAvatar(
                            backgroundColor: Colors.orange.shade100,
                            radius: 26,
                            backgroundImage: _profilePicture != null 
                                ? NetworkImage(_profilePicture!) 
                                : null,
                            child: _profilePicture == null 
                                ? const Icon(Icons.person, color: Colors.orange, size: 30)
                                : null,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                // Overlapping Floating Card
                Positioned(
                  bottom: -25,
                  left: 20,
                  right: 20,
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFFE65100).withOpacity(0.15),
                          blurRadius: 15,
                          offset: const Offset(0, 8),
                        ),
                      ],
                    ),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: const Color(0xFFE65100).withOpacity(0.1),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            Icons.security_outlined,
                            color: Color(0xFFE65100),
                            size: 28,
                          ),
                        ),
                        const SizedBox(width: 16),
                        const Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'FLAME Guard',
                              style: TextStyle(
                                color: Colors.black87,
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            SizedBox(height: 2),
                            Text(
                              'Active Protection System',
                              style: TextStyle(
                                color: Colors.black54,
                                fontSize: 13,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SliverToBoxAdapter(child: SizedBox(height: 10)),
        const SliverToBoxAdapter(
          child: Padding(
            padding: EdgeInsets.symmetric(horizontal: 20),
            child: Text(
              'Quick Access',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ),
        ),
        const SliverToBoxAdapter(child: SizedBox(height: 12)),
        SliverPadding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          sliver: SliverGrid(
            delegate: SliverChildBuilderDelegate(
              (ctx, index) {
                final item = _dashboardItems[index];
                return GestureDetector(
                  onTap: () => _navigateToDashboardItem(index),
                  child: Card(
                    elevation: 4,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16)),
                    child: Container(
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(16),
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [
                            item.color.withOpacity(0.1),
                            item.color.withOpacity(0.05),
                          ],
                        ),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Container(
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: item.color.withOpacity(0.15),
                              shape: BoxShape.circle,
                            ),
                            child: Icon(item.icon,
                                color: item.color, size: 32),
                          ),
                          const SizedBox(height: 10),
                          Text(
                            item.title,
                            style: TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 13,
                                color: item.color),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            item.description,
                            style: TextStyle(
                                fontSize: 10,
                                color: Colors.grey.shade600),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
              childCount: _dashboardItems.length,
            ),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              childAspectRatio: 1.1,
            ),
          ),
        ),
        const SliverToBoxAdapter(child: SizedBox(height: 20)),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final List<Widget> pages = [
      _buildHomeDashboard(),
      const FireAlertsScreen(),
      const AnimalAlertsScreen(),
      const ComplaintsScreen(),
      const NotificationsScreen(),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('FLAME Guard',
            style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        backgroundColor: const Color(0xFFE65100),
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.white),
            onPressed: _logout,
            tooltip: 'Logout',
          ),
        ],
      ),
      body: pages[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        type: BottomNavigationBarType.fixed,
        selectedItemColor: const Color(0xFFE65100),
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(
              icon: Icon(Icons.local_fire_department), label: 'Fire'),
          BottomNavigationBarItem(icon: Icon(Icons.pets), label: 'Animals'),
          BottomNavigationBarItem(
              icon: Icon(Icons.report_problem_outlined), label: 'Complaints'),
          BottomNavigationBarItem(
              icon: Icon(Icons.notifications), label: 'Alerts'),
        ],
      ),
    );
  }
}

// Helper class for dashboard items
class _DashboardItem {
  final String title;
  final IconData icon;
  final Color color;
  final String description;
  const _DashboardItem(
      {required this.title,
      required this.icon,
      required this.color,
      required this.description});
}
