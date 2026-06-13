$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
& node (Join-Path $PSScriptRoot "sync_from_github.mjs")
exit $LASTEXITCODE
