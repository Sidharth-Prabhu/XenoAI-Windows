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
title: 'Simple Todo App',
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
'Getting ready...',
'Almost there...',
];

@override
void initState() {
super.initState();
Timer(Duration(seconds: 3), () {
Navigator.pushReplacement(
context,
MaterialPageRoute(builder: (context) => TodoListScreen()),
);
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
style: TextStyle(
color: Colors.white,
fontSize: 24,
fontWeight: FontWeight.bold,
),
),
SizedBox(height: 20),
CircularProgressIndicator(
valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
),
],
),
),
);
}
}


class TodoListScreen extends StatefulWidget {
@override
_TodoListScreenState createState() => _TodoListScreenState();
}

class _TodoListScreenState extends State<TodoListScreen> {
List<String> todoItems = [];
final TextEditingController _textController = TextEditingController();

void _addTodoItem(String item) {
setState(() {
todoItems.add(item);
});
_textController.clear();
}

void _removeTodoItem(int index) {
setState(() {
todoItems.removeAt(index);
});
}

@override
Widget build(BuildContext context) {
return Scaffold(
appBar: AppBar(
title: Text('Simple Todo App'),
),
body: Column(
children: <Widget>[
Padding(
padding: const EdgeInsets.all(8.0),
child: Row(
children: <Widget>[
Expanded(
child: TextField(
controller: _textController,
decoration: InputDecoration(hintText: 'Enter a todo item'),
),
),
IconButton(
icon: Icon(Icons.add),
onPressed: () {
_addTodoItem(_textController.text);
},
),
],
),
),
Expanded(
child: ListView.builder(
itemCount: todoItems.length,
itemBuilder: (context, index) {
return ListTile(
title: Text(todoItems[index]),
trailing: IconButton(
icon: Icon(Icons.delete),
onPressed: () {
_removeTodoItem(index);
},
),
);
},
),
),
],
),
);
}
}