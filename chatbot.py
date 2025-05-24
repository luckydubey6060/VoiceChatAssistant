import requests  # Not needed for Gemini, but kept for compatibility
from flask import Flask, request, render_template_string
import google.generativeai as genai
from werkzeug.utils import secure_filename
import os

# Configure Gemini API
API_KEY = "AIzaSyDwVy6UD8sIUj4YycQo67bNTu9fLbTCZRE"  # Replace with your Gemini API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")  # Free tier model with multimodal support

# Create the Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder for uploaded images
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Create folder if it doesn’t exist

def get_response(message, image_path=None):
    try:
        if image_path:  # If an image is uploaded
            img = genai.upload_file(image_path)
            response = model.generate_content([message, img])
        else:  # Just text
            response = model.generate_content(message)
        return response.text
    except Exception as e:
        return f"Oops, something went awry in the magic realm! ({str(e)})"

# Updated magical HTML template with photo upload
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Magical Chatbot😜</title>
    <style>
        body {
            font-family: 'Georgia', serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e1e5d, #5d1e5d, #1e5d5d);
            color: #fff;
            overflow: hidden;
        }
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"><circle cx="2" cy="2" r="1" fill="rgba(255,255,255,0.5)"/></svg>');
            background-size: 20px 20px;
            animation: sparkle 10s infinite;
            pointer-events: none;
        }
        h1 {
            text-align: center;
            font-size: 2.5em;
            text-shadow: 0 0 10px #fff, 0 0 20px #ffccff;
            color: #ffccff;
            animation: glow 2s infinite alternate;
        }
        .chatbox {
            width: 800px;
            height: 450px;
            margin: 20px auto;
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid #ffccff;
            border-radius: 20px;
            box-shadow: 0 0 20px rgba(255, 204, 255, 0.5);
            overflow-y: auto;
            padding: 15px;
        }
        .message {
            margin: 10px;
            padding: 10px;
            border-radius: 10px;
            animation: fadeIn 0.5s ease-in;
            max-width: 80%;
        }
        .user {
            background: #cce5ff;
            color: #1e1e5d;
            text-align: right;
            margin-left: auto;
        }
        .bot {
            background: #e5ccff;
            color: #5d1e5d;
        }
        .image-preview {
            max-width: 200px;
            border-radius: 10px;
            margin-top: 5px;
        }
        form {
            text-align: center;
            margin-top: 20px;
            display: flex;
            justify-content: center;
            gap: 10px;
            align-items: center;
        }
        input[type="text"] {
            width: 400px;
            padding: 10px;
            font-size: 1.1em;
            border: 2px solid #ffccff;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.2);
            color: #fff;
            outline: none;
            transition: box-shadow 0.3s;
        }
        input[type="text"]:focus {
            box-shadow: 0 0 15px #ffccff;
        }
        input[type="file"] {
            color: #ffccff;
        }
        input[type="submit"] {
            padding: 10px 20px;
            font-size: 1.1em;
            background: #ffccff;
            color: #1e1e5d;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            box-shadow: 0 0 10px #ffccff;
            transition: all 0.3s;
        }
        input[type="submit"]:hover {
            background: #fff;
            box-shadow: 0 0 20px #ffccff;
        }
        @keyframes sparkle {
            0% { opacity: 0.3; transform: translate(0, 0); }
            50% { opacity: 0.7; transform: translate(5px, 5px); }
            100% { opacity: 0.3; transform: translate(0, 0); }
        }
        @keyframes glow {
            from { text-shadow: 0 0 10px #fff, 0 0 20px #ffccff; }
            to { text-shadow: 0 0 20px #fff, 0 0 30px #ffccff; }
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <h1>✨ Magical Chatbot ✨</h1>
    <div class="chatbox" id="chatbox">
        {% for msg in messages %}
            <div class="message {{ msg.type }}">
                {{ msg.content }}
                {% if msg.image %}
                    <br><img src="{{ msg.image }}" class="image-preview" alt="Uploaded image">
                {% endif %}
            </div>
        {% endfor %}
    </div>
    <form method="POST" enctype="multipart/form-data">
        <input type="text" name="message" placeholder="Cast your spell here..." autocomplete="off">
        <input type="file" name="image" accept="image/*">
        <input type="submit" value="Send 😉">
    </form>
</body>
</html>
"""

# Store chat history
chat_history = []

@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_message = request.form["message"]
        image_file = request.files.get("image")
        image_path = None
        image_url = None

        if image_file:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_url = f"/{image_path}"

        if user_message.lower() == "bye":
            chat_history.append({"type": "user", "content": "bye", "image": image_url})
            chat_history.append({"type": "bot", "content": "Catch you later, wizard!", "image": None})
        else:
            chat_history.append({"type": "user", "content": user_message, "image": image_url})
            bot_reply = get_response(user_message, image_path)
            chat_history.append({"type": "bot", "content": bot_reply, "image": None})

    return render_template_string(HTML_TEMPLATE, messages=chat_history)

# Serve uploaded images
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return app.send_static_file(os.path.join('uploads', filename))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)  # Or 5002 if you prefer