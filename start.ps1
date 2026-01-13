# ============================================
# BiasDetector - Script de demarrage complet
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   BiasDetector - Demarrage Automatique" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verification de Docker
Write-Host "[1/5] Verification de Docker..." -ForegroundColor Yellow
$dockerRunning = $false
try {
    docker ps 2>$null | Out-Null
    $dockerRunning = $true
    Write-Host "  Docker est en cours d'execution" -ForegroundColor Green
} catch {
    Write-Host "  Docker n'est pas lance. Lancement..." -ForegroundColor Yellow
    Start-Process "Docker Desktop" -ErrorAction SilentlyContinue
    Write-Host "  Attente du demarrage de Docker (30 secondes)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}

# Demarrage de MongoDB via Docker
Write-Host ""
Write-Host "[2/5] Demarrage de MongoDB..." -ForegroundColor Yellow
$mongoRunning = docker ps --filter "name=mongodb" --format "{{.Names}}" 2>$null
if ($mongoRunning -eq "mongodb") {
    Write-Host "  MongoDB est deja en cours d'execution" -ForegroundColor Green
} else {
    # Supprimer le conteneur existant s'il existe
    docker rm -f mongodb 2>$null | Out-Null
    # Demarrer MongoDB
    docker run -d -p 27017:27017 --name mongodb mongo:latest 2>$null | Out-Null
    Write-Host "  MongoDB demarre sur le port 27017" -ForegroundColor Green
}

# Verification d'Ollama
Write-Host ""
Write-Host "[3/5] Verification d'Ollama..." -ForegroundColor Yellow
$ollamaRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
    $ollamaRunning = $true
    Write-Host "  Ollama est en cours d'execution" -ForegroundColor Green
} catch {
    Write-Host "  Ollama n'est pas lance!" -ForegroundColor Red
    Write-Host "  Veuillez lancer Ollama manuellement:" -ForegroundColor Yellow
    Write-Host "    1. Ouvrez un nouveau terminal" -ForegroundColor White
    Write-Host "    2. Tapez: ollama serve" -ForegroundColor White
    Write-Host ""
    Write-Host "  Puis dans un autre terminal, telecharger les modeles:" -ForegroundColor Yellow
    Write-Host "    ollama pull llama3.2" -ForegroundColor White
    Write-Host "    ollama pull nomic-embed-text" -ForegroundColor White
    Write-Host ""
    Read-Host "  Appuyez sur Entree une fois Ollama lance"
}

# Demarrage du Backend
Write-Host ""
Write-Host "[4/5] Demarrage du Backend FastAPI..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "backend"
$venvPath = Join-Path $backendPath "venv\Scripts\Activate.ps1"

# Creer le fichier .env s'il n'existe pas
$envPath = Join-Path $backendPath ".env"
$envExamplePath = Join-Path $backendPath ".env.example"
if (-not (Test-Path $envPath)) {
    if (Test-Path $envExamplePath) {
        Copy-Item $envExamplePath $envPath
        Write-Host "  Fichier .env cree" -ForegroundColor Green
    }
}

# Lancer le backend dans une nouvelle fenetre
$backendScript = @"
Set-Location '$backendPath'
& '$venvPath'
Write-Host 'Backend BiasDetector - Port 8000' -ForegroundColor Cyan
Write-Host '================================' -ForegroundColor Cyan
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript
Write-Host "  Backend lance sur http://localhost:8000" -ForegroundColor Green

# Demarrage du Frontend
Write-Host ""
Write-Host "[5/5] Demarrage du Frontend Next.js..." -ForegroundColor Yellow
$frontendPath = Join-Path $PSScriptRoot "frontend"

# Creer le fichier .env.local s'il n'existe pas
$envLocalPath = Join-Path $frontendPath ".env.local"
$envExampleFrontPath = Join-Path $frontendPath ".env.example"
if (-not (Test-Path $envLocalPath)) {
    if (Test-Path $envExampleFrontPath) {
        Copy-Item $envExampleFrontPath $envLocalPath
        Write-Host "  Fichier .env.local cree" -ForegroundColor Green
    }
}

# Lancer le frontend dans une nouvelle fenetre
$frontendScript = @"
Set-Location '$frontendPath'
Write-Host 'Frontend BiasDetector - Port 3000' -ForegroundColor Cyan
Write-Host '==================================' -ForegroundColor Cyan
npm run dev
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript
Write-Host "  Frontend lance sur http://localhost:3000" -ForegroundColor Green

# Resume
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   BiasDetector est pret!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Pour arreter: fermez les fenetres PowerShell" -ForegroundColor Yellow
Write-Host ""

# Ouvrir le navigateur
Start-Sleep -Seconds 5
Start-Process "http://localhost:3000"
