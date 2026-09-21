# Valida a integridade da memória do projeto (equivalente Windows de check-memoria.sh).
# Regras (AGENT.md):
#  - MEMORIA/INDEX.md existe;
#  - cada ficheiro .md referenciado no INDEX existe;
#  - nenhum ficheiro .md sob MEMORIA/ ultrapassa 600 linhas;
#  - ficheiros presentes mas não referenciados geram apenas aviso.

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$mem = Join-Path $root 'MEMORIA'
$index = Join-Path $mem 'INDEX.md'
$maxLines = 600
$fail = $false

if (-not (Test-Path -LiteralPath $index)) {
    Write-Host "ERRO: $index não existe."
    exit 1
}

$indexed = Get-Content -LiteralPath $index |
    ForEach-Object { [regex]::Matches($_, 'MEMORIA/[A-Za-z0-9_./-]+\.md').Value } |
    Sort-Object -Unique

foreach ($f in $indexed) {
    if (-not (Test-Path -LiteralPath (Join-Path $root ($f.Replace('/', '\'))))) {
        Write-Host "ERRO: '$f' está referenciado no INDEX mas não existe."
        $fail = $true
    }
}

$files = Get-ChildItem -LiteralPath $mem -Recurse -Filter '*.md' -File |
    Sort-Object FullName

foreach ($f in $files) {
    $rel = $f.FullName.Substring($root.Length + 1).Replace('\', '/')
    $lines = (Get-Content -LiteralPath $f.FullName).Count
    if ($lines -gt $maxLines) {
        Write-Host "ERRO: '$rel' tem $lines linhas (máximo $maxLines)."
        $fail = $true
    }
    if ($rel -ne 'MEMORIA/INDEX.md' -and $indexed -notcontains $rel) {
        Write-Host "AVISO: '$rel' não está referenciado no INDEX."
    }
}

if ($fail) {
    Write-Host 'Memória com problemas.'
    exit 1
}

Write-Host "Memória OK (INDEX válido e máximo de $maxLines linhas respeitado)."