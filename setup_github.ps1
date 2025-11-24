# Automated GitHub Setup Script for ML Retraining
# This script prepares everything and guides you through GitHub setup

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub ML Retraining Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "✓ Git is installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git is not installed. Please install Git first." -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Get current directory
$scriptDir = $PSScriptRoot
if (-not $scriptDir) {
    $scriptDir = Get-Location
}

Write-Host "Working directory: $scriptDir" -ForegroundColor Gray
Write-Host ""

# Check if already a git repository
if (Test-Path "$scriptDir\.git") {
    Write-Host "⚠ Git repository already initialized" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 0
    }
} else {
    Write-Host "Initializing git repository..." -ForegroundColor Cyan
    Set-Location $scriptDir
    git init
    Write-Host "✓ Git repository initialized" -ForegroundColor Green
}

# Check if .gitignore exists
if (-not (Test-Path "$scriptDir\.gitignore")) {
    Write-Host "Creating .gitignore..." -ForegroundColor Cyan
    # .gitignore should already exist, but just in case
}

# Add all files
Write-Host ""
Write-Host "Adding files to git..." -ForegroundColor Cyan
git add .
Write-Host "✓ Files added" -ForegroundColor Green

# Check if there are changes to commit
$status = git status --porcelain
if ($status) {
    Write-Host ""
    Write-Host "Creating initial commit..." -ForegroundColor Cyan
    git commit -m "Initial commit: ML retraining system"
    Write-Host "✓ Initial commit created" -ForegroundColor Green
} else {
    Write-Host "⚠ No changes to commit" -ForegroundColor Yellow
}

# Set branch to main
Write-Host ""
Write-Host "Setting branch to main..." -ForegroundColor Cyan
git branch -M main
Write-Host "✓ Branch set to main" -ForegroundColor Green

# Check if remote already exists
$remote = git remote get-url origin 2>$null
if ($remote) {
    Write-Host ""
    Write-Host "⚠ Remote 'origin' already exists: $remote" -ForegroundColor Yellow
    $update = Read-Host "Update remote URL? (y/n)"
    if ($update -eq "y") {
        $repoUrl = Read-Host "Enter your GitHub repository URL (e.g., https://github.com/username/dental-ml-retraining.git)"
        git remote set-url origin $repoUrl
        Write-Host "✓ Remote URL updated" -ForegroundColor Green
    }
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "STEP 1: Create GitHub Repository" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Go to: https://github.com/new" -ForegroundColor White
    Write-Host "2. Repository name: dental-ml-retraining" -ForegroundColor White
    Write-Host "3. Description: Automated ML retraining for dental appointments" -ForegroundColor White
    Write-Host "4. Make it PUBLIC (for free Actions)" -ForegroundColor White
    Write-Host "5. DON'T check any boxes (no README, no .gitignore)" -ForegroundColor White
    Write-Host "6. Click 'Create repository'" -ForegroundColor White
    Write-Host ""
    
    $continue = Read-Host "Have you created the repository? (y/n)"
    if ($continue -ne "y") {
        Write-Host "Please create the repository first, then run this script again." -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host ""
    $repoUrl = Read-Host "Enter your GitHub repository URL (e.g., https://github.com/username/dental-ml-retraining.git)"
    
    Write-Host ""
    Write-Host "Adding remote repository..." -ForegroundColor Cyan
    git remote add origin $repoUrl
    Write-Host "✓ Remote added" -ForegroundColor Green
}

# Push to GitHub
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You may be prompted for GitHub credentials." -ForegroundColor Yellow
Write-Host "If you use 2FA, you'll need a Personal Access Token instead of password." -ForegroundColor Yellow
Write-Host "Get token from: https://github.com/settings/tokens" -ForegroundColor Yellow
Write-Host ""

$push = Read-Host "Push to GitHub now? (y/n)"
if ($push -eq "y") {
    try {
        git push -u origin main
        Write-Host ""
        Write-Host "✓ Successfully pushed to GitHub!" -ForegroundColor Green
    } catch {
        Write-Host ""
        Write-Host "✗ Push failed. You may need to:" -ForegroundColor Red
        Write-Host "  1. Set up GitHub authentication" -ForegroundColor Yellow
        Write-Host "  2. Use GitHub Desktop app" -ForegroundColor Yellow
        Write-Host "  3. Or push manually later" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To push manually, run:" -ForegroundColor Cyan
        Write-Host "  git push -u origin main" -ForegroundColor White
    }
} else {
    Write-Host ""
    Write-Host "You can push later by running:" -ForegroundColor Cyan
    Write-Host "  git push -u origin main" -ForegroundColor White
}

# Next steps
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. ✓ Repository created (or already exists)" -ForegroundColor Green
Write-Host "2. ✓ Code pushed (or ready to push)" -ForegroundColor Green
Write-Host ""
Write-Host "3. ⚠ ADD FIREBASE SECRET:" -ForegroundColor Yellow
Write-Host "   a. Go to your repository on GitHub" -ForegroundColor White
Write-Host "   b. Click 'Settings' → 'Secrets and variables' → 'Actions'" -ForegroundColor White
Write-Host "   c. Click 'New repository secret'" -ForegroundColor White
Write-Host "   d. Name: FIREBASE_SERVICE_ACCOUNT_KEY" -ForegroundColor White
Write-Host "   e. Value: Paste your Firebase service account JSON content" -ForegroundColor White
Write-Host "   f. Click 'Add secret'" -ForegroundColor White
Write-Host ""
Write-Host "4. ⚠ TEST THE WORKFLOW:" -ForegroundColor Yellow
Write-Host "   a. Go to 'Actions' tab in your repository" -ForegroundColor White
Write-Host "   b. Click 'Auto-Retrain ML Model'" -ForegroundColor White
Write-Host "   c. Click 'Run workflow' button" -ForegroundColor White
Write-Host "   d. Select branch: main" -ForegroundColor White
Write-Host "   e. Click 'Run workflow'" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

