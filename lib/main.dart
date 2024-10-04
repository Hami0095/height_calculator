import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'package:http/http.dart' as http;

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Height Calculator',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  File? _image;
  bool _isCalculating = false;

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera);

    if (pickedFile != null) {
      print('Image picked: ${pickedFile.path}'); // Debugging line
      setState(() {
        _image = File(pickedFile.path);
      });
    } else {
      print('No image selected.'); // Debugging line
    }
  }

  Future<void> _calculateHeight() async {
    setState(() {
      _isCalculating = true;
    });

    // Send the image to the backend
    var request = http.MultipartRequest(
        'POST', Uri.parse('http://154.208.61.25:5000/upload'));
    request.files.add(await http.MultipartFile.fromPath('image', _image!.path));

    var response = await request.send();

    if (response.statusCode == 200) {
      debugPrint("Kia baat hai ge!");
      // Process the response from the backend
      // Example: final responseData = await response.stream.bytesToString();
      // Handle the response as needed
    }

    setState(() {
      _isCalculating = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Height Calculator'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            _image == null
                ? Image.asset('assets/no_image.jpg', height: 200)
                : Image.file(_image!, height: 200),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _pickImage,
              child: Text('Open Camera'),
            ),
            SizedBox(height: 20),
            if (_image != null) ...[
              ElevatedButton(
                onPressed: _isCalculating ? null : _calculateHeight,
                child: Text('Calculate Height'),
              ),
              if (_isCalculating) CircularProgressIndicator(),
            ],
          ],
        ),
      ),
    );
  }
}
