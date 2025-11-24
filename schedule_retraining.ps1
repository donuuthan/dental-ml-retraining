# Automated Weekly Model Retraining Script for Windows
# This script can be scheduled using Task Scheduler

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = "python"  # Or full path: "C:\Python39\python.exe"
$LogFile = Join-Path $ScriptDir "retraining.log"
$Date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Log start
Add-Content -Path $LogFile -Value "[$Date] Starting automated model retraining..."

# Change to script directory
Set-Location $ScriptDir

# Run retraining script
try {
    & $PythonExe auto_retrain_model.py 2>&1 | Tee-Object -FilePath $LogFile -Append
    
    if ($LASTEXITCODE -eq 0) {
        Add-Content -Path $LogFile -Value "[$Date] Retraining completed successfully"
        
        # Optional: Restart ML service
        # Restart-Service -Name "MLPredictionService"
        
        # Optional: Send notification
        # Invoke-WebRequest -Uri "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" `
        #   -Method POST -Body '{"text":"Model retraining completed successfully"}'
        
        exit 0
    } else {
        Add-Content -Path $LogFile -Value "[$Date] Retraining failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }
} catch {
    Add-Content -Path $LogFile -Value "[$Date] Error: $_"
    exit 1
}

