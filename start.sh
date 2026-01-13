#!/bin/bash

echo "=== BiasDetector - Démarrage ==="
echo ""

# Obtenir le répertoire du script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Vérifier Docker
echo "Vérification de Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker n'est pas démarré."
    echo "   Lancez Docker Desktop et réessayez."
    exit 1
fi
echo "✅ Docker OK"

# Lancer MongoDB si pas déjà lancé
echo "Vérification de MongoDB..."
if ! docker ps | grep -q biasdetector-mongodb; then
    echo "🚀 Démarrage MongoDB..."
    docker run -d -p 27017:27017 --name biasdetector-mongodb mongo:latest 2>/dev/null || docker start biasdetector-mongodb 2>/dev/null
    sleep 2
fi
echo "✅ MongoDB OK"

# Vérifier Ollama
echo "Vérification d'Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama n'est pas démarré."
    echo "   Lancez 'ollama serve' dans un autre terminal et réessayez."
    exit 1
fi
echo "✅ Ollama OK"

# Vérifier les modèles Ollama
echo "Vérification des modèles Ollama..."
if ! ollama list 2>/dev/null | grep -q "nomic-embed-text"; then
    echo "📥 Téléchargement de nomic-embed-text..."
    ollama pull nomic-embed-text
fi

# Lancer Backend
echo ""
echo "🚀 Démarrage du Backend..."
cd "$SCRIPT_DIR/backend"

if [ ! -d "venv" ]; then
    echo "   Création de l'environnement virtuel..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt > /dev/null 2>&1
else
    source venv/bin/activate
fi

./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

echo "   Attente du Backend..."
sleep 5

# Vérifier que le backend a démarré
if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "❌ Le Backend n'a pas démarré correctement."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi
echo "✅ Backend OK (http://localhost:8000)"

# Lancer Frontend
echo ""
echo "🚀 Démarrage du Frontend..."
cd "$SCRIPT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "   Installation des dépendances npm..."
    npm install > /dev/null 2>&1
fi

npm run dev &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

echo "   Attente du Frontend..."
sleep 10

echo ""
echo "============================================"
echo "   BiasDetector est prêt !"
echo "============================================"
echo ""
echo "   Frontend:  http://localhost:3000"
echo "              (ou http://localhost:3001 si port 3000 occupé)"
echo ""
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "   Appuyez sur Ctrl+C pour arrêter"
echo "============================================"
echo ""

# Ouvrir le navigateur
if command -v open &> /dev/null; then
    sleep 2
    open http://localhost:3000 2>/dev/null || open http://localhost:3001 2>/dev/null
fi

# Attendre et nettoyer à la fin
cleanup() {
    echo ""
    echo "Arrêt des services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Au revoir!"
}

trap cleanup EXIT
wait
