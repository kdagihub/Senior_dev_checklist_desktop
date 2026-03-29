# Senior Dev Checklist

Application desktop locale permettant de suivre et valider les compétences indispensables pour prétendre au titre de **Développeur Senior Backend / Fullstack** ou **Ingénieur Logiciel**.

Construite avec **Flask** (backend) + **pywebview** (fenêtre native) + **HTML/CSS/JS** (interface).

---

## Apercu

| Fonctionnalite | Detail |
|---|---|
| Checklist interactive | Cocher/decocher chaque competence maitrisee |
| Barre de progression | Globale + par categorie, mise a jour en temps reel |
| Niveau estime | Junior / Mid-Level / Mid-Senior / Senior / Staff |
| Notes personnelles | Ajouter des notes libres sur chaque competence |
| Categories personnalisables | Ajouter/supprimer des categories et competences |
| Filtres | Toutes / Non maitrisees / Maitrisees |
| Persistance locale | Donnees sauvegardees dans un fichier JSON local |
| Fenetre native | S'ouvre dans sa propre fenetre (pas dans le navigateur) |

---

## Categories de competences incluses

L'application est pre-configuree avec **7 domaines**, **42 competences** :

| # | Categorie | Exemples |
|---|---|---|
| A | **Fondamentaux Backend** | HTTP/REST, Concurrency, Transactions DB, Cache Redis, Securite |
| B | **Django Profond** | ORM avance, Signals, Middleware, Channels, Architecture propre |
| C | **Celery / Redis / Async** | Queue management, Retry, Idempotence, Celery Beat |
| D | **Architecture & Production** | Docker, CI/CD, Monitoring, Migrations en prod |
| E | **Securite & Robustesse** | JWT vs Session, Rate limiting, Gestion des secrets |
| F | **Vision Engineering** | Trade-offs, Tests, Design Systeme, SOLID/DDD |
| G | **Leadership & Impact Senior** | Mentorat, Autonomie, Soft Skills, Vision produit |

Toutes les categories et competences sont modifiables directement depuis l'interface.

---

## Pre-requis

- **Python 3.10+**
- **Linux** : paquet `python3-gi` (PyGObject) et `gir1.2-webkit2-4.1` installes au niveau systeme
- **Windows** : aucune dependance systeme supplementaire (pywebview utilise EdgeChromium)
- **macOS** : aucune dependance systeme supplementaire (pywebview utilise WebKit)

### Verifier les pre-requis sur Linux (Ubuntu/Debian)

```bash
python3 --version                          # Python 3.10+
dpkg -l | grep python3-gi                  # PyGObject
dpkg -l | grep gir1.2-webkit2-4.1          # WebKit bindings
```

Si manquant :

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-webkit2-4.1
```

---

## Installation

### 1. Cloner le depot

```bash
git clone https://github.com/kdagihub/Senior_dev_checklist_desktop.git
cd Senior_dev_checklist_desktop
```

### 2. Creer l'environnement virtuel

Sur **Linux** (necessite `--system-site-packages` pour acceder a PyGObject) :

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
```

Sur **Windows** :

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Sur **macOS** :

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Lancer l'application

```bash
python3 app.py
```

Ou sur Linux, utiliser le script :

```bash
chmod +x run.sh
./run.sh
```

L'application s'ouvre dans une fenetre native.

---

## Raccourci bureau (Linux)

Pour creer une icone cliquable sur le bureau :

1. Copier le fichier `.desktop` :

```bash
cp SeniorDevChecklist.desktop ~/Bureau/
# ou
cp SeniorDevChecklist.desktop ~/Desktop/
```

2. Le rendre executable et approuve :

```bash
chmod +x ~/Bureau/SeniorDevChecklist.desktop
gio set ~/Bureau/SeniorDevChecklist.desktop metadata::trusted true
```

3. **Clic droit** sur l'icone > **Autoriser le lancement** (GNOME).

> **Note :** Adapter les chemins absolus dans le fichier `.desktop` (`Exec=` et `Icon=`) si le projet n'est pas dans `~/Bureau/senior_dev_chcklist/`.

---

## Arborescence du projet

```
Senior_dev_checklist_desktop/
├── app.py                     # Backend Flask + lancement pywebview
├── templates/
│   └── index.html             # Interface complete (HTML + CSS + JS)
├── checklist_data.json        # Donnees utilisateur (auto-genere, gitignore)
├── requirements.txt           # Dependances Python
├── run.sh                     # Script de lancement Linux
├── icon.svg                   # Icone source (vectoriel)
├── icon.png                   # Icone 128x128 (pour .desktop)
├── SeniorDevChecklist.desktop # Raccourci bureau Linux
├── .gitignore
└── README.md
```

---

## Architecture technique

### Backend — `app.py`

Serveur Flask minimaliste exposant une API REST JSON :

| Methode | Route | Description |
|---|---|---|
| `GET` | `/` | Sert la page HTML principale |
| `GET` | `/api/data` | Retourne toutes les categories et competences |
| `POST` | `/api/toggle` | Coche/decoche une competence |
| `POST` | `/api/note` | Met a jour la note d'une competence |
| `POST` | `/api/add_skill` | Ajoute une competence a une categorie |
| `POST` | `/api/add_category` | Cree une nouvelle categorie |
| `POST` | `/api/delete_skill` | Supprime une competence |
| `POST` | `/api/reset` | Reinitialise toutes les donnees par defaut |

Les donnees sont persistees dans `checklist_data.json` (fichier JSON local, auto-genere au premier lancement).

### Frontend — `templates/index.html`

Application single-page (SPA) en vanilla JS :

- Interface dark theme responsive
- Appels `fetch()` vers l'API Flask
- Mise a jour du DOM sans rechargement de page
- Zero dependance externe (pas de framework JS)

### Fenetre native — pywebview

`pywebview` cree une fenetre desktop qui pointe vers le serveur Flask local (`http://127.0.0.1:5555`). Le serveur Flask tourne dans un thread daemon, et la fenetre pywebview gere la boucle d'evenements principale.

---

## Reutiliser pour un autre projet Flask

Cette application peut servir de **template** pour n'importe quelle app desktop locale basee sur Flask :

### 1. Structure a reprendre

```python
import threading, sys
from flask import Flask

app = Flask(__name__)

def start_server():
    app.run(host="127.0.0.1", port=5555, debug=False, use_reloader=False)

if __name__ == "__main__":
    import webview

    # Flask dans un thread daemon
    threading.Thread(target=start_server, daemon=True).start()

    # Fenetre native
    webview.create_window("Mon App", "http://127.0.0.1:5555", width=1000, height=750)
    webview.start()
    sys.exit(0)
```

### 2. Points cles

- **`use_reloader=False`** est obligatoire : le reloader de Flask entre en conflit avec pywebview.
- **`daemon=True`** sur le thread Flask : il se termine automatiquement quand la fenetre se ferme.
- **`sys.exit(0)`** apres `webview.start()` : assure que le processus se termine proprement.
- Sur Linux, le venv doit etre cree avec **`--system-site-packages`** pour acceder a PyGObject (GTK).

### 3. Persistance des donnees

Le pattern utilise ici (lecture/ecriture JSON) est suffisant pour une app locale mono-utilisateur. Pour un projet plus complexe, remplacer par SQLite :

```python
import sqlite3

def get_db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn
```

### 4. Packaging en executable

Pour distribuer l'app sans que l'utilisateur ait besoin de Python :

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "templates:templates" app.py
```

L'executable se trouvera dans `dist/app`.

---

## Personnalisation

### Modifier les competences par defaut

Editer le dictionnaire `DEFAULT_DATA` dans `app.py`. Chaque categorie suit ce format :

```python
{
    "id": "identifiant_unique",
    "title": "Titre affiche",
    "icon": "emoji",
    "color": "#hexcolor",
    "skills": [
        {"id": "skill_id", "text": "Description", "checked": False, "note": ""}
    ]
}
```

### Reinitialiser les donnees

Supprimer `checklist_data.json` et relancer l'app, ou utiliser l'endpoint :

```bash
curl -X POST http://127.0.0.1:5555/api/reset
```

---

## Contribuer

1. Fork le projet
2. Creer une branche (`git checkout -b feature/ma-feature`)
3. Commit (`git commit -m "Ajout de ma feature"`)
4. Push (`git push origin feature/ma-feature`)
5. Ouvrir une Pull Request

---

## Licence

Ce projet est open-source. Libre a vous de l'utiliser, le modifier et le redistribuer.
