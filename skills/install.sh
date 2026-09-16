#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
DEST_DIR=${CODEX_SKILLS_DIR:-${HOME}/.codex/skills}
DRY_RUN=0

usage() {
    cat <<'EOF'
Usage: ./install.sh [--dry-run] [--destination DIRECTORY]

Install all skills found next to this script into Codex's user skills directory.
The default destination is ~/.codex/skills, or $CODEX_SKILLS_DIR when set.
Existing skill directories are backed up before being replaced.
EOF
}

log() {
    printf '[codex-skills] %s\n' "$*"
}

die() {
    printf '[codex-skills] erreur: %s\n' "$*" >&2
    exit 1
}

run() {
    if (( DRY_RUN )); then
        printf '[codex-skills] +'
        printf ' %q' "$@"
        printf '\n'
    else
        "$@"
    fi
}

while (($#)); do
    case "$1" in
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --destination)
            (($# >= 2)) || die "--destination attend un répertoire"
            DEST_DIR=$2
            shift 2
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            usage >&2
            die "option inconnue: $1"
            ;;
    esac
done

[[ -d "$SCRIPT_DIR" ]] || die "répertoire source introuvable: $SCRIPT_DIR"

mapfile -t SKILLS < <(
    find "$SCRIPT_DIR" -mindepth 2 -maxdepth 2 -type f -name SKILL.md -printf '%h\n' \
        | sort
)

((${#SKILLS[@]} > 0)) || die "aucun skill contenant SKILL.md n'a été trouvé"

if (( DRY_RUN == 0 )); then
    mkdir -p -- "$DEST_DIR"
fi

BACKUP_DIR="$DEST_DIR/.backup/$(date +%Y%m%d-%H%M%S)"

for skill_dir in "${SKILLS[@]}"; do
    skill_name=${skill_dir##*/}
    destination="$DEST_DIR/$skill_name"

    if [[ -e "$destination" || -L "$destination" ]]; then
        if [[ -d "$destination" ]] && diff -rq -- "$skill_dir" "$destination" >/dev/null 2>&1; then
            log "Déjà à jour: $skill_name"
            continue
        fi

        log "Sauvegarde: $destination -> $BACKUP_DIR/$skill_name"
        run mkdir -p -- "$BACKUP_DIR"
        run mv -- "$destination" "$BACKUP_DIR/$skill_name"
    fi

    log "Installation: $skill_name -> $destination"
    run mkdir -p -- "$DEST_DIR"
    run cp -a -- "$skill_dir" "$destination"
done

log "Installation terminée (${#SKILLS[@]} skill(s))."
