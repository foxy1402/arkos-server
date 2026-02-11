# ArkOS Server Suite

A collection of lightweight server tools for ArkOS (R36S handheld device), turning your gaming device into a portable server running:
- Telegram Bot for remote system monitoring
- SOCKS5 Proxy Server with authentication
- Automatic cleanup system to extend SD card lifespan

## Features

### 1. IP Telegram Bot (`ip_bot.py`)
- Get public IP address remotely
- Monitor CPU usage in real-time
- Check RAM usage percentage
- Battery status with charging indicator
- Authorized user access only
- Auto-starts on boot

### 2. SOCKS5 Proxy Server (`socks5_proxy.py`)
- **Production-grade with security hardening**
- **Self-healing** - Auto-kills old instances and frees ports
- Username/password authentication (SOCKS5 RFC 1928)
- Environment variable configuration (no code edits needed)
- Rate limiting (5 auth failures per 60s per IP)
- Connection timeout (30s) and idle timeout (5 min)
- Max connections limit (50 concurrent - protects your device)
- IPv4 and domain name support
- Pure Python - no compilation needed
- Lightweight (~10-15MB RAM)
- Auto-restarts on failure
- Auto-starts on boot
- Comprehensive logging to `/var/log/socks5_proxy.log`

### 3. Auto Cleanup (`cleanup.sh` + `cleanup.service`)
- Cleans APT cache, pip cache, Python bytecode
- Runs automatically on every boot
- Extends SD card lifespan by reducing writes
- Logs cleanup results to `/tmp/cleanup.log`

---

## Installation
### Prerequisites

SSH into your ArkOS device:
```bash
ssh ark@<YOUR_R36S_IP>
# Default password: ark
```

### Quick Install (One Command)

```bash
cd /tmp && \
git clone https://github.com/foxy1402/arkos-server.git && \
cd arkos-server && \
sudo cp ip_bot.py socks5_proxy.py cleanup.sh /opt/scripts/ && \
sudo chmod +x /opt/scripts/*.sh /opt/scripts/*.py && \
sudo cp cleanup.service /etc/systemd/system/ && \
sudo cp socks5proxy.service /etc/systemd/system/ && \
sudo touch /var/log/socks5_proxy.log && \
sudo chown ark:ark /var/log/socks5_proxy.log && \
sudo systemctl daemon-reload && \
echo "Files copied! Now configure your settings (see Configuration section)"
```

---

## Configuration
### 1. Configure Telegram Bot

Edit the bot script to add your bot token and Telegram user ID:

```bash
sudo nano /opt/scripts/ip_bot.py
```

Find and replace these lines (around lines 12-13):
```python
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'  # Get from @BotFather
AUTHORIZED_USER = 123456789         # Your Telegram user ID
```

**How to get your Telegram user ID:**
- Message [@userinfobot](https://t.me/userinfobot) on Telegram
- It will reply with your user ID

Save and exit (`Ctrl+X`, then `Y`, then `Enter`)

### 2. Configure SOCKS5 Proxy

**NEW: Environment Variable Configuration (Recommended)**

Edit the systemd service file to change credentials without touching code:

```bash
sudo nano /etc/systemd/system/socks5proxy.service
```

Find and edit these environment variables:
```ini
Environment="SOCKS5_USER=arkproxy"        # Change this!
Environment="SOCKS5_PASS=arkproxy2026"    # Change this!
Environment="SOCKS5_PORT=1080"            # Optional: change port
Environment="SOCKS5_MAX_CONN=50"          # Optional: max connections
```

Save, then apply changes:
```bash
sudo systemctl daemon-reload
sudo systemctl restart socks5proxy.service
```

**Alternative: Edit Python file directly (Old method)**

```bash
sudo nano /opt/scripts/socks5_proxy.py
```

Find and replace defaults (around lines 19-20):
```python
PROXY_USER = os.getenv('SOCKS5_USER', 'your_username')
PROXY_PASS = os.getenv('SOCKS5_PASS', 'your_password')
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`)

---

## Enable & Start Services
### Start Telegram Bot

```bash
# Create systemd service for IP bot (if not exists)
sudo tee /etc/systemd/system/ipbot.service > /dev/null << 'EOF'
[Unit]
Description=Telegram IP Bot for ArkOS
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ark
WorkingDirectory=/opt/scripts
ExecStart=/usr/bin/python3 /opt/scripts/ip_bot.py
Restart=always
RestartSec=30
StandardOutput=/tmp/ip_bot.log
StandardError=/tmp/ip_bot.log

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable ipbot.service
sudo systemctl start ipbot.service
sudo systemctl status ipbot.service
```

### Start SOCKS5 Proxy

**Method 1: Use the provided service file (Recommended)**

```bash
# Copy the service file
sudo cp socks5proxy.service /etc/systemd/system/

# Create log file
sudo touch /var/log/socks5_proxy.log
sudo chown ark:ark /var/log/socks5_proxy.log

# Edit credentials BEFORE starting
sudo nano /etc/systemd/system/socks5proxy.service
# Change SOCKS5_USER and SOCKS5_PASS values, then save

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable socks5proxy.service
sudo systemctl start socks5proxy.service
sudo systemctl status socks5proxy.service

# View logs to see self-healing in action
tail -f /var/log/socks5_proxy.log
```

**Method 2: Manual service creation**

```bash
# Create systemd service for SOCKS5 proxy
sudo tee /etc/systemd/system/socks5proxy.service > /dev/null << 'EOF'
[Unit]
Description=SOCKS5 Proxy Server for ArkOS
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ark
WorkingDirectory=/opt/scripts

# Change these values!
Environment="SOCKS5_USER=arkproxy"
Environment="SOCKS5_PASS=arkproxy2026"
Environment="SOCKS5_PORT=1080"
Environment="SOCKS5_MAX_CONN=50"

ExecStart=/usr/bin/python3 /opt/scripts/socks5_proxy.py
Restart=always
RestartSec=30

# Logging
StandardOutput=append:/var/log/socks5_proxy.log
StandardError=append:/var/log/socks5_proxy.log

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable socks5proxy.service
sudo systemctl start socks5proxy.service
sudo systemctl status socks5proxy.service
```

### Enable Auto Cleanup

```bash
# Already enabled during installation
sudo systemctl enable cleanup.service
sudo systemctl status cleanup.service

# Manually run cleanup anytime
sudo /opt/scripts/cleanup.sh
cat /tmp/cleanup.log
```

---

## SOCKS5 Self-Healing Features

The SOCKS5 proxy includes advanced self-healing capabilities that make it production-ready:

### Automatic Recovery
- **Auto-kills old instances** - Detects and terminates previous processes on startup
- **Port conflict resolution** - Automatically frees port 1080 if in use
- **Retry logic** - 3 automatic retry attempts if binding fails
- **Graceful shutdown** - Handles SIGTERM/SIGINT signals properly

### Security Features
- **Rate limiting** - Max 5 auth failures per 60 seconds per IP
- **Connection timeout** - 30-second timeout prevents hanging connections
- **Idle timeout** - 5-minute idle timeout for inactive connections
- **Max connections** - Limited to 50 concurrent connections (protects your R36S)
- **Input validation** - All SOCKS5 packets validated before processing
- **No password logging** - Credentials never appear in logs

### What You'll See in Logs
```
SOCKS5 Proxy Server for ArkOS R36S
Production-Ready with Self-Healing
⚠ psutil not available - basic self-healing only
==================================================
Checking for old instances...
Checking port availability...
Port 1080 is available
✓ SOCKS5 Proxy started successfully on 0.0.0.0:1080
✓ Username: arkproxy
✓ Max connections: 50
✓ Connection timeout: 30s
✓ Idle timeout: 300s
✓ PID: 12095
==================================================
```

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `SOCKS5_HOST` | `0.0.0.0` | Listen address (0.0.0.0 = all interfaces) |
| `SOCKS5_PORT` | `1080` | Port number |
| `SOCKS5_USER` | `arkproxy` | Username for authentication |
| `SOCKS5_PASS` | `arkproxy2026` | Password for authentication |
| `SOCKS5_MAX_CONN` | `50` | Maximum concurrent connections |
| `SOCKS5_TIMEOUT` | `30` | Connection timeout (seconds) |
| `SOCKS5_IDLE_TIMEOUT` | `300` | Idle connection timeout (seconds) |

---

## Checking Logs & Status
### Telegram Bot Logs

```bash
# Check service status
sudo systemctl status ipbot.service

# View logs (last 50 lines)
tail -50 /tmp/ip_bot.log

# Follow logs in real-time
tail -f /tmp/ip_bot.log

# Restart if needed
sudo systemctl restart ipbot.service
```

### SOCKS5 Proxy Logs

```bash
# Check service status
sudo systemctl status socks5proxy.service

# View logs (last 50 lines)
tail -50 /var/log/socks5_proxy.log

# Follow logs in real-time
tail -f /var/log/socks5_proxy.log

# Check if port is listening
netstat -tuln | grep 1080

# Test connectivity from another device
# On Windows PowerShell:
Test-NetConnection -ComputerName <R36S_IP> -Port 1080

# Test with curl (from Linux/Mac):
curl --socks5-hostname username:password@<R36S_IP>:1080 https://ifconfig.me

# Restart if needed
sudo systemctl restart socks5proxy.service
```

### Auto Cleanup Logs

```bash
# View last cleanup results
cat /tmp/cleanup.log

# Check disk usage
df -h /

# Check service status
sudo systemctl status cleanup.service

# Manually run cleanup
sudo /opt/scripts/cleanup.sh
```

---

## Port Forwarding for Public Access
To access your SOCKS5 proxy from the internet (outside your home network), you need to set up port forwarding on your router.

### Step 1: Find Your R36S Local IP

```bash
hostname -I
# Example output: 192.168.0.179
```

### Step 2: Configure Router Port Forwarding

1. Access your router admin panel (usually `192.168.0.1` or `192.168.1.1`)
2. Login with your router credentials
3. Find **Port Forwarding** section (may be under Advanced NAT/Firewall)4. Add new port forwarding rule:
   - **Service Name**: SOCKS5-ArkOS
   - **External Port**: 1080 (or any port you prefer)
   - **Internal IP**: `192.168.0.179` (your R36S IP)
   - **Internal Port**: 1080
   - **Protocol**: TCP
   - **Enable**: Yes

5. Save settings

### Step 3: Find Your Public IP

From R36S:
```bash
curl ifconfig.me
# This is your public IP address
```

Or send `/ip` command to your Telegram bot!

### Step 4: Connect to Your Proxy

Now you can connect from anywhere using:
- **Host**: `YOUR_PUBLIC_IP` (from Step 3)
- **Port**: `1080` (or your custom external port)
- **Username**: `your_username` (from config)
- **Password**: `your_password` (from config)

**Example with curl:**
```bash
curl --socks5-hostname your_username:your_password@YOUR_PUBLIC_IP:1080 https://ifconfig.me
```

**Browser Setup (Firefox):**
1. Settings Network Settings Manual Proxy Configuration2. SOCKS Host: `YOUR_PUBLIC_IP`
3. Port: `1080`
4. Check "SOCKS v5"
5. OK

### ï¸ Security Considerations

- **Use strong password** for SOCKS5 proxy
- **Change default username** from `arkproxy`
- **Consider changing port** from 1080 to something non-standard
- ï¸ **Dynamic IP**: Most home ISPs use dynamic public IPs that change periodically
- **Use Telegram bot** to get your current public IP anytime with `/ip` command

---

## Common Issues & Fixes
### Telegram Bot Not Responding

**Issue**: Bot doesn't reply to `/ip` command

**Fix 1**: Check if bot is running
```bash
sudo systemctl status ipbot.service
```

**Fix 2**: Check logs for errors
```bash
tail -50 /tmp/ip_bot.log
```

**Fix 3**: Verify bot token is correct
```bash
sudo nano /opt/scripts/ip_bot.py
# Check BOT_TOKEN and AUTHORIZED_USER values
```

**Fix 4**: Restart bot
```bash
sudo systemctl restart ipbot.service
```

**Fix 5**: Check if python-telegram-bot is installed
```bash
pip3 show python-telegram-bot
# If not installed:
pip3 install python-telegram-bot==13.15
```

### SOCKS5 Proxy Connection Failed

**Issue**: Cannot connect to proxy

**Fix 1**: Check if service is running
```bash
sudo systemctl status socks5proxy.service
```

**Fix 2**: Verify port is listening
```bash
netstat -tuln | grep 1080
# Should show: tcp 0 0.0.0.0:1080 0.0.0.0:* LISTEN
```

**Fix 3**: Test from same network first
```bash
# On another device in same WiFi:
curl --socks5-hostname username:password@192.168.0.179:1080 http://ifconfig.me
```

**Fix 4**: Check firewall (if enabled)
```bash
sudo ufw status
# If active, allow port:
sudo ufw allow 1080/tcp
```

**Fix 5**: Restart service
```bash
sudo systemctl restart socks5proxy.service
```

### CPU Stats Showing "Error"

**Issue**: Telegram bot shows "CPU Usage: Error"
**Fix**: This was due to UTF-8 encoding issue in `top` command output. Make sure you have the latest `ip_bot.py` version from the repo:

```bash
cd /tmp/arkos-server
git pull
sudo cp ip_bot.py /opt/scripts/
sudo systemctl restart ipbot.service
```

The fix changes `text=True` to `text=False` in subprocess and adds `errors='ignore'` to UTF-8 decoding.

### Service Won't Start

**Issue**: Service fails to start or immediately exits

**Fix 1**: Check for Python errors
```bash
# Test script manually
sudo python3 /opt/scripts/ip_bot.py
# Or
sudo python3 /opt/scripts/socks5_proxy.py
```

**Fix 2**: Check permissions
```bash
ls -l /opt/scripts/
# Should show: -rwxr-xr-x for .py and .sh files

# Fix if needed:
sudo chmod +x /opt/scripts/*.py /opt/scripts/*.sh
```

**Fix 3**: Check systemd service file
```bash
sudo systemctl cat ipbot.service
sudo systemctl cat socks5proxy.service

# Reload if you made changes:
sudo systemctl daemon-reload
```

### Port Already in Use

**Issue**: `OSError: [Errno 98] Address already in use`

**Fix**: Another process is using the port

```bash
# Find what's using port 1080
sudo netstat -tulpn | grep 1080

# Kill the process (replace PID with actual number)
sudo kill -9 <PID>

# Or restart the service
sudo systemctl restart socks5proxy.service
```

### SD Card Running Out of Space

**Issue**: Disk usage at 90%+

**Fix 1**: Run cleanup manually
```bash
sudo /opt/scripts/cleanup.sh
cat /tmp/cleanup.log
df -h /
```

**Fix 2**: Clean more aggressively
```bash
# Remove old kernels (if any)
sudo apt autoremove -y

# Clean all package cache
sudo apt clean

# Remove thumbnail cache
rm -rf ~/.cache/thumbnails/*

# Check largest directories
du -sh /* 2>/dev/null | sort -h | tail -10
```

---

## Upgrading to Latest Version

To upgrade your SOCKS5 proxy to the latest version with self-healing:

```bash
# SSH into your R36S
ssh ark@<YOUR_R36S_IP>

# Stop the old service
sudo systemctl stop socks5proxy.service

# Pull latest code
cd /tmp
rm -rf arkos-server
git clone https://github.com/foxy1402/arkos-server.git
cd arkos-server

# Backup old version
sudo cp /opt/scripts/socks5_proxy.py /opt/scripts/socks5_proxy.py.backup

# Copy new files
sudo cp socks5_proxy.py /opt/scripts/
sudo cp socks5proxy.service /etc/systemd/system/

# Create log file if it doesn't exist
sudo touch /var/log/socks5_proxy.log
sudo chown ark:ark /var/log/socks5_proxy.log

# Restart with new version
sudo systemctl daemon-reload
sudo systemctl start socks5proxy.service

# Check status and logs
sudo systemctl status socks5proxy.service
tail -f /var/log/socks5_proxy.log
```

**Don't forget to update your credentials!**
```bash
sudo nano /etc/systemd/system/socks5proxy.service
# Change SOCKS5_USER and SOCKS5_PASS
sudo systemctl daemon-reload
sudo systemctl restart socks5proxy.service
```

---

## Service Management Commands
### Quick Reference

```bash
# Start service
sudo systemctl start <service-name>

# Stop service
sudo systemctl stop <service-name>

# Restart service
sudo systemctl restart <service-name>

# Enable on boot
sudo systemctl enable <service-name>

# Disable from boot
sudo systemctl disable <service-name>

# Check status
sudo systemctl status <service-name>

# View logs
journalctl -u <service-name> -f
```

**Service names:**
- `ipbot.service` - Telegram Bot
- `socks5proxy.service` - SOCKS5 Proxy
- `cleanup.service` - Auto Cleanup

---

## Update Scripts
To get the latest versions from GitHub:

```bash
cd /tmp
rm -rf arkos-server  # Remove old copy
git clone https://github.com/foxy1402/arkos-server.git
cd arkos-server

# Backup your current configs (important!)
sudo cp /opt/scripts/ip_bot.py /opt/scripts/ip_bot.py.backup
sudo cp /opt/scripts/socks5_proxy.py /opt/scripts/socks5_proxy.py.backup

# Copy new files
sudo cp ip_bot.py socks5_proxy.py cleanup.sh /opt/scripts/
sudo chmod +x /opt/scripts/*.sh /opt/scripts/*.py

# Re-edit your configs (bot token, proxy credentials, etc.)
sudo nano /opt/scripts/ip_bot.py
sudo nano /opt/scripts/socks5_proxy.py

# Restart services
sudo systemctl restart ipbot.service
sudo systemctl restart socks5proxy.service
```

---

## Performance & Resource Usage
### Resource Consumption

| Service | RAM Usage | CPU Usage | Storage |
|---------|-----------|-----------|---------|
| Telegram Bot | ~15-20 MB | < 1% | 177 KB |
| SOCKS5 Proxy | ~8-12 MB | < 1% (idle) | 149 KB |
| Auto Cleanup | 0 MB (runs once) | N/A | 46 KB |

### Battery Impact

When running as a server with screen off:
- Battery drain: ~3-5% per hour (WiFi only)
- Estimated runtime: 20-30 hours on full charge
- Keep plugged in for 24/7 server use

---

## Use Cases
### Personal VPN Alternative
Use SOCKS5 proxy to browse securely through your home connection when on public WiFi.

### Remote Monitoring
Check your home public IP and network status from anywhere via Telegram.

### IoT Server
Lightweight server for simple automation tasks, running 24/7 on minimal power.

### Development Testing
Test mobile apps behind different network configurations.

---

## Contributing

Feel free to:
- Report bugs via GitHub Issues
- Suggest features
- Submit pull requests
- Star the repository if you find it useful!

---

## License
MIT License - feel free to use and modify!

---

## ï¸ Disclaimer
- This is designed for **personal use** on **your own network**
- Running public servers may violate your ISP's Terms of Service
- Ensure strong passwords for any publicly accessible services
- ArkOS (Ubuntu 19.10) is EOL - no security updates available
- Use at your own risk

---

## Additional Resources
- **ArkOS Wiki**: https://github.com/christianhaitian/arkos/wiki
- **R36S Community**: https://www.reddit.com/r/SBCGaming/
- **Telegram Bot API**: https://core.telegram.org/bots
- **SOCKS5 Protocol**: https://en.wikipedia.org/wiki/SOCKS

---

**Made with for the ArkOS/R36S Community**
Questions? Issues? Open a GitHub issue or discussion!
#   a r k o s - s e r v e r 
 
 