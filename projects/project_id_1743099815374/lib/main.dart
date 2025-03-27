import 'package:flutter/material.dart';
import 'dart:math';
import 'dart:async';

void main() {
runApp(MyApp());
}

class MyApp extends StatelessWidget {
@override
Widget build(BuildContext context) {
return MaterialApp(
title: 'Tic-Tac-Toe',
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
final List<String> loadingMessages = [
'Compiling...',
'Building app...',
'Loading Interface...',
'Initializing...',
'Getting Ready...'
];

@override
void initState() {
super.initState();
Timer(Duration(seconds: 3), () {
Navigator.pushReplacement(
context, MaterialPageRoute(builder: (context) => TicTacToe()));
});
}

@override
Widget build(BuildContext context) {
return Scaffold(
backgroundColor: Colors.blue,
body: Center(
child: Column(
mainAxisAlignment: MainAxisAlignment.center,
children: <Widget>[
Text(
loadingMessages[Random().nextInt(loadingMessages.length)],
style: TextStyle(
color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
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


class TicTacToe extends StatefulWidget {
@override
_TicTacToeState createState() => _TicTacToeState();
}

class _TicTacToeState extends State<TicTacToe> {
List<String> board = ['', '', '', '', '', '', '', '', ''];
String currentPlayer = 'X';
bool gameEnded = false;

void makeMove(int index) {
if (board[index] == '' && !gameEnded) {
setState(() {
board[index] = currentPlayer;
if (checkWinner()) {
gameEnded = true;
} else if (board.every((element) => element != '')) {
gameEnded = true;
} else {
currentPlayer = currentPlayer == 'X' ? 'O' : 'X';
}
});
}
}

bool checkWinner() {
List<List<int>> winningCombinations = [
[0, 1, 2],
[3, 4, 5],
[6, 7, 8],
[0, 3, 6],
[1, 4, 7],
[2, 5, 8],
[0, 4, 8],
[2, 4, 6],
];
for (var combination in winningCombinations) {
if (board[combination[0]] != '' &&
board[combination[0]] == board[combination[1]] &&
board[combination[1]] == board[combination[2]]) {
return true;
}
}
return false;
}

void resetGame() {
setState(() {
board = ['', '', '', '', '', '', '', '', ''];
currentPlayer = 'X';
gameEnded = false;
});
}


@override
Widget build(BuildContext context) {
return Scaffold(
appBar: AppBar(
title: Text('Tic-Tac-Toe'),
),
body: Column(
children: [
Expanded(
child: GridView.builder(
gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
crossAxisCount: 3,
),
itemCount: 9,
itemBuilder: (context, index) {
return GestureDetector(
onTap: () => makeMove(index),
child: Container(
decoration: BoxDecoration(
border: Border.all(color: Colors.black),
),
child: Center(
child: Text(
board[index],
style: TextStyle(fontSize: 40),
),
),
),
);
},
),
),
ElevatedButton(onPressed: resetGame, child: Text('Reset Game'))
],
),
);
}
}