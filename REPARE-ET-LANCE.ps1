# ============================================
# BiasDetector - REPARATION ET LANCEMENT
# ============================================

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "     BiasDetector - Reparation et Lancement" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "C:\Users\youss\ProjetAyoub\BiasDetector"
Set-Location $projectRoot

# ============================================
# ETAPE 1: ARRETER LES PROCESSUS EXISTANTS
# ============================================
Write-Host "[1/6] Arret des processus existants..." -ForegroundColor Yellow

# Arreter MongoDB s'il tourne
try {
    docker stop mongodb 2>&1 | Out-Null
    Write-Host "  MongoDB arrete" -ForegroundColor Green
} catch {
    Write-Host "  MongoDB n'etait pas en cours" -ForegroundColor Gray
}

Write-Host "  Processus arretes" -ForegroundColor Green

# ============================================
# ETAPE 2: INSTALLER TAILWINDCSS-ANIMATE
# ============================================
Write-Host ""
Write-Host "[2/6] Installation de tailwindcss-animate..." -ForegroundColor Yellow
Set-Location "$projectRoot\frontend"
npm install tailwindcss-animate@^1.0.7
Write-Host "  tailwindcss-animate installe!" -ForegroundColor Green

# ============================================
# ETAPE 3: DOCKER & MONGODB
# ============================================
Write-Host ""
Write-Host "[3/6] Lancement de MongoDB..." -ForegroundColor Yellow
Set-Location $projectRoot

# Verifier si Docker est en cours
$dockerRunning = $false
try {
    docker info 2>&1 | Out-Null
    $dockerRunning = $true
    Write-Host "  Docker est en cours d'execution" -ForegroundColor Green
} catch {
    Write-Host "  Docker n'est pas lance!" -ForegroundColor Red
    Write-Host "  Lancez Docker Desktop manuellement puis relancez ce script" -ForegroundColor Yellow
    Read-Host "  Appuyez sur Entree pour quitter"
    exit
}

# Lancer MongoDB
try {
    docker rm mongodb 2>&1 | Out-Null
    docker run -d -p 27017:27017 --name mongodb mongo:latest 2>&1 | Out-Null
    Write-Host "  MongoDB demarre sur le port 27017" -ForegroundColor Green
    Start-Sleep -Seconds 3
} catch {
    Write-Host "  Erreur lors du demarrage de MongoDB" -ForegroundColor Red
}

# ============================================
# ETAPE 4: OLLAMA
# ============================================
Write-Host ""
Write-Host "[4/6] Verification d'Ollama..." -ForegroundColor Yellow

$ollamaRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue 2>&1
    $ollamaRunning = $true
    Write-Host "  Ollama est deja en cours d'execution" -ForegroundColor Green
} catch {
    Write-Host "  Ollama n'est pas lance. Demarrage..." -ForegroundColor Yellow

    # Lancer Ollama dans une nouvelle fenetre
    $ollamaScript = @"
`$host.UI.RawUI.WindowTitle = 'Ollama Server - NE PAS FERMER'
Write-Host 'Ollama Server - Ne fermez pas cette fenetre' -ForegroundColor Cyan
Write-Host '===========================================' -ForegroundColor Cyan
Write-Host ''
ollama serve
"@
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $ollamaScript

    Write-Host "  Attente du demarrage (10 secondes)..." -ForegroundColor White
    Start-Sleep -Seconds 10
}

# ============================================
# ETAPE 5: BACKEND
# ============================================
Write-Host ""
Write-Host "[5/6] Lancement du Backend..." -ForegroundColor Yellow

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
Start-Sleep -Seconds 5

# ============================================
# ETAPE 6: FRONTEND
# ============================================
Write-Host ""
Write-Host "[6/6] Lancement du Frontend..." -ForegroundColor Yellow

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

# Attendre 8 secondes puis ouvrir le navigateur
Write-Host "  Ouverture du navigateur dans 8 secondes..." -ForegroundColor White
Start-Sleep -Seconds 8
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "  Appuyez sur une touche pour fermer cette fenetre..." -ForegroundColor Gray
Read-Host
