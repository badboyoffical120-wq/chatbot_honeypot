# Deployment Script for GitHub & Render

Write-Host "=== Chatbot Honeypot Deployment ==="
Write-Host ""

# Check if git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Git is not installed!" -ForegroundColor Red
    Write-Host "Please download and install Git from https://git-scm.com/download/win"
    exit 1
}

$gitRepo = "https://github.com/badboyoffical120-wq/chatbot_honeypot.git"
$branch = "main"

Write-Host "Repository: $gitRepo" -ForegroundColor Green
Write-Host ""

# Initialize git if not already done
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init
    git config user.email "you@example.com"
    git config user.name "Your Name"
}

# Check current status
Write-Host "Checking git status..." -ForegroundColor Yellow
git status
Write-Host ""

# Add all files
Write-Host "Adding files..." -ForegroundColor Yellow
git add .

# Commit
$commitMsg = "Update: API key management and Render deployment setup"
Write-Host "Committing with message: $commitMsg" -ForegroundColor Yellow
git commit -m $commitMsg

# Add remote if not exists
$remoteExists = git config --get remote.origin.url
if (-not $remoteExists) {
    Write-Host "Adding remote origin..." -ForegroundColor Yellow
    git remote add origin $gitRepo
}

# Set branch to main
Write-Host "Setting branch to main..." -ForegroundColor Yellow
git branch -M main

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "You will be prompted to authenticate with GitHub" -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== SUCCESS ===" -ForegroundColor Green
    Write-Host "Your code has been pushed to GitHub!"
    Write-Host "Render will auto-deploy your application."
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Go to https://render.com/dashboard"
    Write-Host "2. Connect your GitHub repository"
    Write-Host "3. Deploy will start automatically"
} else {
    Write-Host ""
    Write-Host "ERROR: Git push failed!" -ForegroundColor Red
    Write-Host "Make sure you have GitHub credentials set up."
}

Pause
