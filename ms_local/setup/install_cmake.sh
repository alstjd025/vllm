#!/bin/bash
set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CMAKE_VERSION="3.28.1"
INSTALL_PREFIX="/usr/local"

step() {
    echo -e "\n${GREEN}==>${NC} $1"
}

warn() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

error() {
    echo -e "${RED}ERROR:${NC} $1"
    exit 1
}

# Check current CMake version
step "Checking current CMake version..."
if command -v cmake &> /dev/null; then
    CURRENT_VERSION=$(cmake --version | head -n1 | awk '{print $3}')
    echo "Current CMake version: $CURRENT_VERSION"
    
    if [ "$CURRENT_VERSION" == "$CMAKE_VERSION" ]; then
        echo "CMake $CMAKE_VERSION is already installed."
        read -p "Reinstall anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Skipping installation."
            exit 0
        fi
    fi
else
    echo "CMake not found."
fi

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" == "x86_64" ]; then
    ARCH_SUFFIX="x86_64"
elif [ "$ARCH" == "aarch64" ]; then
    ARCH_SUFFIX="aarch64"
else
    error "Unsupported architecture: $ARCH"
fi

CMAKE_FILE="cmake-${CMAKE_VERSION}-linux-${ARCH_SUFFIX}.sh"
DOWNLOAD_URL="https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/${CMAKE_FILE}"

# Download CMake
step "Downloading CMake ${CMAKE_VERSION} for ${ARCH_SUFFIX}..."
cd /tmp
if [ -f "$CMAKE_FILE" ]; then
    warn "File $CMAKE_FILE already exists, removing..."
    rm -f "$CMAKE_FILE"
fi

wget "$DOWNLOAD_URL" || error "Download failed"

# Make executable
chmod +x "$CMAKE_FILE"

# Remove old CMake (optional)
if command -v apt &> /dev/null; then
    step "Removing old CMake from apt..."
    sudo apt remove -y cmake 2>/dev/null || true
fi

# Install new CMake
step "Installing CMake to ${INSTALL_PREFIX}..."
sudo ./"$CMAKE_FILE" --prefix="${INSTALL_PREFIX}" --skip-license --exclude-subdir

# Verify installation
step "Verifying installation..."
NEW_CMAKE_PATH="${INSTALL_PREFIX}/bin/cmake"

if [ ! -f "$NEW_CMAKE_PATH" ]; then
    error "Installation failed: $NEW_CMAKE_PATH not found"
fi

NEW_VERSION=$("$NEW_CMAKE_PATH" --version | head -n1 | awk '{print $3}')
echo "Installed CMake version: $NEW_VERSION"

# Check PATH
step "Checking PATH configuration..."
if ! echo "$PATH" | grep -q "${INSTALL_PREFIX}/bin"; then
    warn "${INSTALL_PREFIX}/bin is not in PATH"
    echo ""
    echo "Add this to your ~/.bashrc or ~/.bash_profile:"
    echo "  export PATH=\"${INSTALL_PREFIX}/bin:\$PATH\""
    echo ""
    echo "Or run now:"
    echo "  export PATH=\"${INSTALL_PREFIX}/bin:\$PATH\""
fi

# Cleanup
step "Cleaning up..."
rm -f "/tmp/$CMAKE_FILE"

echo ""
echo "=================================================="
echo -e "${GREEN}CMake ${CMAKE_VERSION} installed successfully!${NC}"
echo "=================================================="
echo ""
echo "Location: $NEW_CMAKE_PATH"
echo "Version:  $NEW_VERSION"
echo ""
echo "If 'cmake --version' shows old version, run:"
echo "  export PATH=\"${INSTALL_PREFIX}/bin:\$PATH\""
echo "  hash -r"
echo ""
