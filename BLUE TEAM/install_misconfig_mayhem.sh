#!/bin/bash

echo "======================================="
echo " Installing Misconfig Mayhem Dependencies"
echo " Kali Linux"
echo "======================================="

# Vérification root
if [ "$EUID" -ne 0 ]; then
  echo "[!] Please run as root (sudo)"
  exit 1
fi

echo "[+] Updating system..."
apt update && apt upgrade -y

echo "[+] Installing base tools..."
apt install -y \
  git \
  curl \
  wget \
  unzip \
  net-tools \
  ca-certificates \
  gnupg \
  lsb-release

echo "[+] Installing Docker..."
apt install -y docker.io docker-compose
systemctl enable docker
systemctl start docker

echo "[+] Adding current user to docker group..."
usermod -aG docker $SUDO_USER

echo "[+] Installing Python & pip..."
apt install -y python3 python3-pip python3-venv

echo "[+] Installing Python security/web dependencies..."
pip3 install --upgrade pip
pip3 install fastapi uvicorn pyjwt python-multipart requests

echo "[+] Installing Pentesting tools..."
apt install -y \
  nmap \
  nikto \
  gobuster \
  sqlmap \
  whatweb \
  hydra \
  jq

echo "[+] Installing Nuclei..."
GO_VERSION=1.22.0
wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz -O /tmp/go.tar.gz
rm -rf /usr/local/go
tar -C /usr/local -xzf /tmp/go.tar.gz
rm /tmp/go.tar.gz

echo 'export PATH=$PATH:/usr/local/go/bin' >> /etc/profile
export PATH=$PATH:/usr/local/go/bin

go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
ln -s /root/go/bin/nuclei /usr/local/bin/nuclei

echo "[+] Updating Nuclei templates..."
nuclei -update-templates

echo "[+] Installing wordlists..."
apt install -y wordlists
ln -s /usr/share/wordlists /wordlists || true

echo "======================================="
echo " Installation completed successfully!"
echo "======================================="
echo ""
echo "[IMPORTANT]"
echo " Log out and log back in so Docker works without sudo."
echo ""
echo " Useful commands:"
echo "   docker --version"
echo "   docker-compose --version"
echo "   nuclei -version"
echo "   nmap --version"
