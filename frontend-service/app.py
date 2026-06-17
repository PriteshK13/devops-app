import os

import httpx
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

ESTIMATION_SERVICE_URL = os.getenv("ESTIMATION_SERVICE_URL", "http://estimation-service:8001")
CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://chatbot-service:8002")

PORTFOLIO = [
    {
        "category": "Weddings",
        "icon": "💒",
        "title": "Dream Wedding Celebrations",
        "description": "From intimate garden ceremonies to grand ballroom receptions with bespoke floral design.",
        "highlights": ["Custom mandap & aisle decor", "Live band or DJ", "Cinematic videography"],
        "image_gradient": "linear-gradient(135deg, #fce4ec 0%, #f8bbd9 100%)",
    },
    {
        "category": "Corporate Events",
        "icon": "🏢",
        "title": "Corporate Excellence",
        "description": "Product launches, annual galas, and conferences executed with precision and polish.",
        "highlights": ["AV & stage production", "Branded experiences", "VIP guest management"],
        "image_gradient": "linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)",
    },
    {
        "category": "Birthdays",
        "icon": "🎂",
        "title": "Unforgettable Birthdays",
        "description": "Milestone celebrations tailored for kids, teens, and adults with themed experiences.",
        "highlights": ["Themed decor packages", "Entertainment acts", "Custom cake & dessert bars"],
        "image_gradient": "linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)",
    },
]


@app.route("/")
def index():
    return render_template("index.html", portfolio=PORTFOLIO)


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "frontend"})


@app.route("/api/proxy/estimate", methods=["POST"])
def proxy_estimate():
    data = request.get_json(silent=True) or {}
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(f"{ESTIMATION_SERVICE_URL}/api/estimate", json=data)
            return jsonify(response.json()), response.status_code
    except httpx.RequestError as exc:
        return jsonify({"Status": "Error", "detail": f"Estimation service unavailable: {exc}"}), 503


@app.route("/api/proxy/chatbot", methods=["POST"])
def proxy_chatbot():
    data = request.get_json(silent=True) or {}
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(f"{CHATBOT_SERVICE_URL}/api/chatbot", json=data)
            return jsonify(response.json()), response.status_code
    except httpx.RequestError as exc:
        return jsonify({"reply": "Sorry, the assistant is temporarily unavailable.", "detail": str(exc)}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.getenv("FLASK_DEBUG", "0") == "1")
