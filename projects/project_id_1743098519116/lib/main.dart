import 'package:flutter/material.dart';
import 'dart:math';
import 'dart:async';

import 'screens/todo_list_screen.dart';

void main() {
runApp(const MyApp());
}

class MyApp extends StatelessWidget {
const MyApp({super.key});

@override
Widget build(BuildContext context) {
return MaterialApp(
title: 'Todo App',
theme: ThemeData(
primarySwatch: Colors.blue,
),
home: const SplashScreen(),
);
}
}

class SplashScreen extends StatefulWidget {
const SplashScreen({super.key});

@override
State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
List<String> loadingMessages = [
'Compiling...',
'Building app...',
'Loading Interface...',
'Fetching data...',
'Getting ready...',
];

@override
void initState() {
super.initState();
Timer(const Duration(seconds: 3), () {
Navigator.pushReplacement(
context,
MaterialPageRoute(builder: (context) => const TodoListScreen()),
);
});
}

@override
Widget build(BuildContext context) {
Random random = Random();
String message = loadingMessages[random.nextInt(loadingMessages.length)];
return Scaffold(
body: Center(
child: Column(
mainAxisAlignment: MainAxisAlignment.center,
children: [
const CircularProgressIndicator(),
const SizedBox(height: 20),
Text(message),
],
),
),
);
}
}