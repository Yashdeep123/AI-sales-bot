
import os
import sys
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify, render_template, send_from_directory

from products import SAAS_PRODUCTS, get_product, list_products
from sales_agent import SalesAgent
from summarizer import CallSummarizer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RECORDINGS_DIR = os.path.join(BASE_DIR, "recordings")
CALLS_FILE = os.path.join(DATA_DIR, "calls.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RECORDINGS_DIR, exist_ok=True)

if not os.path.exists(CALLS_FILE):
    with open(CALLS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB audio files


def load_calls():
    try:
        with open(CALLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_calls(calls):
    with open(CALLS_FILE, "w", encoding="utf-8") as f:
        json.dump(calls, f, indent=2, ensure_ascii=False)


# --- Web UI Routes ---

@app.route("/")
def index():
    return render_template("index.html")


# --- REST API Endpoints ---

@app.route("/api/products", methods=["GET"])
def get_products_api():
    """Return catalog of available SaaS products."""
    return jsonify({
        "products": list_products(),
        "catalog": SAAS_PRODUCTS
    })


@app.route("/api/greeting", methods=["POST"])
def get_greeting():
    """Generate the initial opening line for the AI voice sales agent."""
    data = request.get_json() or {}
    product_id = data.get("product_id", "aws-services")
    language = data.get("language", "en")
    agent = SalesAgent(product_id=product_id, language=language)
    greeting = agent.generate_initial_greeting()
    return jsonify({
        "greeting": greeting,
        "language": language,
        "product": get_product(product_id)["name"]
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    """Process customer voice input / text and return AI sales response."""
    data = request.get_json() or {}
    user_message = data.get("user_message", "")
    conversation_history = data.get("conversation_history", [])
    product_id = data.get("product_id", "aws-services")
    language = data.get("language", "en")
    api_key = data.get("api_key")

    agent = SalesAgent(product_id=product_id, language=language, api_key=api_key)
    response_text = agent.respond(user_message, conversation_history)

    return jsonify({
        "response": response_text,
        "language": language
    })


@app.route("/api/summary", methods=["POST"])
def generate_summary():
    """Analyze full call transcript, generate structured summary & assign sales status."""
    data = request.get_json() or {}
    transcript = data.get("transcript", [])
    product_id = data.get("product_id", "aws-services")
    language = data.get("language", "en")
    api_key = data.get("api_key")

    product = get_product(product_id)
    summarizer = CallSummarizer(api_key=api_key)
    analysis = summarizer.analyze_call(
        transcript_messages=transcript,
        product_name=product["name"],
        language=language
    )

    return jsonify(analysis)


@app.route("/api/recordings", methods=["POST"])
def upload_recording():
    """Save recorded 2-way call audio blob and return audio URL."""
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    call_id = request.form.get("call_id", str(uuid.uuid4())[:8])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = "webm"
    if "wav" in audio_file.content_type:
        extension = "wav"
    filename = f"call_{call_id}_{timestamp}.{extension}"
    filepath = os.path.join(RECORDINGS_DIR, filename)

    audio_file.save(filepath)

    return jsonify({
        "success": True,
        "filename": filename,
        "recording_url": f"/recordings/{filename}"
    })


@app.route("/recordings/<filename>")
def serve_recording(filename):
    """Serve saved voice recordings for inline audio player."""
    return send_from_directory(RECORDINGS_DIR, filename)


@app.route("/api/calls", methods=["GET"])
def get_calls():
    """Retrieve saved call history sorted by most recent."""
    calls = load_calls()
    calls.sort(key=lambda c: c.get("created_at", ""), reverse=True)
    return jsonify(calls)


@app.route("/api/calls", methods=["POST"])
def save_call():
    """Persist a finished call with recording, transcript, summary, and sales status."""
    call_data = request.get_json() or {}
    if not call_data.get("id"):
        call_data["id"] = f"call_{str(uuid.uuid4())[:8]}"
    if not call_data.get("created_at"):
        call_data["created_at"] = datetime.now().isoformat()

    calls = load_calls()
    calls.append(call_data)
    save_calls(calls)

    return jsonify({
        "success": True,
        "call": call_data
    })


@app.route("/api/calls/<call_id>", methods=["DELETE"])
def delete_call(call_id):
    """Delete a specific call from history."""
    calls = load_calls()
    new_calls = [c for c in calls if c.get("id") != call_id]
    save_calls(new_calls)
    return jsonify({"success": True, "remaining": len(new_calls)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 AI Voice Sales Bot Server running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
