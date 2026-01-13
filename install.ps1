# ============================================
# BiasDetector - Script d'installation
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   BiasDetector - Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot

# Installation Backend
Write-Host "[1/4] Installation du Backend..." -ForegroundColor Yellow
$backendPath = Join-Path $projectRoot "backend"
Set-Location $backendPath

# Creer venv si necessaire
$venvPath = Join-Path $backendPath "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "  Creation de l'environnement virtuel..." -ForegroundColor White
    python -m venv venv
}

# Activer venv et installer les dependances
Write-Host "  Installation des dependances Python..." -ForegroundColor White
& "$venvPath\Scripts\pip.exe" install -r requirements.txt

# Copier .env
$envPath = Join-Path $backendPath ".env"
$envExamplePath = Join-Path $backendPath ".env.example"
if (-not (Test-Path $envPath)) {
    Copy-Item $envExamplePath $envPath
    Write-Host "  Fichier .env cree" -ForegroundColor Green
}

Write-Host "  Backend installe!" -ForegroundColor Green

# Installation Frontend
Write-Host ""
Write-Host "[2/4] Installation du Frontend..." -ForegroundColor Yellow
$frontendPath = Join-Path $projectRoot "frontend"
Set-Location $frontendPath

Write-Host "  Installation des dependances npm..." -ForegroundColor White
npm install

# Copier .env.local
$envLocalPath = Join-Path $frontendPath ".env.local"
$envExampleFrontPath = Join-Path $frontendPath ".env.example"
if (-not (Test-Path $envLocalPath)) {
    Copy-Item $envExampleFrontPath $envLocalPath
    Write-Host "  Fichier .env.local cree" -ForegroundColor Green
}

Write-Host "  Frontend installe!" -ForegroundColor Green

# Verification Ollama
Write-Host ""
Write-Host "[3/4] Verification d'Ollama..." -ForegroundColor Yellow
$ollamaInstalled = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollamaInstalled) {
    Write-Host "  Ollama est installe" -ForegroundColor Green
    Write-Host "  Telechargement des modeles..." -ForegroundColor White

    # Telecharger les modeles
    Write-Host "  Telechargement de llama3.2 (peut prendre quelques minutes)..." -ForegroundColor White
    ollama pull llama3.2

    Write-Host "  Telechargement de nomic-embed-text..." -ForegroundColor White
    ollama pull nomic-embed-text

    Write-Host "  Modeles telecharges!" -ForegroundColor Green
} else {
    Write-Host "  Ollama n'est pas installe!" -ForegroundColor Red
    Write-Host "  Telechargez-le depuis: https://ollama.ai" -ForegroundColor Yellow
}

# Verification Docker
Write-Host ""
Write-Host "[4/4] Verification de Docker..." -ForegroundColor Yellow
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerInstalled) {
    Write-Host "  Docker est installe" -ForegroundColor Green
} else {
    Write-Host "  Docker n'est pas installe!" -ForegroundColor Red
    Write-Host "  Telechargez-le depuis: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
}

# Retour au dossier racine
Set-Location $projectRoot

# Resume
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Installation terminee!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Pour lancer l'application:" -ForegroundColor White
Write-Host "    .\start.ps1" -ForegroundColor Yellow
Write-Host ""

if (-not $ollamaInstalled) {
    Write-Host "  N'oubliez pas d'installer Ollama!" -ForegroundColor Red
}
if (-not $dockerInstalled) {
    Write-Host "  N'oubliez pas d'installer Docker!" -ForegroundColor Red
}
