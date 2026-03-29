import json
import os
import sys
import threading
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "checklist_data.json")

DEFAULT_DATA = {
    "categories": [
        {
            "id": "fondamentaux",
            "title": "A. Fondamentaux Backend (non négociables)",
            "icon": "🧠",
            "color": "#6366f1",
            "skills": [
                {"id": "http_rest", "text": "HTTP / REST / Architecture Web", "checked": False, "note": ""},
                {"id": "concurrency", "text": "Concurrency (threads, async, workers)", "checked": False, "note": ""},
                {"id": "transactions_db", "text": "Transactions DB / Isolation levels", "checked": False, "note": ""},
                {"id": "scalabilite", "text": "Scalabilité (horizontal vs vertical)", "checked": False, "note": ""},
                {"id": "cache", "text": "Cache (Redis, stratégie d'invalidation)", "checked": False, "note": ""},
                {"id": "securite_base", "text": "Sécurité (auth, CSRF, XSS, injections)", "checked": False, "note": ""},
                {"id": "design_patterns", "text": "Design patterns (services, repository, etc.)", "checked": False, "note": ""}
            ]
        },
        {
            "id": "django_profond",
            "title": "B. Django Profond (pas juste CRUD)",
            "icon": "⚙️",
            "color": "#059669",
            "skills": [
                {"id": "django_orm", "text": "Django ORM (optimisation, annotate, select_related, prefetch_related)", "checked": False, "note": ""},
                {"id": "django_signals", "text": "Django signals (quand les éviter surtout)", "checked": False, "note": ""},
                {"id": "middleware", "text": "Middleware (custom logic)", "checked": False, "note": ""},
                {"id": "django_channels", "text": "Django Channels / Async", "checked": False, "note": ""},
                {"id": "permissions_auth", "text": "Permissions & auth custom", "checked": False, "note": ""},
                {"id": "archi_propre", "text": "Architecture propre (pas tout dans views.py)", "checked": False, "note": ""}
            ]
        },
        {
            "id": "celery_redis",
            "title": "C. Celery / Redis / Async",
            "icon": "🚀",
            "color": "#dc2626",
            "skills": [
                {"id": "queue_mgmt", "text": "Queue management", "checked": False, "note": ""},
                {"id": "retry_strategy", "text": "Retry strategy", "checked": False, "note": ""},
                {"id": "idempotence", "text": "Idempotence", "checked": False, "note": ""},
                {"id": "monitoring_tasks", "text": "Monitoring des tasks", "checked": False, "note": ""},
                {"id": "celery_beat", "text": "Scheduling (Celery Beat)", "checked": False, "note": ""},
                {"id": "failure_mgmt", "text": "Gestion des failures", "checked": False, "note": ""}
            ]
        },
        {
            "id": "archi_prod",
            "title": "D. Architecture & Production",
            "icon": "🏗️",
            "color": "#ea580c",
            "skills": [
                {"id": "mono_vs_micro", "text": "Monolithe vs Microservices", "checked": False, "note": ""},
                {"id": "docker", "text": "Docker / Orchestration", "checked": False, "note": ""},
                {"id": "ci_cd", "text": "CI/CD", "checked": False, "note": ""},
                {"id": "logs_monitoring", "text": "Logs / Monitoring", "checked": False, "note": ""},
                {"id": "migrations_prod", "text": "Gestion des migrations en prod", "checked": False, "note": ""}
            ]
        },
        {
            "id": "securite_robustesse",
            "title": "E. Sécurité & Robustesse",
            "icon": "🔐",
            "color": "#7c3aed",
            "skills": [
                {"id": "jwt_vs_session", "text": "JWT vs Session auth", "checked": False, "note": ""},
                {"id": "rate_limiting", "text": "Rate limiting", "checked": False, "note": ""},
                {"id": "protection_api", "text": "Protection API publique", "checked": False, "note": ""},
                {"id": "gestion_secrets", "text": "Gestion des secrets", "checked": False, "note": ""},
                {"id": "audit_logging", "text": "Audit / Logging", "checked": False, "note": ""}
            ]
        },
        {
            "id": "vision_engineering",
            "title": "F. Vision Engineering (Ingénieur Logiciel)",
            "icon": "🔬",
            "color": "#0891b2",
            "skills": [
                {"id": "tradeoffs", "text": "Arbitrages (Trade-offs) : savoir expliquer pourquoi choisir une techno plutôt qu'une autre", "checked": False, "note": ""},
                {"id": "tests", "text": "Fiabilité & Tests : unitaires, intégration, charge", "checked": False, "note": ""},
                {"id": "maintenabilite", "text": "Maintenabilité : garantir la qualité long terme du code", "checked": False, "note": ""},
                {"id": "infra_devops", "text": "Infrastructure & DevOps : CI/CD, Docker, Kubernetes, observabilité", "checked": False, "note": ""},
                {"id": "design_systeme", "text": "Design Système : découper un projet complexe, anticiper les échecs", "checked": False, "note": ""},
                {"id": "methodologies", "text": "Méthodologies de conception (DDD, Clean Architecture, SOLID)", "checked": False, "note": ""}
            ]
        },
        {
            "id": "leadership_senior",
            "title": "G. Leadership & Impact (Senior)",
            "icon": "👑",
            "color": "#ca8a04",
            "skills": [
                {"id": "mentorat", "text": "Mentorat : guider les juniors, revues de code constructives", "checked": False, "note": ""},
                {"id": "autonomie", "text": "Autonomie totale sur des projets complexes", "checked": False, "note": ""},
                {"id": "vision_produit", "text": "Vision produit : comprendre le business, pas juste le code", "checked": False, "note": ""},
                {"id": "soft_skills", "text": "Soft Skills : communication avec non-techniques (PO, clients)", "checked": False, "note": ""},
                {"id": "traduire_besoins", "text": "Traduire des besoins business en solutions techniques", "checked": False, "note": ""},
                {"id": "estimation", "text": "Estimation réaliste des délais et complexité", "checked": False, "note": ""},
                {"id": "documentation", "text": "Documentation technique claire et maintenue", "checked": False, "note": ""}
            ]
        }
    ]
}


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    save_data(DEFAULT_DATA)
    return DEFAULT_DATA


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def get_data():
    return jsonify(load_data())


@app.route("/api/toggle", methods=["POST"])
def toggle_skill():
    payload = request.json
    cat_id = payload["category_id"]
    skill_id = payload["skill_id"]
    data = load_data()
    for cat in data["categories"]:
        if cat["id"] == cat_id:
            for skill in cat["skills"]:
                if skill["id"] == skill_id:
                    skill["checked"] = not skill["checked"]
                    break
            break
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/note", methods=["POST"])
def update_note():
    payload = request.json
    cat_id = payload["category_id"]
    skill_id = payload["skill_id"]
    note = payload["note"]
    data = load_data()
    for cat in data["categories"]:
        if cat["id"] == cat_id:
            for skill in cat["skills"]:
                if skill["id"] == skill_id:
                    skill["note"] = note
                    break
            break
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/add_skill", methods=["POST"])
def add_skill():
    payload = request.json
    cat_id = payload["category_id"]
    text = payload["text"].strip()
    if not text:
        return jsonify({"error": "Texte vide"}), 400
    data = load_data()
    for cat in data["categories"]:
        if cat["id"] == cat_id:
            new_id = text.lower().replace(" ", "_").replace("/", "_")[:30] + f"_{len(cat['skills'])}"
            cat["skills"].append({"id": new_id, "text": text, "checked": False, "note": ""})
            break
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/add_category", methods=["POST"])
def add_category():
    payload = request.json
    title = payload["title"].strip()
    icon = payload.get("icon", "📌")
    color = payload.get("color", "#6b7280")
    if not title:
        return jsonify({"error": "Titre vide"}), 400
    data = load_data()
    new_id = title.lower().replace(" ", "_").replace("/", "_")[:30]
    data["categories"].append({
        "id": new_id,
        "title": title,
        "icon": icon,
        "color": color,
        "skills": []
    })
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/delete_skill", methods=["POST"])
def delete_skill():
    payload = request.json
    cat_id = payload["category_id"]
    skill_id = payload["skill_id"]
    data = load_data()
    for cat in data["categories"]:
        if cat["id"] == cat_id:
            cat["skills"] = [s for s in cat["skills"] if s["id"] != skill_id]
            break
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/reset", methods=["POST"])
def reset_data():
    save_data(DEFAULT_DATA)
    return jsonify({"ok": True})


def start_server():
    app.run(host="127.0.0.1", port=5555, debug=False, use_reloader=False)


if __name__ == "__main__":
    import webview

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    webview.create_window(
        "Senior Dev Checklist",
        "http://127.0.0.1:5555",
        width=1000,
        height=750,
        min_size=(600, 400),
        text_select=True,
    )
    webview.start()
    sys.exit(0)
