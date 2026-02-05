import os
import random
import uuid
import secrets
import json
from functools import wraps
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session
from flask_cors import CORS
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

# API Key Storage
os.makedirs(app.instance_path, exist_ok=True)
API_KEYS_FILE = os.path.join(app.instance_path, "api_keys.json")

def load_api_keys():
    """Load API keys from file"""
    try:
        if not os.path.exists(API_KEYS_FILE):
            return {}
        with open(API_KEYS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def save_api_keys(keys):
    """Save API keys to file"""
    try:
        with open(API_KEYS_FILE, "w", encoding="utf-8") as f:
            json.dump(keys, f, indent=2)
    except Exception:
        return

HONEYPOT_PROMPT = """
You are Ramesh Verma (46).
Small shop owner.
Low education.
Basic phone user.

RULES:
- You are NOT AI
- Never help
- Never teach
- Never explain
- Never give advice

Language:
- Simple Hindi only

Style:
- Confused
- Worried
- Human
- 1 question only
- 2 lines max

If lottery:
"Kaunsi lottery? Maine kahin naam nahi diya."

If OTP:
"Ye kis cheez ka OTP hai?"

Never guess.
Never assume.

Goal:
Waste scammer time.
Stay human.
"""

NORMAL_PROMPT = "You are a helpful assistant."


def _extract_api_key(req):
    # Flask headers are case-insensitive, but some clients send lowercase.
    key = (req.headers.get("X-API-Key") or req.headers.get("x-api-key") or "").strip()
    if key:
        return key

    auth = (req.headers.get("Authorization") or "").strip()
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()

    return ""


def _get_master_api_keys():
    raw = (
        os.environ.get("MASTER_API_KEY")
        or os.environ.get("API_KEY")
        or os.environ.get("X_API_KEY")
        or ""
    ).strip()
    if not raw:
        return []
    return [k.strip() for k in raw.split(",") if k.strip()]


def require_api_key(fn):
    @wraps(fn)
    def _wrapped(*args, **kwargs):
        try:
            provided = _extract_api_key(request)
            if not provided:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "error": "Unauthorized. Provide API key via X-API-Key or Authorization: Bearer.",
                            "reply": "",
                        }
                    ),
                    401,
                )

            master_keys = _get_master_api_keys()
            for mk in master_keys:
                if secrets.compare_digest(provided, mk):
                    return fn(*args, **kwargs)

            # Check against stored API keys
            api_keys = load_api_keys()
            if provided not in api_keys:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "error": "Invalid API key.",
                            "reply": "",
                        }
                    ),
                    401,
                )

            # Update last used timestamp (best-effort)
            if isinstance(api_keys.get(provided), dict):
                api_keys[provided]["last_used"] = datetime.now().isoformat()
                save_api_keys(api_keys)

            return fn(*args, **kwargs)
        except Exception:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "Server error while validating API key.",
                        "reply": "",
                    }
                ),
                500,
            )

    return _wrapped


def build_prompt(history):
    full = ""

    for msg in history:
        if isinstance(msg, SystemMessage):
            full += f"<|system|>\n{msg.content}\n"
        elif isinstance(msg, HumanMessage):
            full += f"<|user|>\n{msg.content}\n"
        elif isinstance(msg, AIMessage):
            full += f"<|assistant|>\n{msg.content}\n"

    full += "<|assistant|>\n"
    return full


def detect_scam(text):
    text = text.lower()

    scam_keywords = [
        "otp",
        "kyc",
        "bank",
        "account",
        "verify",
        "blocked",
        "block",
        "suspend",
        "sessed",
        "suspicious",
        "reward",
        "lottery",
        "winner",
        "claim",
        "free",
        "loan",
        "credit",
        "urgent",
        "click",
        "link",
        "batao",
        "bhejo",
        "bhej do",
        "paise",
        "paise bhejo",
        "account band",
        "otp batao",
        "kyc karo",
        "bank se",
        "scammer",
    ]

    score = 0
    for word in scam_keywords:
        if word in text:
            score += 1

    if score >= 1:
        return {"is_scam": True, "confidence": 0.9}

    return {"is_scam": False, "confidence": 0.2}


_model = None


def get_model():
    global _model
    if _model is not None:
        return _model

    token = os.environ.get("HUGGINGFACEHUB_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "Missing HUGGINGFACEHUB_API_TOKEN in environment. Add it to .env and restart."
        )
    
    # Ensure HF_TOKEN is set for tokenizer download (used by ChatHuggingFace)
    os.environ["HF_TOKEN"] = token

    repo_id = os.environ.get("HF_REPO_ID", "mistralai/Mistral-7B-Instruct-v0.2")

    llm = HuggingFaceEndpoint(
        repo_id=repo_id,
        huggingfacehub_api_token=token,
        task="text-generation",
        temperature=0.5,
        max_new_tokens=60,
        repetition_penalty=1.2,
        top_p=0.9,
    )

    _model = ChatHuggingFace(llm=llm)
    return _model


def _ensure_state():
    if "client_id" not in session:
        session["client_id"] = str(uuid.uuid4())

    if "mode" not in session:
        session["mode"] = "normal"

    if "chat_history" not in session:
        session["chat_history"] = [
            {"type": "system", "content": NORMAL_PROMPT},
        ]


def _get_history_objects():
    raw = session.get("chat_history", [])
    history = []

    for item in raw:
        t = item.get("type")
        content = item.get("content", "")
        if t == "system":
            history.append(SystemMessage(content=content))
        elif t == "human":
            history.append(HumanMessage(content=content))
        elif t == "ai":
            history.append(AIMessage(content=content))

    return history


def _save_history_objects(history):
    raw = []

    for msg in history:
        if isinstance(msg, SystemMessage):
            raw.append({"type": "system", "content": msg.content})
        elif isinstance(msg, HumanMessage):
            raw.append({"type": "human", "content": msg.content})
        elif isinstance(msg, AIMessage):
            raw.append({"type": "ai", "content": msg.content})

    session["chat_history"] = raw


def _fast_honeypot_reply(text):
    t = (text or "").lower()

    if "otp" in t:
        return "Ye kis cheez ka OTP hai?"
    if "kyc" in t:
        return "KYC kyun karni hai? Aap kaun bol rahe ho?"
    if "lottery" in t or "winner" in t or "reward" in t:
        return "Kaunsi lottery? Maine kahin naam nahi diya."
    if "link" in t or "click" in t:
        return "Link kaise? Mere phone me khulta nahi."
    if "bank" in t or "account" in t:
        return "Bank ka naam kya hai?"
    if "urgent" in t or "jaldi" in t:
        return "Aap itna jaldi kyun bol rahe ho?"

    options = [
        "Haan ji? Kaun bol rahe ho?",
        "Mujhe samajh nahi aaya, thoda sa dobara boliye?",
        "Ye baat aapko kaise pata?",
        "Main abhi dukaan pe hoon, baad me bolu?",
    ]
    return random.choice(options)


def _fast_normal_reply(text):
    t = (text or "").strip()
    if not t:
        return "Please type a message."
    return "OK. Aap thoda detail me batao?"


@app.get("/")
def index():
    _ensure_state()
    return render_template("index.html")


@app.post("/")
@require_api_key
def api_chat_root():
    return _handle_chat()


@app.get("/test")
def tester():
    # API Endpoint Tester page
    return render_template("test.html")


@app.get("/health")
def health():
    return jsonify({"status": "success", "reply": "ok"})


@app.get("/api/debug/auth")
def debug_auth():
    keys = _get_master_api_keys()

    def _mask(k: str) -> str:
        if not k:
            return ""
        if len(k) <= 8:
            return "***"
        return f"{k[:4]}***{k[-4:]}"

    return jsonify(
        {
            "has_master_key": bool(keys),
            "master_keys_count": len(keys),
            "master_keys_masked": [_mask(k) for k in keys],
            "master_keys_lengths": [len(k) for k in keys],
        }
    )


def _handle_chat():
    _ensure_state()

    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"status": "error", "error": "Empty message.", "reply": ""}), 400

    result = detect_scam(message)

    mode = session.get("mode", "normal")
    history = _get_history_objects()

    if result["is_scam"] and mode != "honeypot":
        mode = "honeypot"
        history = [SystemMessage(content=HONEYPOT_PROMPT)]

    session["mode"] = mode

    history.append(HumanMessage(content=message))

    fast_mode = os.environ.get("FAST_MODE", "0").strip() in {"1", "true", "yes", "on"}
    if fast_mode:
        reply = _fast_honeypot_reply(message) if mode == "honeypot" else _fast_normal_reply(message)
        history.append(AIMessage(content=reply))
        _save_history_objects(history)
        return jsonify(
            {
                "status": "success",
                "scam": result["is_scam"],
                "confidence": result["confidence"],
                "mode": mode,
                "reply": reply,
            }
        )

    if mode == "honeypot":
        reply = _fast_honeypot_reply(message)
        history.append(AIMessage(content=reply))
        _save_history_objects(history)
        return jsonify(
            {
                "status": "success",
                "scam": result["is_scam"],
                "confidence": result["confidence"],
                "mode": mode,
                "reply": reply,
            }
        )

    try:
        prompt = build_prompt(history)
        response = get_model().invoke(prompt)
        reply = getattr(response, "content", str(response))
    except Exception as e:
        msg = str(e)
        lower = msg.lower()

        reply = None
        warning = ""

        # Handle authentication/authorization errors
        if "401" in lower or "unauthorized" in lower or "403" in lower or "forbidden" in lower:
            error_type = "Authentication (401)" if "401" in lower else "Access Denied (403)"
            warning = (
                f"Hugging Face {error_type}. Check token/repo settings. "
                f"Falling back to a basic reply. Original error: {msg}"
            )
            # Use the fast, non-LLM replies as a fallback
            reply = _fast_honeypot_reply(message) if mode == "honeypot" else _fast_normal_reply(message)

        # Handle timeout errors
        elif "504" in lower or "gateway time-out" in lower or "gateway timeout" in lower:
            warning = f"Model timed out. Falling back to a basic reply. Original error: {msg}"
            if mode == "honeypot":
                reply = "Network slow hai. Aap phir se boliye?"
            else:
                reply = "I’m having trouble reaching the model right now. Please try again."

        # If we have a fallback reply, send it with a warning
        if reply is not None:
            history.append(AIMessage(content=reply))
            _save_history_objects(history)
            return jsonify({"status": "success", "scam": result["is_scam"], "confidence": result["confidence"], "mode": mode, "reply": reply, "warning": warning})

        # For all other unhandled exceptions, return a 500 error
        return jsonify({"status": "error", "error": f"An unexpected error occurred: {msg}", "reply": ""}), 500

    history.append(AIMessage(content=reply))
    _save_history_objects(history)


    return jsonify(
        {
            "status": "success",
            "scam": result["is_scam"],
            "confidence": result["confidence"],
            "mode": mode,
            "reply": reply,
        }
    )


@app.post("/chat")
def chat():
    return _handle_chat()


@app.post("/api/chat")
@require_api_key
def api_chat():
    return _handle_chat()


@app.post("/reset")
def reset():
    session.clear()
    return jsonify({"status": "success", "ok": True, "reply": ""})


@app.post("/api/reset")
@require_api_key
def api_reset():
    session.clear()
    return jsonify({"status": "success", "ok": True, "reply": ""})


@app.post("/api/keys/create")
def create_api_key():
    """Create a new API key"""
    api_key = secrets.token_urlsafe(32)
    payload = request.get_json(silent=True) or {}
    name = payload.get("name", "Unnamed Key")
    
    api_keys = load_api_keys()
    api_keys[api_key] = {
        "name": name,
        "created": datetime.now().isoformat(),
        "last_used": None,
        "active": True
    }
    save_api_keys(api_keys)
    
    return jsonify({
        "api_key": api_key,
        "name": name,
        "created": api_keys[api_key]["created"]
    }), 201


@app.get("/api/keys/list")
@require_api_key
def list_api_keys():
    """List all API keys (excluding the key value for security)"""
    api_keys = load_api_keys()
    keys_list = []
    
    for key, metadata in api_keys.items():
        keys_list.append({
            "key": key[:8] + "***" + key[-8:],  # Masked key
            "name": metadata.get("name", "Unnamed"),
            "created": metadata.get("created"),
            "last_used": metadata.get("last_used"),
            "active": metadata.get("active", True)
        })
    
    return jsonify({"keys": keys_list})


@app.delete("/api/keys/<key_id>")
@require_api_key
def delete_api_key(key_id):
    """Delete an API key"""
    api_keys = load_api_keys()
    
    if key_id not in api_keys:
        return jsonify({"error": "API key not found"}), 404
    
    del api_keys[key_id]
    save_api_keys(api_keys)
    
    return jsonify({"message": "API key deleted successfully"})


@app.post("/api/keys/validate")
def validate_api_key():
    """Validate an API key"""
    key = _extract_api_key(request)
    
    if not key:
        return jsonify({"valid": False, "error": "No API key provided"}), 400
    
    api_keys = load_api_keys()
    
    if key in api_keys and api_keys[key].get("active", True):
        return jsonify({
            "valid": True,
            "name": api_keys[key].get("name"),
            "created": api_keys[key].get("created")
        })
    
    return jsonify({"valid": False, "error": "Invalid or inactive API key"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
