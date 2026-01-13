# ============================================
# BiasDetector - REPARATION COMPLETE
# ============================================
# Ce script corrige TOUTES les erreurs et reinstalle tout

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "     BiasDetector - Reparation Complete" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "C:\Users\youss\ProjetAyoub\BiasDetector"
Set-Location $projectRoot

# ============================================
# ETAPE 1: ARRET DE TOUT
# ============================================
Write-Host "[1/8] Arret de tous les processus..." -ForegroundColor Yellow

# Arreter MongoDB
try {
    docker stop mongodb 2>&1 | Out-Null
    docker rm mongodb 2>&1 | Out-Null
    Write-Host "  MongoDB arrete" -ForegroundColor Green
} catch {}

# Tuer les processus sur les ports
try {
    $ports = @(3000, 3001, 8000)
    foreach ($port in $ports) {
        $proc = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
        if ($proc) {
            Stop-Process -Id $proc -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Host "  Ports liberes" -ForegroundColor Green
} catch {}

Start-Sleep -Seconds 2

# ============================================
# ETAPE 2: REINSTALLER LES DEPENDANCES BACKEND
# ============================================
Write-Host ""
Write-Host "[2/8] Reinstallation des dependances Backend..." -ForegroundColor Yellow
Set-Location "$projectRoot\backend"

# Activer le venv
& ".\venv\Scripts\Activate.ps1"

# Desinstaller pymongo problematique et reinstaller la bonne version
Write-Host "  Correction de pymongo/motor..." -ForegroundColor White
pip uninstall pymongo motor -y 2>&1 | Out-Null
pip install pymongo==4.6.0 motor==3.3.2 2>&1 | Out-Null

# Reinstaller toutes les dependances
Write-Host "  Installation des dependances..." -ForegroundColor White
pip install -r requirements.txt 2>&1 | Out-Null

Write-Host "  Backend dependances installees!" -ForegroundColor Green

# ============================================
# ETAPE 3: REINSTALLER LES DEPENDANCES FRONTEND
# ============================================
Write-Host ""
Write-Host "[3/8] Reinstallation des dependances Frontend..." -ForegroundColor Yellow
Set-Location "$projectRoot\frontend"

# Installer tailwindcss-animate
npm install tailwindcss-animate@^1.0.7 2>&1 | Out-Null
Write-Host "  Frontend dependances installees!" -ForegroundColor Green

# ============================================
# ETAPE 4: DOCKER
# ============================================
Write-Host ""
Write-Host "[4/8] Verification de Docker..." -ForegroundColor Yellow
Set-Location $projectRoot

$dockerReady = $false
$attempts = 0

while (-not $dockerReady -and $attempts -lt 30) {
    try {
        docker info 2>&1 | Out-Null
        $dockerReady = $true
    } catch {
        if ($attempts -eq 0) {
            Write-Host "  Lancement de Docker Desktop..." -ForegroundColor White
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
        Start-Sleep -Seconds 2
        $attempts++
    }
}

if ($dockerReady) {
    Write-Host "  Docker est pret!" -ForegroundColor Green
} else {
    Write-Host "  ERREUR: Lancez Docker Desktop manuellement!" -ForegroundColor Red
    Read-Host "  Appuyez sur Entree apres avoir lance Docker"
}

# ============================================
# ETAPE 5: MONGODB
# ============================================
Write-Host ""
Write-Host "[5/8] Demarrage de MongoDB..." -ForegroundColor Yellow

docker run -d -p 27017:27017 --name mongodb mongo:latest 2>&1 | Out-Null
Start-Sleep -Seconds 3
Write-Host "  MongoDB demarre!" -ForegroundColor Green

# ============================================
# ETAPE 6: OLLAMA
# ============================================
Write-Host ""
Write-Host "[6/8] Verification d'Ollama..." -ForegroundColor Yellow

$ollamaRunning = $false
try {
    Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue | Out-Null
    $ollamaRunning = $true
    Write-Host "  Ollama est deja en cours" -ForegroundColor Green
} catch {
    Write-Host "  Lancement d'Ollama..." -ForegroundColor White

    $ollamaScript = @"
`$host.UI.RawUI.WindowTitle = 'Ollama Server'
Write-Host 'Ollama Server - Ne fermez pas!' -ForegroundColor Cyan
ollama serve
"@
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $ollamaScript

    Write-Host "  Attente d'Ollama (15 secondes)..." -ForegroundColor White
    Start-Sleep -Seconds 15
    Write-Host "  Ollama lance!" -ForegroundColor Green
}

# ============================================
# ETAPE 7: BACKEND
# ============================================
Write-Host ""
Write-Host "[7/8] Lancement du Backend..." -ForegroundColor Yellow

$backendScript = @"
Set-Location '$projectRoot\backend'
`$host.UI.RawUI.WindowTitle = 'BiasDetector Backend'
Write-Host ''
Write-Host 'BiasDetector Backend - Port 8000' -ForegroundColor Cyan
Write-Host ''

# Activer venv
& '.\venv\Scripts\Activate.ps1'

# Lancer
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript
Write-Host "  Backend lance!" -ForegroundColor Green
Start-Sleep -Seconds 8

# ============================================
# ETAPE 8: FRONTEND
# ============================================
Write-Host ""
Write-Host "[8/8] Lancement du Frontend..." -ForegroundColor Yellow

$frontendScript = @"
Set-Location '$projectRoot\frontend'
`$host.UI.RawUI.WindowTitle = 'BiasDetector Frontend'
Write-Host ''
Write-Host 'BiasDetector Frontend - Port 3000' -ForegroundColor Cyan
Write-Host ''

npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript
Write-Host "  Frontend lance!" -ForegroundColor Green

# ============================================
# TERMINE
# ============================================
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "     Reparation terminee!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Application: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend:     http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Ouverture du navigateur dans 10 secondes..." -ForegroundColor White

Start-Sleep -Seconds 10
Start-Process "http://localhost:3000"

Write-Host ""
Read-Host "  Appuyez sur Entree pour fermer"
