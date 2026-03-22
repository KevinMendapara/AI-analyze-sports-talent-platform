from flask import Flask, render_template, request, jsonify, session
import json, random, time, os

app = Flask(__name__)
app.secret_key = "talentscout_secret_2024"

# In-memory user store (demo)
USERS = {}

# ── Auth routes ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    if not all([data.get("fullName"), email, data.get("phone"),
                data.get("bloodGroup"), data.get("password")]):
        return jsonify({"ok": False, "msg": "All fields are required."}), 400
    if email in USERS:
        return jsonify({"ok": False, "msg": "Email already registered."}), 409
    USERS[email] = {
        "fullName": data["fullName"],
        "email": email,
        "phone": data["phone"],
        "bloodGroup": data["bloodGroup"],
        "password": data["password"],
    }
    session["user"] = USERS[email]
    return jsonify({"ok": True, "user": {k: v for k, v in USERS[email].items() if k != "password"}})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"ok": False, "msg": "Please enter your credentials."}), 400
    # Demo: accept any credentials, create user if not exists
    if email not in USERS:
        USERS[email] = {
            "fullName": email.split("@")[0].title(),
            "email": email,
            "phone": "+91 9000000000",
            "bloodGroup": "O+",
            "password": password,
        }
    elif USERS[email]["password"] != password:
        return jsonify({"ok": False, "msg": "Invalid password."}), 401
    session["user"] = USERS[email]
    return jsonify({"ok": True, "user": {k: v for k, v in USERS[email].items() if k != "password"}})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/me")
def me():
    user = session.get("user")
    if not user:
        return jsonify({"ok": False}), 401
    return jsonify({"ok": True, "user": {k: v for k, v in user.items() if k != "password"}})

# ── Analysis route ────────────────────────────────────────────────────────────

@app.route("/api/analyze", methods=["POST"])
def analyze():
    video_type = request.form.get("videoType", "Batting")

    if video_type == "Batting":
        report = {
            "type": "Batting",
            "overallScore": random.randint(81, 92),
            "footworkAccuracy": random.randint(82, 94),
            "batSpeed": random.randint(128, 148),
            "shotSelectionGrade": random.choice(["A", "A−", "B+", "B"]),
            "elbowExtension": random.randint(88, 96),
            "backswingAngle": random.randint(38, 48),
            "weightTransfer": random.randint(78, 90),
            "followThrough": random.randint(72, 88),
            "creasePosition": "Off-stump guard, 8cm ahead of crease",
            "radarData": [
                {"metric": "Footwork",   "value": random.randint(78, 95)},
                {"metric": "Bat Speed",  "value": random.randint(75, 92)},
                {"metric": "Shot Select","value": random.randint(72, 90)},
                {"metric": "Timing",     "value": random.randint(82, 96)},
                {"metric": "Balance",    "value": random.randint(78, 93)},
                {"metric": "Eye-Line",   "value": random.randint(80, 95)},
            ],
            "timeline": [
                {"frame": f"{i*0.2:.1f}s", "score": random.randint(60 + i*4, 70 + i*4)}
                for i in range(8)
            ],
            "keyframes": [
                {"label": "Stance",         "score": random.randint(82,94), "note": "Open stance, slight inside-edge risk"},
                {"label": "Pickup",         "score": random.randint(85,96), "note": "High backlift — aggressive intent detected"},
                {"label": "Impact",         "score": random.randint(80,92), "note": "Bat face slightly closed at contact"},
                {"label": "Follow-through", "score": random.randint(72,85), "note": "Truncated swing detected — power leak ~12%"},
            ],
            "coachNotes": [
                {"type": "ok",   "title": "Crease Position",    "note": "Off-stump guard, 8cm ahead of crease. Ideal for pace attack."},
                {"type": "warn", "title": "Follow-through",     "note": "Truncated swing costs ~12% power efficiency. Drill: shadow batting with full extension."},
                {"type": "ok",   "title": "Eye-Line Discipline","note": "Head remains still through 94% of analysed deliveries."},
            ],
        }
    else:
        pace = random.randint(130, 145)
        report = {
            "type": "Bowling",
            "overallScore": random.randint(79, 90),
            "releasePAngle": round(random.uniform(22.0, 28.0), 1),
            "estimatedPace": pace,
            "lineLengthConsistency": random.randint(74, 88),
            "seamPosition": random.randint(90, 98),
            "runUpEfficiency": random.randint(76, 88),
            "hyperextension": round(random.uniform(4.0, 11.0), 1),
            "wristPosition": "Classic side-on, pronated at release",
            "landingZone": "Good length — 68% in optimal corridor",
            "radarData": [
                {"metric": "Pace",     "value": random.randint(78, 92)},
                {"metric": "Accuracy", "value": random.randint(72, 88)},
                {"metric": "Seam",     "value": random.randint(88, 98)},
                {"metric": "Run-up",   "value": random.randint(75, 90)},
                {"metric": "Wrist",    "value": random.randint(70, 85)},
                {"metric": "Action",   "value": random.randint(82, 94)},
            ],
            "timeline": [
                {"frame": f"{i*0.3:.1f}s", "score": random.randint(55 + i*5, 65 + i*5)}
                for i in range(8)
            ],
            "keyframes": [
                {"label": "Run-up",         "score": random.randint(78,90), "note": "Rhythm break at 4th stride — minor"},
                {"label": "Load",           "score": random.randint(84,95), "note": "Full rotation — excellent hip-shoulder separation"},
                {"label": "Release",        "score": random.randint(86,96), "note": f"Optimal wrist-cock angle"},
                {"label": "Follow-through", "score": random.randint(72,85), "note": "Front leg not fully braced — injury risk flagged"},
            ],
            "coachNotes": [
                {"type": "ok",   "title": "Wrist Position",    "note": "Classic side-on, pronated at release. High swing probability in overcast conditions."},
                {"type": "warn", "title": "Front Leg Brace",   "note": "Incomplete bracing increases lumbar load. Physio assessment recommended."},
                {"type": "ok",   "title": "Landing Zone",      "note": "Good length — 68% in optimal corridor. Effective for inducing false shots."},
            ],
        }

    return jsonify({"ok": True, "report": report})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
