import 'package:flutter/material.dart';
import '../services/api_service.dart';

class AnimalsScreen extends StatefulWidget {
  const AnimalsScreen({super.key});

  @override
  State<AnimalsScreen> createState() => _AnimalsScreenState();
}

class _AnimalsScreenState extends State<AnimalsScreen> {
  List<dynamic> _animals = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchAnimals();
  }

  Future<void> _fetchAnimals() async {
    setState(() => _isLoading = true);
    final data = await ApiService.getAnimals();
    setState(() { _animals = data; _isLoading = false; });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Forest Animals', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.green.shade700,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.green))
          : _animals.isEmpty
              ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.eco_outlined, size: 70, color: Colors.grey),
                      SizedBox(height: 12),
                      Text('No Animals Found', style: TextStyle(fontSize: 16, color: Colors.grey)),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _fetchAnimals,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _animals.length,
                    itemBuilder: (ctx, i) => _buildAnimalCard(_animals[i]),
                  ),
                ),
    );
  }

  Widget _buildAnimalCard(dynamic animal) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Row(
        children: [
          // Animal image or placeholder
          ClipRRect(
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(14),
              bottomLeft: Radius.circular(14),
            ),
            child: animal['image'] != null
                ? Image.network(
                    animal['image'].toString().startsWith('http')
                        ? animal['image']
                        : '${ApiService.BASE_URL}${animal['image']}',
                    width: 100,
                    height: 100,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => _animalPlaceholder(),
                  )
                : _animalPlaceholder(),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    animal['name'] ?? 'Unknown Animal',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  if (animal['division'] != null) ...[
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        const Icon(Icons.account_tree_outlined, size: 13, color: Colors.grey),
                        const SizedBox(width: 4),
                        Text(animal['division'],
                            style: const TextStyle(color: Colors.grey, fontSize: 12)),
                      ],
                    ),
                  ],
                  if (animal['scientific_name'] != null) ...[
                    const SizedBox(height: 2),
                    Text(animal['scientific_name'],
                        style: TextStyle(
                            fontSize: 11,
                            fontStyle: FontStyle.italic,
                            color: Colors.green.shade700)),
                  ],
                  const SizedBox(height: 6),
                  Text(
                    animal['description'] ?? 'No description available.',
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 12, color: Colors.black87),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _animalPlaceholder() {
    return Container(
      width: 100,
      height: 100,
      color: Colors.green.shade50,
      child: Icon(Icons.pets, size: 40, color: Colors.green.shade300),
    );
  }
}
