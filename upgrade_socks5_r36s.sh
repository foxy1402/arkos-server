#!/bin/bash
# ArkOS SOCKS5 Proxy Upgrade - All-in-One Script

echo "=== ArkOS SOCKS5 Proxy Upgrade ==="
echo ""
echo "This will:"
echo "1. Pull latest code from GitHub"
echo "2. Backup current version"
echo "3. Install upgraded SOCKS5 proxy"
echo "4. Stop old service"
echo "5. Start upgraded service"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

cd /tmp
rm -rf arkos-server
git clone https://github.com/foxy1402/arkos-server.git
cd arkos-server

echo ""
echo "[1/5] Backing up current version..."
sudo cp /opt/scripts/socks5_proxy.py /opt/scripts/socks5_proxy.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "No backup needed"

echo "[2/5] Installing new socks5_proxy.py..."
sudo cp socks5_proxy.py /opt/scripts/
sudo chmod +x /opt/scripts/socks5_proxy.py

echo "[3/5] Installing new socks5proxy.service..."
sudo cp socks5proxy.service /etc/systemd/system/

echo "[4/6] Stopping old service..."
sudo systemctl stop socks5proxy.service
sleep 1

echo "[5/6] Reloading systemd..."
sudo systemctl daemon-reload

echo "[6/6] Starting upgraded service..."
sudo systemctl start socks5proxy.service

echo ""
echo "=== Checking Status ==="
sudo systemctl status socks5proxy.service --no-pager -l

echo ""
echo "? Upgrade complete!"
echo ""
echo "IMPORTANT: Change your credentials!"
echo "  sudo nano /etc/systemd/system/socks5proxy.service"
echo "  (Change SOCKS5_USER and SOCKS5_PASS)"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl restart socks5proxy.service"
echo ""
echo "View logs:"
echo "  sudo journalctl -u socks5proxy.service -f"
