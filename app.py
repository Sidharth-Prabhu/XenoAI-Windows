import os
import time
import subprocess
import shutil
import json
from datetime import datetime
from flask import Flask, request, render_template, send_file, jsonify, url_for, session, redirect
from functools import wraps
from PIL import Image

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Replace with a secure key

# Configure Gemini API
try:
    import google.generativeai as genai
    # Replace with your actual key
    GEMINI_API_KEY = "AIzaSyDsFr09dbeekpsPYxIWESlvE_QJaErVv1Y"
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except ImportError as e:
    print(
        f"Failed to import google.generativeai: {e}. Install it with 'pip install google-generativeai'")

# Directories and files
PROJECT_DIR = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "projects")
USER_DATA_FILE = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "users.json")
PROJECT_DATA_FILE = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "projects.json")
PROMPT_LOG_FILE = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "prompts.json")

if not os.path.exists(PROJECT_DIR):
    os.makedirs(PROJECT_DIR)
if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump({}, f)
if not os.path.exists(PROJECT_DATA_FILE):
    with open(PROJECT_DATA_FILE, 'w') as f:
        json.dump([], f)
if not os.path.exists(PROMPT_LOG_FILE):
    with open(PROMPT_LOG_FILE, 'w') as f:
        json.dump([], f)

# Login required decorator


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    with open(PROJECT_DATA_FILE, 'r') as f:
        projects = json.load(f)
    return render_template('index.html', username=session.get('username'), projects=projects)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        with open(USER_DATA_FILE, 'r') as f:
            users = json.load(f)

        if username in users:
            return jsonify({"error": "Username already exists"}), 400

        users[username] = {"password": password}
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(users, f, indent=2)

        session['username'] = username
        return jsonify({"redirect": url_for('index')})

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        with open(USER_DATA_FILE, 'r') as f:
            users = json.load(f)

        if username in users and users[username]['password'] == password:
            session['username'] = username
            return jsonify({"redirect": url_for('index')})
        return jsonify({"error": "Invalid username or password"}), 401

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/generate', methods=['POST'])
@login_required
def generate_app():
    prompt = request.form.get('prompt', '')
    app_name = request.form.get('app_name', 'GeneratedApp')
    app_version = request.form.get('app_version', '1.0.0')
    package_name = request.form.get('package_name', 'com.example.generatedapp')
    build_type = request.form.get('build_type', 'debug')
    api_key = request.form.get('api_key', None)
    continue_build = request.form.get('continue_build', None)
    app_icon = request.files.get('app_icon')  # Get the uploaded icon file

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Log the prompt
    with open(PROMPT_LOG_FILE, 'r') as f:
        prompts = json.load(f)
    prompts.append({
        "prompt": prompt,
        "username": session['username'],
        "timestamp": datetime.now().isoformat()
    })
    with open(PROMPT_LOG_FILE, 'w') as f:
        json.dump(prompts, f, indent=2)

    requires_api_key = any(keyword in prompt.lower()
                           for keyword in ['api', 'fetch', 'http', 'request'])
    if requires_api_key and not api_key:
        return jsonify({"requires_api_key": True}), 200

    # If not continuing to build, just return the generated code
    if not continue_build:
        gemini_prompt = f"""
        Generate Dart code for a Flutter app based on this idea: '{prompt}'. 
        Provide complete, raw Dart code for all necessary files including:
        1. `lib/main.dart` with imports, widgets, and basic Material Design styling
        2. Any additional screen files needed (e.g., `lib/screens/screen_name.dart`)
        Use only built-in Flutter dependencies (no external packages from pub.dev).
        If an API key is provided (e.g., '{api_key or ""}'), include it in the code where necessary.
        Return only the raw Dart code for each file, separated by '---' between files, 
        with no Markdown, backticks, or explanatory text. Start each file with its path 
        on the first line (e.g., 'lib/main.dart'), followed by the code, add a splash screen for the app 
        that should show a loading screen animation for 5 seconds with black background and a branding text "Made by Team SyntaxError404"
        in white text with random texts like 'Compiling...', 'Building app...',
        'Loading Interface...' and so on, this should show randomly with time intervals in the splash screen.
        """
        try:
            response = model.generate_content(gemini_prompt)
            generated_content = response.text.strip()
            return jsonify({"code": generated_content})
        except Exception as e:
            app.logger.error(f"Gemini API error: {str(e)}")
            return jsonify({"error": f"Failed to generate code: {str(e)}"}), 500

    # If continue_build is true, proceed with building the APK
    unique_number = int(time.time() * 1000)
    project_name = f"project_id_{unique_number}"
    project_path = os.path.join(PROJECT_DIR, project_name)

    max_attempts = 3
    attempt = 0
    generated_content = None
    last_error = None

    while attempt < max_attempts:
        attempt += 1
        app.logger.info(
            f"Attempt {attempt} to generate app for prompt: {prompt}")

        if attempt == 1:
            gemini_prompt = f"""
            Generate Dart code for a Flutter app based on this idea: '{prompt}'. 
            Provide complete, raw Dart code for all necessary files including:
            1. `lib/main.dart` with imports, widgets, and basic Material Design styling
            2. Any additional screen files needed (e.g., `lib/screens/screen_name.dart`)
            Use only built-in Flutter dependencies (no external packages from pub.dev).
            If an API key is provided (e.g., '{api_key or ""}'), include it in the code where necessary.
            Return only the raw Dart code for each file, separated by '---' between files, 
            with no Markdown, backticks, or explanatory text. Start each file with its path 
            on the first line (e.g., 'lib/main.dart'), followed by the code, add a splash screen for the app 
            that should show a loading screen animation for 3 seconds with random texts like 'Compiling...', 'Building app...',
            'Loading Interface...' and so on, this should show randomly with time intervals in the splash screen.
            """
        else:
            gemini_prompt = f"""
            The previous attempt to generate a Flutter app for '{prompt}' failed with this build error: 
            '{last_error}'. Here’s the previously generated code:
            {generated_content}
            Please analyze the error, fix the code to resolve it, and provide corrected raw Dart code 
            for all necessary files (e.g., `lib/main.dart`, `lib/screens/screen_name.dart`). 
            Use only built-in Flutter dependencies. If an API key is provided (e.g., '{api_key or ""}'), 
            include it where necessary. Return only the raw Dart code, separated by '---' between files, 
            with no Markdown, backticks, or explanatory text. Start each file with its path on the first line.
            """

        try:
            response = model.generate_content(gemini_prompt)
            generated_content = response.text.strip()
        except Exception as e:
            app.logger.error(
                f"Gemini API error on attempt {attempt}: {str(e)}")
            return jsonify({"error": f"Failed to generate code: {str(e)}"}), 500

        try:
            if os.path.exists(project_path):
                shutil.rmtree(project_path)

            flutter_create_cmd = f'flutter create --project-name "{app_name.lower()}" --org "{package_name.rsplit(".", 1)[0]}" "{project_path}"'
            create_result = subprocess.run(
                ["powershell", "-Command", flutter_create_cmd],
                capture_output=True,
                text=True
            )
            if create_result.returncode != 0:
                raise Exception(
                    f"Project creation failed: {create_result.stderr}")
            time.sleep(5)

            pubspec_path = os.path.join(project_path, "pubspec.yaml")
            with open(pubspec_path, 'r') as f:
                pubspec_content = f.readlines()

            new_pubspec = []
            for line in pubspec_content:
                if line.strip().startswith('name:'):
                    new_pubspec.append(f"name: {app_name.lower()}\n")
                elif line.strip().startswith('version:'):
                    new_pubspec.append(f"version: {app_version}\n")
                else:
                    new_pubspec.append(line)

            with open(pubspec_path, 'w') as f:
                f.writelines(new_pubspec)

            manifest_path = os.path.join(
                project_path, "android", "app", "src", "main", "AndroidManifest.xml")
            with open(manifest_path, 'r') as f:
                manifest_content = f.read()

            manifest_content = manifest_content.replace(
                'com.example', package_name.rsplit(".", 1)[0])
            with open(manifest_path, 'w') as f:
                f.write(manifest_content)

            # Handle app icon if provided
            if app_icon and app_icon.filename.endswith('.png'):
                try:
                    # Save the uploaded icon temporarily
                    temp_icon_path = os.path.join(
                        project_path, "temp_icon.png")
                    app_icon.save(temp_icon_path)

                    # Define icon sizes and directories for Android
                    icon_sizes = {
                        'mipmap-mdpi': (48, 48),
                        'mipmap-hdpi': (72, 72),
                        'mipmap-xhdpi': (96, 96),
                        'mipmap-xxhdpi': (144, 144),
                        'mipmap-xxxhdpi': (192, 192)
                    }

                    # Open the uploaded image
                    with Image.open(temp_icon_path) as img:
                        # Ensure image is in RGBA mode
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')

                        # Replace default icons in Android resources
                        android_res_path = os.path.join(
                            project_path, "android", "app", "src", "main", "res")
                        for folder, size in icon_sizes.items():
                            icon_path = os.path.join(android_res_path, folder)
                            if not os.path.exists(icon_path):
                                os.makedirs(icon_path)

                            # Resize image for each density
                            resized_img = img.resize(
                                size, Image.Resampling.LANCZOS)
                            output_path = os.path.join(
                                icon_path, "ic_launcher.png")
                            resized_img.save(output_path, "PNG")

                    # Clean up temporary file
                    os.remove(temp_icon_path)

                    # Update AndroidManifest.xml to use the new icon
                    with open(manifest_path, 'r') as f:
                        manifest_content = f.read()
                    manifest_content = manifest_content.replace(
                        'android:icon="@mipmap/ic_launcher"',
                        'android:icon="@mipmap/ic_launcher"')
                    with open(manifest_path, 'w') as f:
                        f.write(manifest_content)

                except Exception as e:
                    app.logger.error(f"Failed to process app icon: {str(e)}")
                    # Continue even if icon processing fails, using default icon

            files_content = {}
            current_file = None
            current_content = []

            for line in generated_content.split('\n'):
                line = line.strip()
                if line.startswith('lib/') and (line.endswith('.dart') or line in ['lib/main.dart']):
                    if current_file and current_content:
                        files_content[current_file] = '\n'.join(
                            current_content)
                    current_file = line
                    current_content = []
                elif line == '---':
                    if current_file and current_content:
                        files_content[current_file] = '\n'.join(
                            current_content)
                    current_file = None
                    current_content = []
                elif current_file:
                    current_content.append(line)

            if current_file and current_content:
                files_content[current_file] = '\n'.join(current_content)

            lib_path = os.path.join(project_path, "lib")
            screens_path = os.path.join(lib_path, "screens")
            if not os.path.exists(lib_path):
                os.makedirs(lib_path)
            if any(path.startswith('lib/screens/') for path in files_content.keys()):
                if not os.path.exists(screens_path):
                    os.makedirs(screens_path)

            for file_path, content in files_content.items():
                full_path = os.path.join(project_path, file_path)
                with open(full_path, 'w') as f:
                    f.write(content.strip())

            apk_path = build_apk(project_path, build_type)
            if apk_path:
                with open(PROJECT_DATA_FILE, 'r') as f:
                    projects = json.load(f)
                projects.append({
                    "project_name": project_name,
                    "app_name": app_name,
                    "username": session['username'],
                    "created_at": datetime.now().isoformat()
                })
                with open(PROJECT_DATA_FILE, 'w') as f:
                    json.dump(projects, f, indent=2)

                download_url = url_for(
                    'download_page', project_name=project_name, _external=True)
                return jsonify({"redirect": download_url})
            else:
                raise Exception("Build returned no APK path")

        except Exception as e:
            last_error = str(e)
            if isinstance(e, subprocess.CalledProcessError):
                last_error = e.stderr
            app.logger.error(f"Attempt {attempt} failed: {last_error}")
            if attempt == max_attempts:
                return jsonify({"error": f"Failed to generate APK after {max_attempts} attempts: {last_error}"}), 500
            time.sleep(2)


def build_apk(project_path, build_type='debug'):
    os.chdir(project_path)
    if not os.path.exists("android"):
        app.logger.error("Android directory not found in project path.")
        return None
    try:
        build_cmd = f"flutter build apk --{build_type}"
        result = subprocess.run(
            build_cmd,
            shell=True,
            check=True,
            cwd=project_path,
            capture_output=True,
            text=True
        )
        app.logger.info(f"Build Output: {result.stdout}")
        apk_suffix = "debug" if build_type == "debug" else "release"
        apk_path = os.path.join(
            project_path, "build", "app", "outputs", "flutter-apk", f"app-{apk_suffix}.apk")
        if os.path.exists(apk_path):
            return apk_path
        app.logger.error("APK file not found after build.")
        return None
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Build error: {e.stderr}")
        raise


@app.route('/download/<project_name>')
@login_required
def download_page(project_name):
    debug_apk_path = os.path.join(
        PROJECT_DIR, project_name, "build", "app", "outputs", "flutter-apk", "app-debug.apk")
    release_apk_path = os.path.join(
        PROJECT_DIR, project_name, "build", "app", "outputs", "flutter-apk", "app-release.apk")

    if os.path.exists(debug_apk_path):
        apk_path = f"/download_file/{project_name}/debug"
    elif os.path.exists(release_apk_path):
        apk_path = f"/download_file/{project_name}/release"
    else:
        return render_template('error.html', message="APK not found"), 404

    return render_template('download.html', apk_path=apk_path, project_name=project_name)


@app.route('/download_file/<project_name>/<build_type>')
@login_required
def download_file(project_name, build_type):
    apk_path = os.path.join(PROJECT_DIR, project_name, "build",
                            "app", "outputs", "flutter-apk", f"app-{build_type}.apk")
    if os.path.exists(apk_path):
        return send_file(apk_path, as_attachment=True, download_name=f"{project_name}.apk")
    return "File not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
