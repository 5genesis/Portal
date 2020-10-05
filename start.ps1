$port = if ($null -eq $args[0]) { "5000" } else { $args[0] }

Write-Host Starting Portal on port $port

& ./venv/Scripts/activate.ps1
& waitress-serve --listen=*:$port portal:app
& deactivate