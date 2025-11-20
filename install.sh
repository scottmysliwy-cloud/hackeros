#!/bin/bash
set -e

USER="scott"



echo "🚀 Bootstrapping Hackeros..."

# 1. Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Ensure uv is in the path for this session
    source $HOME/.cargo/env
else
    echo "✅ uv is already installed"
fi

# 2. Install Python (uv manages this automatically, but we can be explicit)
echo "🐍 Ensuring Python is available..."
uv python install

# 3. Create Virtual Environment
echo "🛠️  Creating virtual environment..."
uv venv --allow-existing

# 4. Install Project Dependencies
echo "📥 Installing dependencies..."
# Activate venv for the install command or use uv pip directly
source .venv/bin/activate
uv pip install -e ".[dev]"
source ~/.bashrc

pacman -S --noconfirm openssh which
systemctl enable sshd
systemctl start sshd

# create user with wheel group
useradd -m -G wheel -s /bin/bash $USER

passwd $USER

echo "✨ Done! Activate your environment with:"
echo "   source .venv/bin/activate"
