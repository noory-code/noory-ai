import 'package:flutter/material.dart';

void main() {
  runApp(const DatePickerApp());
}

class DatePickerApp extends StatelessWidget {
  const DatePickerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: Colors.blue, // 깔끔한 기본 블루 톤
      ),
      home: const DatePickerExample(),
    );
  }
}

// 달력을 띄우고 날짜를 저장해야 하므로 StatefulWidget을 사용합니다.
class DatePickerExample extends StatefulWidget {
  const DatePickerExample({super.key});

  @override
  State<DatePickerExample> createState() => _DatePickerExampleState();
}

class _DatePickerExampleState extends State<DatePickerExample> {
  DateTime? _selectedDate; // 선택된 날짜를 저장할 변수

  // 달력을 띄우는 핵심 함수
  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(), // 달력이 켜질 때 기본으로 선택되어 있을 날짜 (오늘)
      firstDate: DateTime(2000), // 선택 가능한 가장 과거의 날짜
      lastDate: DateTime(2100), // 선택 가능한 가장 미래의 날짜
      // 💡 팁: 달력 상단의 도움말 텍스트를 한글로 바꿀 수도 있습니다.
      helpText: '예약 날짜를 선택하세요',
      cancelText: '취소',
      confirmText: '확인',
    );

    // 사용자가 날짜를 선택하고 '확인'을 눌렀다면 (취소 안 하고)
    if (picked != null && picked != _selectedDate) {
      setState(() {
        _selectedDate = picked; // 화면을 다시 그려서 선택된 날짜를 갱신합니다.
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('기본 데이트 피커')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // 선택된 날짜 보여주기
            Text(
              _selectedDate == null
                  ? '아직 날짜를 선택하지 않았습니다.'
                  : '선택된 날짜: ${_selectedDate!.year}년 ${_selectedDate!.month}월 ${_selectedDate!.day}일',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 30),

            // 달력 띄우기 버튼
            FilledButton.icon(
              onPressed: () => _selectDate(context),
              icon: const Icon(Icons.calendar_today),
              label: const Text('날짜 선택하기'),
            ),
          ],
        ),
      ),
    );
  }
}
