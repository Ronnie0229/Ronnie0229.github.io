$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$git = "C:\Program Files\Git\cmd\git.exe"

if (-not (Test-Path -LiteralPath $git)) {
  throw "Git was not found: $git"
}

$changes = & $git -C $projectRoot status --porcelain
if ($LASTEXITCODE -ne 0) {
  throw "Unable to read the Git status."
}

if ($changes) {
  Write-Host "Local changes were found. Sync stopped to avoid overwriting them." -ForegroundColor Yellow
  Write-Host "Commit, push, or resolve these changes first:" -ForegroundColor Yellow
  $changes | ForEach-Object { Write-Host $_ }
  exit 2
}

Write-Host "Pulling the latest website changes from GitHub..."
& $git -C $projectRoot pull --ff-only origin main
if ($LASTEXITCODE -ne 0) {
  throw "Sync failed. Check the network and GitHub credentials."
}

Write-Host "Sync complete. The local project is up to date." -ForegroundColor Green
