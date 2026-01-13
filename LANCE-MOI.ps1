# ============================================
# BiasDetector - SCRIPT COMPLET DE LANCEMENT
# ============================================
# Ce script fait TOUT automatiquement!

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "     BiasDetector - Lancement Automatique" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "C:\Users\youss\ProjetAyoub\BiasDetector"
Set-Location $projectRoot

# ============================================
# ETAPE 1: DOCKER & MONGODB
# ============================================
Write-Host "[1/5] Lancement de Docker et MongoDB..." -ForegroundColor Yellow

# Verifier si Docker est en cours d'execution
$dockerRunning = $false
try {
    docker info 2>&1 | Out-Null
    $dockerRunning = $true
    Write-Host "  Docker est deja en cours d'execution" -ForegroundColor Green
} catch {
    Write-Host "  Docker n'est pas lance. Demarrage..." -ForegroundColor Yellow

    # Chercher Docker Desktop
    $dockerPaths = @(
        "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe",
        "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe",
        "$env:LOCALAPPDATA\Docker\Docker Desktop.exe"
    )

    $dockerFound = $false
    foreach ($path in $dockerPaths) {
        if (Test-Path $path) {
            Write-Host "  Lancement de Docker Desktop..." -ForegroundColor White
            Start-Process $path
            $dockerFound = $true
            break
        }
    }

    if (-not $dockerFound) {
        Write-Host "  ERREUR: Docker Desktop n'est pas installe!" -ForegroundColor Red
        Write-Host "  Telechargez-le: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
        Write-Host ""
        Read-Host "  Appuyez sur Entree apres avoir installe Docker"
        exit
    }

    # Attendre que Docker soit pret (max 60 secondes)
    Write-Host "  Attente du demarrage de Docker (peut prendre 30-60 secondes)..." -ForegroundColor White
    $maxWait = 60
    $waited = 0
    while ($waited -lt $maxWait) {
        try {
            docker info 2>&1 | Out-Null
            $dockerRunning = $true
            Write-Host "  Docker est pret!" -ForegroundColor Green
            break
        } catch {
            Start-Sleep -Seconds 2
            $waited += 2
            Write-Host "." -NoNewline
        }
    }

    if (-not $dockerRunning) {
        Write-Host ""
        Write-Host "  Docker met trop de temps a demarrer." -ForegroundColor Yellow
        Write-Host "  Lancez Docker Desktop manuellement, puis relancez ce script." -ForegroundColor Yellow
        exit
    }
}

# Lancer MongoDB
Write-Host "  Demarrage de MongoDB..." -ForegroundColor White

# Arreter et supprimer l'ancien conteneur s'il existe
docker stop mongodb 2>&1 | Out-Null
docker rm mongodb 2>&1 | Out-Null

# Demarrer MongoDB
try {
    docker run -d -p 27017:27017 --name mongodb mongo:latest 2>&1 | Out-Null
    Write-Host "  MongoDB demarre sur le port 27017" -ForegroundColor Green
    Start-Sleep -Seconds 3
} catch {
    Write-Host "  Erreur lors du demarrage de MongoDB" -ForegroundColor Red
    Write-Host "  Verifiez que Docker fonctionne correctement" -ForegroundColor Yellow
}

# ============================================
# ETAPE 2: OLLAMA
# ============================================
Write-Host ""
Write-Host "[2/5] Verification d'Ollama..." -ForegroundColor Yellow

$ollamaRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue 2>&1
    $ollamaRunning = $true
    Write-Host "  Ollama est deja en cours d'execution" -ForegroundColor Green
} catch {
    Write-Host "  Ollama n'est pas lance. Demarrage..." -ForegroundColor Yellow

    # Lancer Ollama dans une nouvelle fenetre
    $ollamaScript = @"
Write-Host 'Ollama Server - Ne fermez pas cette fenetre' -ForegroundColor Cyan
Write-Host '===========================================' -ForegroundColor Cyan
ollama serve
"@
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $ollamaScript

    Write-Host "  Attente du demarrage d'Ollama (10 secondes)..." -ForegroundColor White
    Start-Sleep -Seconds 10

    # Verifier a nouveau
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue 2>&1
        Write-Host "  Ollama est pret!" -ForegroundColor Green
    } catch {
        Write-Host "  ATTENTION: Ollama ne repond pas" -ForegroundColor Yellow
        Write-Host "  L'application peut ne pas fonctionner correctement" -ForegroundColor Yellow
    }
}

# Verifier que les modeles sont installes
Write-Host "  Verification des modeles..." -ForegroundColor White
$modelsNeeded = @("llama3.2", "nomic-embed-text")
$modelsToDownload = @()

foreach ($model in $modelsNeeded) {
    try {
        $result = ollama list 2>&1 | Select-String $model
        if ($result) {
            Write-Host "    $model est installe" -ForegroundColor Green
        } else {
            $modelsToDownload += $model
        }
    } catch {
        $modelsToDownload += $model
    }
}

if ($modelsToDownload.Count -gt 0) {
    Write-Host "  Telechargement des modeles manquants..." -ForegroundColor Yellow
    foreach ($model in $modelsToDownload) {
        Write-Host "    Telechargement de $model (peut prendre quelques minutes)..." -ForegroundColor White
        ollama pull $model
    }
}

# ============================================
# ETAPE 3: PREPARATION DES FICHIERS
# ============================================
Write-Host ""
Write-Host "[3/5] Preparation des fichiers de configuration..." -ForegroundColor Yellow

# Backend .env
$backendEnv = "$projectRoot\backend\.env"
$backendEnvExample = "$projectRoot\backend\.env.example"
if (-not (Test-Path $backendEnv)) {
    if (Test-Path $backendEnvExample) {
        Copy-Item $backendEnvExample $backendEnv
        Write-Host "  Backend .env cree" -ForegroundColor Green
    }
} else {
    Write-Host "  Backend .env existe deja" -ForegroundColor Green
}

# Frontend .env.local
$frontendEnv = "$projectRoot\frontend\.env.local"
$frontendEnvExample = "$projectRoot\frontend\.env.example"
if (-not (Test-Path $frontendEnv)) {
    if (Test-Path $frontendEnvExample) {
        Copy-Item $frontendEnvExample $frontendEnv
        Write-Host "  Frontend .env.local cree" -ForegroundColor Green
    }
} else {
    Write-Host "  Frontend .env.local existe deja" -ForegroundColor Green
}

# ============================================
# ETAPE 4: BACKEND
# ============================================
Write-Host ""
Write-Host "[4/5] Lancement du Backend..." -ForegroundColor Yellow

$backendScript = @"
Set-Location '$projectRoot\backend'
`$host.UI.RawUI.WindowTitle = 'BiasDetector - Backend (Port 8000)'
Write-Host ''
Write-Host '================================================' -ForegroundColor Cyan
Write-Host '    BiasDetector Backend - FastAPI + Ollama' -ForegroundColor Cyan
Write-Host '================================================' -ForegroundColor Cyan
Write-Host ''
Write-Host '  Backend API: http://localhost:8000' -ForegroundColor White
Write-Host '  Docs: http://localhost:8000/docs' -ForegroundColor White
Write-Host ''

# Activer venv
& '.\venv\Scripts\Activate.ps1'

# Lancer uvicorn
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript
Write-Host "  Backend lance sur http://localhost:8000" -ForegroundColor Green
Start-Sleep -Seconds 3

# ============================================
# ETAPE 5: FRONTEND
# ============================================
Write-Host ""
Write-Host "[5/5] Lancement du Frontend..." -ForegroundColor Yellow

$frontendScript = @"
Set-Location '$projectRoot\frontend'
`$host.UI.RawUI.WindowTitle = 'BiasDetector - Frontend (Port 3000)'
Write-Host ''
Write-Host '================================================' -ForegroundColor Cyan
Write-Host '    BiasDetector Frontend - Next.js' -ForegroundColor Cyan
Write-Host '================================================' -ForegroundColor Cyan
Write-Host ''
Write-Host '  Application: http://localhost:3000' -ForegroundColor White
Write-Host ''

npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript
Write-Host "  Frontend lance sur http://localhost:3000" -ForegroundColor Green

# ============================================
# RESUME FINAL
# ============================================
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "     BiasDetector est pret!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Application:  http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  MongoDB:      Port 27017 (Docker)" -ForegroundColor Gray
Write-Host "  Ollama:       Port 11434" -ForegroundColor Gray
Write-Host ""
Write-Host "  Pour arreter: Fermez toutes les fenetres PowerShell" -ForegroundColor Yellow
Write-Host ""

# Attendre 5 secondes puis ouvrir le navigateur
Write-Host "  Ouverture du navigateur dans 5 secondes..." -ForegroundColor White
Start-Sleep -Seconds 5
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "  Appuyez sur une touche pour fermer cette fenetre..." -ForegroundColor Gray
Read-Host
