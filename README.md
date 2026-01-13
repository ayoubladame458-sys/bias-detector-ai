# BiasDetector - Détection Intelligente de Biais avec IA Locale

BiasDetector est un outil d'analyse de documents qui utilise l'Intelligence Artificielle **100% locale** pour détecter automatiquement différents types de biais dans les textes.

**Aucune clé API requise** - Tout fonctionne sur votre machine.

---

## Table des Matières

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation sur macOS](#installation-sur-macos)
- [Lancement du Projet](#lancement-du-projet)
- [Accès à l'Application](#accès-à-lapplication)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Dépannage](#dépannage)

---

## Fonctionnalités

- **Analyse de Documents** : Upload de PDF, TXT, DOCX avec détection de 6 types de biais
- **RAG (Retrieval Augmented Generation)** : Analyse contextuelle basée sur l'historique
- **Chat IA** : Posez des questions sur les patterns de biais détectés
- **Recherche Sémantique** : Trouvez des documents similaires par le sens
- **Statistiques** : Visualisez les tendances de biais dans vos documents
- **100% Privé** : Vos documents ne quittent jamais votre machine

### Types de Biais Détectés

| Biais | Description |
|-------|-------------|
| Genre | Stéréotypes basés sur le genre |
| Politique | Orientation politique partisane |
| Culturel | Ethnocentrisme, suppositions culturelles |
| Confirmation | Recherche d'infos confirmant ses croyances |
| Sélection | Cherry-picking de données |
| Ancrage | Dépendance excessive à l'info initiale |

---

## Prérequis

Avant de commencer, installez les logiciels suivants sur votre Mac :

| Logiciel | Version | Installation |
|----------|---------|--------------|
| **Python** | 3.11+ | `brew install python` ou [python.org](https://python.org) |
| **Node.js** | 18+ | `brew install node` ou [nodejs.org](https://nodejs.org) |
| **Docker Desktop** | Latest | [Télécharger Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| **Ollama** | Latest | [Télécharger Ollama](https://ollama.ai) |

### Vérifier les installations

```bash
python3 --version   # Doit afficher Python 3.11+
node --version      # Doit afficher v18+
docker --version    # Doit afficher Docker version 20+
ollama --version    # Doit afficher ollama version 0.x
```

---

## Installation sur macOS

### Étape 1 : Télécharger le projet

```bash
# Cloner le projet (ou télécharger le ZIP)
git clone <url-du-projet>
cd BiasDetector
```

### Étape 2 : Installer et configurer Ollama

```bash
# Télécharger les modèles requis
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

> **Note** : Le téléchargement peut prendre quelques minutes selon votre connexion.

### Étape 3 : Configurer le Backend

```bash
# Aller dans le dossier backend
cd backend

# Créer l'environnement virtuel Python
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### Étape 4 : Configurer le Frontend

```bash
# Aller dans le dossier frontend
cd ../frontend

# Installer les dépendances Node.js
npm install
```

---

## Lancement du Projet

### Ordre de lancement important

Lancez les services dans cet ordre :

### 1. Lancer Docker Desktop

Ouvrez l'application **Docker Desktop** et attendez que l'icône devienne verte (prêt).

### 2. Lancer MongoDB

```bash
# Dans un nouveau terminal
docker run -d -p 27017:27017 --name biasdetector-mongodb mongo:latest
```

> Si le conteneur existe déjà : `docker start biasdetector-mongodb`

### 3. Lancer Ollama

```bash
# Dans un nouveau terminal
ollama serve
```

> Laissez ce terminal ouvert. Ollama doit tourner en permanence.

### 4. Lancer le Backend

```bash
# Dans un nouveau terminal
cd BiasDetector/backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Attendez de voir :
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5. Lancer le Frontend

```bash
# Dans un nouveau terminal
cd BiasDetector/frontend
npm run dev
```

Attendez de voir :
```
✓ Ready in X.Xs
- Local: http://localhost:3000
```

> Si le port 3000 est occupé, Next.js utilisera automatiquement le port 3001.

---

## Accès à l'Application

Une fois tous les services lancés :

| Service | URL |
|---------|-----|
| **Application Web** | http://localhost:3000 (ou 3001) |
| **API Backend** | http://localhost:8000 |
| **Documentation API (Swagger)** | http://localhost:8000/docs |
| **Documentation API (ReDoc)** | http://localhost:8000/redoc |

---

## Configuration

### Variables d'environnement Backend

Le fichier `backend/.env` contient la configuration :

```env
# Ollama (IA locale)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=biasdetector

# RAG
RAG_ENABLED=True
RAG_MAX_CONTEXT_CHUNKS=5
RAG_RELEVANCE_THRESHOLD=0.7

# Fichiers
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=./uploads
```

### Changer de modèle Ollama

Pour utiliser un modèle différent :

```bash
# Télécharger un autre modèle
ollama pull mistral

# Modifier backend/.env
OLLAMA_MODEL=mistral
```

Modèles recommandés :
- `llama3.2:3b` - Équilibré (2GB) - **Recommandé**
- `mistral` - Très bon (4GB)
- `llama3.2` - Plus puissant (4GB)

---

## Architecture

```
BiasDetector/
├── backend/                 # API FastAPI (Python)
│   ├── app/
│   │   ├── api/endpoints/   # Routes API
│   │   ├── services/        # Logique métier
│   │   │   ├── ollama_service.py    # Service IA
│   │   │   ├── chroma_service.py    # Service LanceDB
│   │   │   ├── rag_service.py       # Service RAG
│   │   │   └── database_service.py  # Service MongoDB
│   │   └── models/          # Schémas Pydantic
│   ├── main.py              # Point d'entrée
│   ├── requirements.txt     # Dépendances Python
│   └── .env                 # Configuration
│
├── frontend/                # Interface Next.js (React)
│   ├── src/
│   │   ├── app/             # Pages
│   │   ├── components/      # Composants React
│   │   ├── hooks/           # Hooks personnalisés
│   │   └── lib/             # Utilitaires
│   └── package.json         # Dépendances Node.js
│
└── README.md                # Ce fichier
```

### Flux de données

```
[Document Upload] → [Extraction Texte] → [Chunking]
                                              ↓
[LanceDB] ← [Embeddings] ← [Ollama nomic-embed-text]
    ↓
[Recherche RAG] → [Contexte Similaire]
                        ↓
              [Ollama llama3.2] → [Analyse de Biais]
                                        ↓
                              [MongoDB] → [Résultats]
```

---

## Dépannage

### Docker ne démarre pas

**Problème** : `Cannot connect to Docker daemon`

**Solution** :
1. Ouvrez Docker Desktop manuellement
2. Attendez que l'icône devienne verte
3. Réessayez la commande

### Ollama ne répond pas

**Problème** : `Connection refused on port 11434`

**Solution** :
```bash
# Vérifier si Ollama tourne
curl http://localhost:11434/api/tags

# Si erreur, lancer Ollama
ollama serve
```

### Modèles Ollama manquants

**Problème** : `Model not found`

**Solution** :
```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### Port déjà utilisé

**Problème** : `Port 3000 is in use`

**Solution** : Next.js utilisera automatiquement le port 3001. Accédez à http://localhost:3001

Pour libérer le port manuellement :
```bash
# Trouver le processus
lsof -i :3000

# Tuer le processus (remplacer PID)
kill -9 <PID>
```

### MongoDB ne démarre pas

**Problème** : `Connection refused on port 27017`

**Solution** :
```bash
# Vérifier si le conteneur existe
docker ps -a | grep mongo

# Si existe mais arrêté
docker start biasdetector-mongodb

# Si n'existe pas, créer
docker run -d -p 27017:27017 --name biasdetector-mongodb mongo:latest
```

### Erreurs Python (ModuleNotFoundError)

**Solution** :
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Erreurs npm

**Solution** :
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Espace disque insuffisant

**Problème** : `No space left on device`

**Solution** :
```bash
# Nettoyer le cache pip
pip cache purge

# Nettoyer Docker
docker system prune -a

# Déplacer le projet sur un disque avec plus d'espace
```

---

## Script de Lancement Rapide (macOS)

Créez un fichier `start.sh` à la racine du projet :

```bash
#!/bin/bash

echo "=== BiasDetector - Démarrage ==="

# Vérifier Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker n'est pas démarré. Lancez Docker Desktop."
    exit 1
fi
echo "✅ Docker OK"

# Lancer MongoDB si pas déjà lancé
if ! docker ps | grep -q biasdetector-mongodb; then
    echo "🚀 Démarrage MongoDB..."
    docker run -d -p 27017:27017 --name biasdetector-mongodb mongo:latest 2>/dev/null || docker start biasdetector-mongodb
fi
echo "✅ MongoDB OK"

# Vérifier Ollama
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️  Ollama n'est pas démarré. Lancez 'ollama serve' dans un autre terminal."
    exit 1
fi
echo "✅ Ollama OK"

# Lancer Backend
echo "🚀 Démarrage Backend..."
cd backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

sleep 5

# Lancer Frontend
echo "🚀 Démarrage Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== BiasDetector est prêt ! ==="
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter tous les services"

# Attendre et nettoyer
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
```

Rendez-le exécutable et lancez-le :
```bash
chmod +x start.sh
./start.sh
```

---

## Utilisation

1. **Ouvrez** http://localhost:3000 dans votre navigateur
2. **Uploadez** un document (PDF, TXT, ou DOCX)
3. **Cliquez** sur "Analyze" pour lancer l'analyse
4. **Consultez** les biais détectés avec les citations et suggestions
5. **Utilisez** le chat RAG pour poser des questions sur vos analyses

---

## Licence

MIT License - Libre d'utilisation

---

Projet académique - Spécialisation IA&BD/CCV
