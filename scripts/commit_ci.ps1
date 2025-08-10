# Коммит и пуш файла .github/workflows/ci.yml в текущую ветку репозитория
# Запуск из PowerShell:  powershell -ExecutionPolicy Bypass -File .\scripts\commit_ci.ps1

$ErrorActionPreference = 'Stop'
$repo = 'C:\Projects\poisk-more-qgis'
$ciPath = Join-Path $repo '.github\workflows\ci.yml'

if (-not (Test-Path (Split-Path $ciPath))) {
    New-Item -Type Directory -Force (Split-Path $ciPath) | Out-Null
}

# Проверка наличия файла
if (-not (Test-Path $ciPath)) {
    Write-Error "Файл не найден: $ciPath. Сначала сохраните его по этому пути."
}

Push-Location $repo
try {
    # Определяем ветку
    $branch = (git rev-parse --abbrev-ref HEAD).Trim()
    if ([string]::IsNullOrWhiteSpace($branch)) {
        throw "Не удалось определить ветку. Убедитесь, что это git-репозиторий и есть хотя бы один коммит."
    }

    # Минимальная конфигурация git, если не задана
    if (-not (git config user.name))  { git config user.name  "PoiskMore-CI"   | Out-Null }
    if (-not (git config user.email)) { git config user.email "ci@poisk-more" | Out-Null }

    git add .github\workflows\ci.yml
    $hasChanges = git status --porcelain
    if (-not [string]::IsNullOrWhiteSpace($hasChanges)) {
        git commit -m "CI: add/update .github/workflows/ci.yml"
    } else {
        Write-Host "Нет изменений для коммита — файл уже в актуальном состоянии."
    }

    # Пуш в текущую ветку
    git push -u origin $branch
    Write-Host "Готово: файл закоммичен и запушен в $branch."
}
finally {
    Pop-Location
}
