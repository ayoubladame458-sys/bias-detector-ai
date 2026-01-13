# ============================================
# BiasDetector - LANCEMENT FINAL CORRIGE
# ============================================
# Ce script corrige TOUTES les erreurs et lance l'application

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "     BiasDetector - Lancement Final" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "C:\Users\youss\ProjetAyoub\BiasDetector"
Set-Location $projectRoot

# ============================================
# ETAPE 1: NETTOYAGE
# ============================================
Write-Host "[1/7] Nettoyage des processus existants..." -ForegroundColor Yellow

# Arreter les ports occupes
try {
    $processes = Get-NetTCPConnection -LocalPort 3000,3001,8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($proc in $processes) {
        Stop-Process -Id $proc -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  Ports liberes" -ForegroundColor Green
} catch {
    Write-Host "  Ports deja libres" -ForegroundColor Gray
}

# Arreter MongoDB
try {
    docker stop mongodb 2>&1 | Out-Null
    docker rm mongodb 2>&1 | Out-Null
    Write-Host "  MongoDB nettoye" -ForegroundColor Green
} catch {
    Write-Host "  MongoDB deja nettoye" -ForegroundColor Gray
}

Start-Sleep -Seconds 2

# ============================================
# ETAPE 2: VERIFICATION DOCKER
# ============================================
Write-Host ""
Write-Host "[2/7] Verification de Docker..." -ForegroundColor Yellow

$dockerReady = $false
$attempts = 0
$maxAttempts = 30

while (-not $dockerReady -and $attempts -lt $maxAttempts) {
    try {
        docker info 2>&1 | Out-Null
        $dockerReady = $true
        Write-Host "  Docker est pret!" -ForegroundColor Green
    } catch {
        if ($attempts -eq 0) {
            Write-Host "  Docker n'est pas lance. Tentative de lancement..." -ForegroundColor Yellow

            # Chercher et lancer Docker Desktop
            $dockerPaths = @(
                "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe",
                "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe"
            )

            foreach ($path in $dockerPaths) {
                if (Test-Path $path) {
                    Start-Process $path -ErrorAction SilentlyContinue
                    break
                }
            }
        }

        Write-Host "  Attente de Docker... ($attempts/$maxAttempts)" -ForegroundColor Gray
        Start-Sleep -Seconds 2
        $attempts++
    }
}

if (-not $dockerReady) {
    Write-Host "  ERREUR: Docker ne demarre pas!" -ForegroundColor Red
    Write-Host "  Lancez Docker Desktop manuellement puis relancez ce script." -ForegroundColor Yellow
    Read-Host "  Appuyez sur Entree pour quitter"
    exit
}

# ============================================
# ETAPE 3: MONGODB
# ============================================
Write-Host ""
Write-Host "[3/7] Demarrage de MongoDB..." -ForegroundColor Yellow

try {
    docker run -d -p 27017:27017 --name mongodb mongo:latest 2>&1 | Out-Null
    Write-Host "  MongoDB demarre sur le port 27017" -ForegroundColor Green
    Start-Sleep -Seconds 3
} catch {
    Write-Host "  Erreur MongoDB (peut continuer)" -ForegroundColor Yellow
}

# ============================================
# ETAPE 4: OLLAMA
# ============================================
Write-Host ""
Write-Host "[4/7] Verification d'Ollama..." -ForegroundColor Yellow

$ollamaReady = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue 2>&1
    $ollamaReady = $true
    Write-Host "  Ollama est deja en cours" -ForegroundColor Green
} catch {
    Write-Host "  Lancement d'Ollama..." -ForegroundColor Yellow

    $ollamaScript = @"
`$host.UI.RawUI.WindowTitle = 'Ollama Server - NE PAS FERMER'
Write-Host ''
Write-Host '================================================' -ForegroundColor Cyan
Write-Host '    Ollama Server - Ne fermez pas!' -ForegroundColor Cyan
Write-Host '================================================' -ForegroundColor Cyan
Write-Host ''
ollama serve
"@
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $ollamaScript

    Write-Host "  Attente d'Ollama (15 secondes)..." -ForegroundColor White
    Start-Sleep -Seconds 15

    # Verifier que ca a marche
    try {
        Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue 2>&1 | Out-Null
        Write-Host "  Ollama est pret!" -ForegroundColor Green
    } catch {
        Write-Host "  ATTENTION: Ollama ne repond pas (peut causer des erreurs)" -ForegroundColor Yellow
    }
}

# ============================================
# ETAPE 5: INSTALLATION FRONTEND
# ============================================
Write-Host ""
Write-Host "[5/7] Installation des dependances frontend..." -ForegroundColor Yellow
Set-Location "$projectRoot\frontend"

# Verifier si tailwindcss-animate est installe
$needInstall = $true
if (Test-Path "package-lock.json") {
    $packageLock = Get-Content "package-lock.json" -Raw | ConvertFrom-Json
    if ($packageLock.packages.'node_modules/tailwindcss-animate') {
        $needInstall = $false
        Write-Host "  tailwindcss-animate deja installe" -ForegroundColor Green
    }
}

if ($needInstall) {
    Write-Host "  Installation de tailwindcss-animate..." -ForegroundColor White
    npm install tailwindcss-animate@^1.0.7 2>&1 | Out-Null
    Write-Host "  tailwindcss-animate installe!" -ForegroundColor Green
}

# ============================================
# ETAPE 6: BACKEND
# ============================================
Write-Host ""
Write-Host "[6/7] Lancement du Backend..." -ForegroundColor Yellow
Set-Location $projectRoot

$backendScript = @"
Set-Location '$projectRoot\backend'
`$host.UI.RawUI.WindowTitle = 'BiasDetector Backend - Port 8000'
Write-Host ''
Write-Host '================================================' -ForegroundColor Cyan
Write-Host '    BiasDetector Backend' -ForegroundColor Cyan
Write-Host '================================================' -ForegroundColor Cyan
Write-Host ''
Write-Host '  Backend API: http://localhost:8000' -ForegroundColor White
Write-Host '  API Docs:    http://localhost:8000/docs' -ForegroundColor White
Write-Host ''
Write-Host '  Ne fermez pas cette fenetre!' -ForegroundColor Yellow
Write-Host ''

# Activer venv
& '.\venv\Scripts\Activate.ps1'

# Lancer uvicorn
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript
Write-Host "  Backend en cours de demarrage..." -ForegroundColor White

# Attendre que le backend soit pret
Write-Host "  Attente du backend (10 secondes)..." -ForegroundColor White
Start-Sleep -Seconds 10

# Verifier si le backend repond
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -TimeoutSec 3 -ErrorAction SilentlyContinue 2>&1
    Write-Host "  Backend est pret!" -ForegroundColor Green
} catch {
    Write-Host "  Backend demarre (peut prendre quelques secondes de plus)" -ForegroundColor Yellow
}

# ============================================
# ETAPE 7: FRONTEND
# ============================================
Write-Host ""
Write-Host "[7/7] Lancement du Frontend..." -ForegroundColor Yellow

$frontendScript = @"
Set-Location '$projectRoot\frontend'
`$host.UI.RawUI.WindowTitle = 'BiasDetector Frontend - Port 3000'
Write-Host ''
Write-Host '================================================' -ForegroundColor Cyan
Write-Host '    BiasDetector Frontend' -ForegroundColor Cyan
Write-Host '================================================' -ForegroundColor Cyan
Write-Host ''
Write-Host '  Application: http://localhost:3000' -ForegroundColor White
Write-Host ''
Write-Host '  Ne fermez pas cette fenetre!' -ForegroundColor Yellow
Write-Host ''

npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript
Write-Host "  Frontend en cours de demarrage..." -ForegroundColor White

# ============================================
# RESUME FINAL
# ============================================
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "     BiasDetector est pret!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Application:" -ForegroundColor White
Write-Host "    http://localhost:3000" -ForegroundColor Cyan
Write-Host "    (ou http://localhost:3001 si 3000 est occupe)" -ForegroundColor Gray
Write-Host ""
Write-Host "  Backend API:" -ForegroundColor White
Write-Host "    http://localhost:8000" -ForegroundColor Cyan
Write-Host "    http://localhost:8000/docs (documentation)" -ForegroundColor Gray
Write-Host ""
Write-Host "  Services actifs:" -ForegroundColor White
Write-Host "    - MongoDB (Port 27017)" -ForegroundColor Gray
Write-Host "    - Ollama (Port 11434)" -ForegroundColor Gray
Write-Host "    - Backend (Port 8000)" -ForegroundColor Gray
Write-Host "    - Frontend (Port 3000)" -ForegroundColor Gray
Write-Host ""
Write-Host "  Pour arreter:" -ForegroundColor Yellow
Write-Host "    Fermez toutes les fenetres PowerShell" -ForegroundColor White
Write-Host ""

# Attendre puis ouvrir le navigateur
Write-Host "  Ouverture du navigateur dans 10 secondes..." -ForegroundColor White
Start-Sleep -Seconds 10

# Essayer les deux ports
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -ErrorAction SilentlyContinue 2>&1
    Start-Process "http://localhost:3000"
} catch {
    Start-Process "http://localhost:3001"
}

Write-Host ""
Write-Host "  Appuyez sur une touche pour fermer cette fenetre..." -ForegroundColor Gray
Read-Host
