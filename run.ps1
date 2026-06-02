# MIRAN V8 Launcher
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  mirnan V8 - Partonic Resonance" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
Write-Host "  [1] CLI - Interactive Terminal" -ForegroundColor Green
Write-Host "  [2] Web UI - http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  [3] Physics Demo" -ForegroundColor Green
Write-Host "  [4] Physics Trace" -ForegroundColor Green
Write-Host "  [5] Physics Validation" -ForegroundColor Green
Write-Host "  [6] Run Tests" -ForegroundColor Green
Write-Host "  [7] Exit`n" -ForegroundColor Green

$choice = Read-Host "Select (1-7)"
$env:PYTHONPATH = $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"

if ($choice -eq "1") {
    python "$PSScriptRoot\cli.py" -i
    Read-Host "Press Enter to exit"
}
elseif ($choice -eq "2") {
    Write-Host "Starting server at http://127.0.0.1:8000" -ForegroundColor Yellow
    python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
}
elseif ($choice -eq "3") {
    python "$PSScriptRoot\physics_demo.py" --full --prompt "العلم نور" --max-words 8
    Read-Host "Press Enter to exit"
}
elseif ($choice -eq "4") {
    $p = Read-Host "Enter prompt"
    python "$PSScriptRoot\physics_demo.py" --prompt $p --json
    Read-Host "Press Enter to exit"
}
elseif ($choice -eq "5") {
    python "$PSScriptRoot\physics_demo.py" --validate --compare
    Read-Host "Press Enter to exit"
}
elseif ($choice -eq "6") {
    python -m pytest tests/ -v
    Read-Host "Press Enter to exit"
}
