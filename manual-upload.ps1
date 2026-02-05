# Manual GitHub Upload Instructions
# ===================================

Write-Host "========================================" -ForegroundColor Green
Write-Host "  GitHub Web Upload Instructions" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Open GitHub in browser
$repoUrl = "https://github.com/badboyoffical120-wq/chatbot_honeypot"

Write-Host "1. Opening your GitHub repository..." -ForegroundColor Yellow
Start-Process $repoUrl

Write-Host ""
Write-Host "2. In your browser:" -ForegroundColor Yellow
Write-Host "   - Click 'Add file' button" -ForegroundColor White
Write-Host "   - Select 'Upload files'" -ForegroundColor White
Write-Host ""

Write-Host "3. Drag and drop these files:" -ForegroundColor Yellow
$files = @(
    "app.py",
    "requirements.txt", 
    "Procfile",
    "render.yaml",
    "DEPLOYMENT.md",
    ".gitignore"
)

foreach ($file in $files) {
    Write-Host "   ✓ $file" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "4. Also upload folders:" -ForegroundColor Yellow
Write-Host "   ✓ static/style.css" -ForegroundColor Cyan
Write-Host "   ✓ templates/index.html" -ForegroundColor Cyan

Write-Host ""
Write-Host "5. Click 'Commit changes'" -ForegroundColor Yellow
Write-Host ""
Write-Host "✓ Upload complete! Render will auto-deploy your app." -ForegroundColor Green
Write-Host ""

# List all files to upload
Write-Host "File list for reference:" -ForegroundColor Yellow
Write-Host ""
Get-ChildItem -Path "c:\Users\rahul\Desktop\j" -Recurse -File | 
    Where-Object { $_.FullName -notmatch '\.git' -and $_.FullName -notmatch '\.env' } |
    Select-Object FullName | 
    ForEach-Object { 
        $relativePath = $_.FullName -replace 'c:\\Users\\rahul\\Desktop\\j\\', ''
        Write-Host "   $relativePath" -ForegroundColor White
    }

Write-Host ""
Read-Host "Press Enter when done"
