import requests
import random
import string
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

PASSWORD = "Temp@2025!"

def random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
def generate():
    try:
        domain_res = requests.get("https://api.mail.tm/domains").json()
        domains = [d["domain"] for d in domain_res["hydra:member"]]
        com_domains = [d for d in domains if d.endswith(".com")]
        domain = random.choice(com_domains if com_domains else domains)
        email = random_string() + "@" + domain

        requests.post(
            "https://api.mail.tm/accounts",
            json={"address": email, "password": PASSWORD}
        )

        login = requests.post(
            "https://api.mail.tm/token",
            json={"address": email, "password": PASSWORD}
        )
        token = login.json().get("token")

        if not token:
            return jsonify({"error": "Failed to get token"}), 500

        return jsonify({"email": email, "token": token})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/messages", methods=["GET"])
def get_messages():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return jsonify({"error": "No token"}), 401
    try:
        res = requests.get(
            "https://api.mail.tm/messages",
            headers={"Authorization": f"Bearer {token}"}
        )
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/messages/<msg_id>", methods=["GET"])
def get_message(msg_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return jsonify({"error": "No token"}), 401
    try:
        res = requests.get(
            f"https://api.mail.tm/messages/{msg_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)