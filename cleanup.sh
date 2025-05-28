#!/bin/bash
# clean un repo
# Vérifie si un argument est donné
if [ -z "$1" ]; then
  echo "Usage: $0 <git-repo-url>"
  exit 1
fi

REPO_URL="$1"
REPO_NAME=$(basename -s .git "$REPO_URL")
TMP_DIR="${REPO_NAME}.git"
BUNDLE_FILE="${REPO_NAME}.bundle"

# Clone le dépôt en mode --mirror
git clone --mirror "$REPO_URL" "$TMP_DIR" || exit 2

# Crée le bundle
cd "$TMP_DIR" || exit 3
git bundle create "../$BUNDLE_FILE" --all || exit 4
cd ..

# Compresse le bundle
xz "$BUNDLE_FILE" || exit 5

# Supprime le dépôt cloné
rm -rf "$TMP_DIR"

echo "Bundle compressé créé : ${BUNDLE_FILE}.xz"
