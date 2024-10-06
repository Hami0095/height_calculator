import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';

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
  String? _heightResult; // To store the height result returned by the server

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera);

    if (pickedFile != null) {
      print('Image picked: ${pickedFile.path}'); // Debugging line
      setState(() {
        _image = File(pickedFile.path);
        _heightResult = null; // Reset the result when a new image is picked
      });
    } else {
      print('No image selected.'); // Debugging line
    }
  }

  Future<void> _calculateHeight() async {
    if (_image == null) return; // Check if an image is selected

    setState(() {
      _isCalculating = true;
    });

    try {
      // Send the image to the backend
      var request = http.MultipartRequest(
          'POST', Uri.parse('http://192.168.100.179:5000/upload'));
      request.files
          .add(await http.MultipartFile.fromPath('image', _image!.path));

      var response = await request.send();
      if (response.statusCode == 200) {
        // Get the response body as a string
        final responseData = await http.Response.fromStream(response);
        print('Server Response: ${responseData.body}'); // Log the raw response

        // Parse the response body as JSON
        final Map<String, dynamic> data = jsonDecode(responseData.body);

        // Check the status and height_info in the response
        if (data['status'] == 'success' && data.containsKey('height_info')) {
          final heightInfo = data['height_info'];

          double? heightCm = heightInfo['height_cm']?.toDouble();
          int? feet = heightInfo['height_ft'];
          double? inches = heightInfo['height_inch']?.toDouble();

          if (heightCm != null && feet != null && inches != null) {
            setState(() {
              _heightResult =
                  'Estimated Height: ${heightCm.toStringAsFixed(2)} cm (${feet} ft ${inches.toStringAsFixed(1)} in)';
            });
          } else {
            setState(() {
              _heightResult =
                  'Failed to parse height details. Please try again.';
            });
          }
        } else {
          setState(() {
            _heightResult = 'Failed to get height details. Please try again.';
          });
        }
      } else {
        setState(() {
          _heightResult = 'Failed to calculate height. Try again.';
        });
      }
    } catch (e) {
      setState(() {
        _heightResult = 'Error: $e';
      });
    } finally {
      setState(() {
        _isCalculating = false;
      });
    }
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
              SizedBox(height: 20),
              if (_heightResult != null)
                Text(
                  _heightResult!,
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
            ],
          ],
        ),
      ),
    );
  }
}
