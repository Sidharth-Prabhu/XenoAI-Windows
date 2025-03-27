import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';

void main() {
runApp(MyApp());
}

class MyApp extends StatelessWidget {
@override
Widget build(BuildContext context) {
return MaterialApp(
title: 'Simple Clock',
theme: ThemeData(
primarySwatch: Colors.blue,
),
home: SplashScreen(),
);
}
}

class SplashScreen extends StatefulWidget {
@override
_SplashScreenState createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
List<String> loadingMessages = [
'Compiling...',
'Building app...',
'Loading Interface...',
'Preparing Clock...',
'Almost there...'
];

@override
void initState() {
super.initState();
Timer(Duration(seconds: 3), () {
Navigator.pushReplacement(
context, MaterialPageRoute(builder: (context) => MyHomePage()));
});
}

@override
Widget build(BuildContext context) {
return Scaffold(
backgroundColor: Colors.blue,
body: Center(
child: Column(
mainAxisAlignment: MainAxisAlignment.center,
children: [
Text(
loadingMessages[Random().nextInt(loadingMessages.length)],
style: TextStyle(color: Colors.white, fontSize: 20),
),
CircularProgressIndicator(
valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
),
],
),
),
);
}
}

class MyHomePage extends StatefulWidget {
@override
_MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
TimeOfDay _currentTime = TimeOfDay.now();

@override
void initState() {
super.initState();
_updateTime();
}

void _updateTime() {
setState(() {
_currentTime = TimeOfDay.now();
});
Timer(Duration(seconds: 1), _updateTime);
}

@override
Widget build(BuildContext context) {
return Scaffold(
appBar: AppBar(
title: Text('Simple Clock'),
),
body: Center(
child: Text(
_currentTime.format(context),
style: TextStyle(fontSize: 48),
),
),
);
}
}