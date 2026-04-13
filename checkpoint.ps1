param(
    [Parameter(Mandatory = $false)]
    [string]$Mensagem = "checkpoint local"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host ""
Write-Host "== STATUS ATUAL ==" -ForegroundColor Cyan
git status --short

$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupDir = Join-Path $root "Backups"
$backupFile = Join-Path $backupDir "projeto-retorica_$timestamp.zip"

if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

Write-Host ""
Write-Host "== GERANDO BACKUP ==" -ForegroundColor Cyan
Compress-Archive -Path ".\site-retorica-main", ".\functions", ".\.firebaserc", ".\firebase.json" -DestinationPath $backupFile -Force
Write-Host "Backup criado em: $backupFile" -ForegroundColor Green

Write-Host ""
Write-Host "== ADICIONANDO ALTERACOES ==" -ForegroundColor Cyan
git add .

$temMudancas = git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "Nenhuma alteracao nova para commit." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "== CRIANDO COMMIT ==" -ForegroundColor Cyan
git commit -m $Mensagem

Write-Host ""
Write-Host "== RESUMO FINAL ==" -ForegroundColor Cyan
git log --oneline -1
Write-Host "Backup: $backupFile" -ForegroundColor Green
