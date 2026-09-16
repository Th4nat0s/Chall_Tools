#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
BACKUP_DIR="${HOME}/.config/configs-backup/$(date +%Y%m%d-%H%M%S)"

log() {
    printf '[configs] %s\n' "$*"
}

die() {
    printf '[configs] erreur: %s\n' "$*" >&2
    exit 1
}

install_packages() {
    if command -v apt-get >/dev/null 2>&1; then
        command -v sudo >/dev/null 2>&1 || die "sudo est requis pour installer les paquets"
        log "Installation des paquets vim, vim-pathogen, vim-syntastic, mc et tmux"
        sudo apt-get update
        sudo apt-get install -y vim vim-pathogen vim-syntastic mc tmux
    else
        die "gestionnaire de paquets non supporté: apt-get est requis"
    fi
}

install_config() {
    local source=$1
    local destination=$2
    local destination_dir

    destination_dir=$(dirname -- "$destination")
    mkdir -p -- "$destination_dir"

    if [[ -e "$destination" || -L "$destination" ]]; then
        if cmp -s -- "$source" "$destination" 2>/dev/null; then
            log "Déjà à jour: $destination"
            return
        fi
        mkdir -p -- "$BACKUP_DIR"
        cp -a -- "$destination" "$BACKUP_DIR/"
        log "Sauvegarde: $destination -> $BACKUP_DIR/"
    fi

    install -m 0644 -- "$source" "$destination"
    log "Installé: $destination"
}

install_packages

install_config "$SCRIPT_DIR/bashrc"      "$HOME/.bashrc"
install_config "$SCRIPT_DIR/gdbinit"     "$HOME/.gdbinit"
install_config "$SCRIPT_DIR/minirc.dfl"  "$HOME/.minirc.dfl"
install_config "$SCRIPT_DIR/rc_ssh"      "$HOME/.ssh/rc"
install_config "$SCRIPT_DIR/tmux.conf"   "$HOME/.tmux.conf"
install_config "$SCRIPT_DIR/vimrc"       "$HOME/.vimrc"
install_config "$SCRIPT_DIR/mc/ini"      "$HOME/.config/mc/ini"
install_config "$SCRIPT_DIR/mc/panels.ini" "$HOME/.config/mc/panels.ini"

chmod 0700 "$HOME/.ssh"
chmod 0700 "$HOME/.config/mc"
chmod 0700 "$HOME/.vim" 2>/dev/null || true
chmod 0700 "$HOME/.config/configs-backup" 2>/dev/null || true

log "Installation terminée. Rechargez Bash avec: source ~/.bashrc"
