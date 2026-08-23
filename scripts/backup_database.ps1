# ================================================================================
# Database Backup Script for Medical Device Management System
# PowerShell script to create timestamped SQLite backups
# ================================================================================

param(
    [string]$DatabasePath = ".\database\devices.db",
    [string]$BackupDir = ".\database\backups",
    [int]$KeepDays = 7
)

# Ensure backup directory exists
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

# Generate timestamp
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = Join-Path $BackupDir "devices_backup_$Timestamp.db"

# Check database exists
if (!(Test-Path $DatabasePath)) {
    Write-Error "Database file not found: $DatabasePath"
    exit 1
}

# Stop any running processes using the database (SQLite lock files)
$LockFile = "$DatabasePath-wal"
if (Test-Path $LockFile) {
    Write-Host "Note: Database in WAL mode, backup may be consistent"
}

try {
    # Copy database file
    Copy-Item -Path $DatabasePath -Destination $BackupFile -Force
    Write-Host "✅ Backup created: $BackupFile"
    
    # Get backup size
    $Size = (Get-Item $BackupFile).Length / 1MB
    Write-Host "📊 Backup size: $([math]::Round($Size, 2)) MB"
    
    # Clean old backups (older than KeepDays)
    $Cutoff = (Get-Date).AddDays(-$KeepDays)
    $OldBackups = Get-ChildItem $BackupDir -Filter "devices_backup_*.db" | Where-Object {$_.LastWriteTime -lt $Cutoff}
    
    foreach ($Old in $OldBackups) {
        Remove-Item $Old.FullName -Force
        Write-Host "🗑️  Removed old backup: $($Old.Name)"
    }
    
    Write-Host "✅ Backup completed successfully"
    exit 0
}
catch {
    Write-Error "Backup failed: $_"
    exit 1
}