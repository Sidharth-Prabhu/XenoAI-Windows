import 'package:flutter/material.dart';

class TodoListScreen extends StatefulWidget {
const TodoListScreen({super.key});

@override
State<TodoListScreen> createState() => _TodoListScreenState();
}

class _TodoListScreenState extends State<TodoListScreen> {
final List<String> _todos = [];
final TextEditingController _textController = TextEditingController();

void _addTodo() {
setState(() {
if (_textController.text.isNotEmpty) {
_todos.add(_textController.text);
_textController.clear();
}
});
}

void _removeTodo(int index) {
setState(() {
_todos.removeAt(index);
});
}

@override
Widget build(BuildContext context) {
return Scaffold(
appBar: AppBar(
title: const Text('Todo List'),
),
body: Column(
children: [
Padding(
padding: const EdgeInsets.all(8.0),
child: Row(
children: [
Expanded(
child: TextField(
controller: _textController,
decoration: const InputDecoration(hintText: 'Add a todo'),
),
),
IconButton(
onPressed: _addTodo,
icon: const Icon(Icons.add),
),
],
),
),
Expanded(
child: ListView.builder(
itemCount: _todos.length,
itemBuilder: (context, index) {
return ListTile(
title: Text(_todos[index]),
trailing: IconButton(
onPressed: () => _removeTodo(index),
icon: const Icon(Icons.delete),
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