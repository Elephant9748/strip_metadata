#! /bin/bash

set -e
set -o pipefail

data="Hi-------!"
printf "Input Passphrase on images file: "
read -rs passphrase
printf "%s" "$passphrase"
printf "\n"

encrypted=$(echo -n "secret" | gpg --yes --batch --passphrase-fd 0 --symmetric --s2k-mode 3 --s2k-count 65011712 --s2k-digest-algo SHA512 --cipher-algo AES256 --armor<<<"$data")

printf "%s\n" "$encrypted"

echo -n "secret" | gpg --yes --batch --passphrase-fd 0 --symmetric --s2k-mode 3 --s2k-count 65011712 --s2k-digest-algo SHA512 --cipher-algo AES256 --armor<<<"this is encrypted data"
