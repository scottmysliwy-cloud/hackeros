#!/bin/bash

# Set install mode to online since boot.sh is used for curl installations
export HACKEROS_ONLINE_INSTALL=true


sudo pacman -Syu --noconfirm --needed git

# Use custom repo if specified, otherwise default to basecamp/hackeros
hackeros_repo="${hackeros_repo:-scottmysliwy-cloud/hackeros}"

echo -e "\nCloning HackerOS from: https://github.com/${hackeros_repo}.git"
rm -rf ~/.local/share/hackeros/
git clone "https://github.com/${hackeros_repo}.git" ~/.local/share/hackeros >/dev/null

# Use custom branch if instructed, otherwise default to master
hackeros_ref="${hackeros_ref:-master}"
if [[ $hackeros_ref != "master" ]]; then
  echo -e "\e[32mUsing branch: $hackeros_ref\e[0m"
  cd ~/.local/share/hackeros
  git fetch origin "${hackeros_ref}" && git checkout "${hackeros_ref}"
  cd -
fi

echo -e "\nInstallation starting..."
source ~/.local/share/hackeros/install.sh