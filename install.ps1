$python=$args[0]

try {
    Write-Host Using (& $python --version)
} catch {
    Write-Host $_
    Write-Host Could not obtain Python version, please check script parameter. Aborting.
    exit
}

Write-Host Creating Virtualenv...
& $python -m venv ./venv
& ./venv/Scripts/activate.ps1

Write-Host Installing requirements...
& pip install -r ./requirements.txt
& pip install waitress

Write-Host Initializing database...
& flask db upgrade

& deactivate