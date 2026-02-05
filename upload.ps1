# GitHub Upload Script (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GitHub Upload - Chatbot Honeypot" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check/Install Git
Write-Host "[1/5] Checking Git installation..." -ForegroundColor Yellow

$gitPath = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitPath) {
    Write-Host "Installing Git..." -ForegroundColor Yellow
    
    # Download Git
    $gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"
    $gitInstaller = "$env:TEMP\GitInstaller.exe"
    
    Write-Host "Downloading Git installer..." -ForegroundColor Cyan
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $gitUrl -OutFile $gitInstaller -ErrorAction Stop
    
    Write-Host "Running Git installer (silent mode)..." -ForegroundColor Cyan
    Start-Process -FilePath $gitInstaller -ArgumentList @("/SILENT", "/NORESTART") -Wait
    
    Write-Host "Git installed successfully!" -ForegroundColor Green
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

Write-Host "Git version: $(git --version)" -ForegroundColor Green
Write-Host ""

# Step 2: Configure git
Write-Host "[2/5] Configuring Git..." -ForegroundColor Yellow
git config user.email "badboyofficial@github.com"
git config user.name "Rahul"
Write-Host "Git configured!" -ForegroundColor Green
Write-Host ""

# Step 3: Initialize repo
Write-Host "[3/5] Initializing repository..." -ForegroundColor Yellow
git init
Write-Host "Repository initialized!" -ForegroundColor Green
Write-Host ""

# Step 4: Add and commit files
Write-Host "[4/5] Adding and committing files..." -ForegroundColor Yellow
git add .
git commit -m "Initial commit: Scam detector chatbot with API management and Render deployment"
Write-Host "Files committed!" -ForegroundColor Green
Write-Host ""

# Step 5: Push to GitHub
Write-Host "[5/5] Adding remote and pushing to GitHub..." -ForegroundColor Yellow

$remote = git config --get remote.origin.url
if (-not $remote) {
    git remote add origin "https://github.com/badboyoffical120-wq/chatbot_honeypot.git"
    Write-Host "Remote added!" -ForegroundColor Green
}

git branch -M main

Write-Host ""
Write-Host "Pushing to GitHub (you may need to authenticate)..." -ForegroundColor Cyan
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  SUCCESS! Files uploaded to GitHub" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository URL:" -ForegroundColor Cyan
    Write-Host "https://github.com/badboyoffical120-wq/chatbot_honeypot" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Go to https://render.com/dashboard" -ForegroundColor White
    Write-Host "2. Click 'New +' > 'Web Service'" -ForegroundColor White
    Write-Host "3. Select your GitHub repository" -ForegroundColor White
    Write-Host "4. Render will auto-detect settings and deploy!" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR: Push failed!" -ForegroundColor Red
    Write-Host "Check your GitHub credentials and try again." -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to close"
