# XenoAI - GEMINI Powered AI App Builder (Windows Version)

## Overview

This project is a Python Flask-based application that provides a ChatGPT-like UI for users to input app ideas. The system uses the Gemini API to generate Android app code (both in Android Studio and React Native), automates the build process, and provides a downloadable APK to the user.

## Features

- Accepts user prompts to generate Android app source code.
- Uses GEMINI API for generating the code.
- uses Flutter SDK for building and packaging the app.
- Automatically debugs the code if any error is occured.
- Uses the Flutter SDK for efficient APK generation.
- Provides a downloadable APK file upon completion.
- Allows users to further refine and modify the generated app.

## Technologies Used

- **Flask**: Web framework to handle API requests.
- **Gemini API**: AI-based app code generation.
- **Flutter SDK**: Used to generate and build APK files.
- **HTML, CSS, JavaScript**: Frontend for the user prompt interface.

## Installation

### Prerequisites

Ensure you have the following installed:

- Python 3.x
- Flask (`pip install flask`)
- google.generativeai (`pip install google.generativeai`)
- Gemini API key (from Google AI services)
- Flutter SDK (Ensure `flutter` command is accessible)

### Setup Instructions

1. Clone this repository:
   ```bash
   git clone https://github.com/Sidharth-Prabhu/XenoAI-Darwin.git
   cd XenoAI-Darwin
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the Gemini API key:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```
4. Run the Flask server:
   ```bash
   python app.py
   ```
5. Access the UI at `http://localhost:2525`

## Usage

1. Enter your app idea in the prompt field.
2. Choose the desired framework (Android Studio or React Native).
3. Submit the request to generate the app code.
4. Wait for the APK to be built and download it once available.

## Deployment

To deploy the Flask app on a remote server:

```bash
flask run --host=0.0.0.0 --port=2525
```

## Contribution

Contributions are welcome! Please submit a pull request or report issues in the repository.

