# MIRAN V3.0 Launcher
Write-Host "`n╔════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     MIRAN V3.0 - PSRA         ║" -ForegroundColor Cyan
Write-Host "║  Phase-Symbolic Resonance     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n  [1] CLI - Terminal Interface" -ForegroundColor Green
Write-Host "  [2] Web - Browser (http://127.0.0.1:5000)" -ForegroundColor Green
Write-Host "  [3] Run Tests (pytest)" -ForegroundColor Green
Write-Host "  [4] Exit`n" -ForegroundColor Green

$choice = Read-Host "Select (1-4)"
$env:PYTHONPATH = "$PSScriptRoot"
$env:PYTHONIOENCODING = "utf-8"

switch ($choice) {
    "1" { python "$PSScriptRoot\demo_v3.py"; Read-Host "`nPress Enter to exit" }
    "2" { Write-Host "`nStarting web server at http://127.0.0.1:5000" -ForegroundColor Yellow; python "$PSScriptRoot\web_app.py"; Read-Host "`nPress Enter to exit" }
    "3" { pytest "$PSScriptRoot\tests" -v; Read-Host "`nPress Enter to exit" }
}
