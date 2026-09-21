#!/usr/bin/env bash
# Valida a integridade da memória do projeto (regras do AGENT.md).
#  - MEMORIA/INDEX.md existe;
#  - cada ficheiro .md referenciado no INDEX existe;
#  - nenhum ficheiro .md sob MEMORIA/ ultrapassa 600 linhas;
#  - ficheiros presentes mas não referenciados geram apenas aviso.
# Sem dependências externas: usa apenas utilitários base (grep, wc, find, tr, sort).

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEMORIA="$ROOT/MEMORIA"
INDEX="$MEMORIA/INDEX.md"
MAX_LINES=600
fail=0

msg() { printf '%s\n' "$*"; }

if [ ! -f "$INDEX" ]; then
    msg "ERRO: $INDEX não existe."
    exit 1
fi

indexed="$(grep -oE 'MEMORIA/[A-Za-z0-9_./-]+\.md' "$INDEX" | sort -u)"

for f in $indexed; do
    if [ ! -f "$ROOT/$f" ]; then
        msg "ERRO: '$f' está referenciado no INDEX mas não existe."
        fail=1
    fi
done

files="$(find "$MEMORIA" -type f -name '*.md' | sort)"
for f in $files; do
    rel="${f#"$ROOT"/}"
    lines="$(wc -l < "$f" | tr -d ' ')"
    if [ "$lines" -gt "$MAX_LINES" ]; then
        msg "ERRO: '$rel' tem $lines linhas (máximo $MAX_LINES)."
        fail=1
    fi
    if [ "$rel" != "MEMORIA/INDEX.md" ] && ! printf '%s\n' "$indexed" | grep -qx "$rel"; then
        msg "AVISO: '$rel' não está referenciado no INDEX."
    fi
done

if [ "$fail" -ne 0 ]; then
    msg "Memória com problemas."
    exit 1
fi

msg "Memória OK (INDEX válido e máximo de $MAX_LINES linhas respeitado)."