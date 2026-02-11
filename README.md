# ArkOS Server Suite

A collection of lightweight server tools for ArkOS (R36S handheld device), turning your gaming device into a portable server running:
- ðŸ“± Telegram Bot for remote system monitoring
- ðŸŒ SOCKS5 Proxy Server with authentication
- ðŸ§¹ Automatic cleanup system to extend SD card lifespan

## Features

### 1. IP Telegram Bot (`ip_bot.py`)
- ðŸ“¡ Get public IP address remotely
- ðŸ”§ Monitor CPU usage in real-time
- ðŸ’¾ Check RAM usage percentage
- ðŸ”‹ Battery status with charging indicator
- ðŸ”’ Authorized user access only
- âš¡ Auto-starts on boot

### 2. SOCKS5 Proxy Server (`socks5_proxy.py`)
- ðŸ” Username/password authentication
- ðŸŒ Pure Python implementation (no compilation needed)
- ðŸš€ Lightweight (~10MB RAM)
- ðŸ”„ Auto-restarts on failure
- ðŸ”Œ IPv4 and domain name support
- âš¡ Auto-starts on boot

### 3. Auto Cleanup (`cleanup.sh` + `cleanup.service`)
- ðŸ—‘ï¸ Cleans APT cache, pip cache, Python bytecode
- â° Runs automatically on every boot
- ðŸ’¾ Extends SD card lifespan by reducing writes
- ðŸ“Š Logs cleanup results to `/tmp/cleanup.log`

---

## ðŸ“¦ Installation

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
sudo systemctl daemon-reload && \
echo "âœ… Files copied! Now configure your settings (see Configuration section)"
```

---

## âš™ï¸ Configuration

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

Edit the proxy script to change credentials and port:

```bash
sudo nano /opt/scripts/socks5_proxy.py
```

Find and replace these lines (around lines 12-15):
```python
PROXY_HOST = '0.0.0.0'           # Listen on all interfaces
PROXY_PORT = 1080                # Default SOCKS5 port
PROXY_USER = 'your_username'     # Change this!
PROXY_PASS = 'your_password'     # Change this!
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`)

---

## ðŸš€ Enable & Start Services

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

```bash
# Create systemd service for SOCKS5 proxy (if not exists)
sudo tee /etc/systemd/system/socks5proxy.service > /dev/null << 'EOF'
[Unit]
Description=SOCKS5 Proxy Server for ArkOS
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ark
WorkingDirectory=/opt/scripts
ExecStart=/usr/bin/python3 /opt/scripts/socks5_proxy.py
Restart=always
RestartSec=30

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

## ðŸ” Checking Logs & Status

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

# Check if port is listening
netstat -tuln | grep 1080

# Test connectivity from another device
# On Windows PowerShell:
Test-NetConnection -ComputerName <R36S_IP> -Port 1080

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

## ðŸŒ Port Forwarding for Public Access

To access your SOCKS5 proxy from the internet (outside your home network), you need to set up port forwarding on your router.

### Step 1: Find Your R36S Local IP

```bash
hostname -I
# Example output: 192.168.0.179
```

### Step 2: Configure Router Port Forwarding

1. Access your router admin panel (usually `192.168.0.1` or `192.168.1.1`)
2. Login with your router credentials
3. Find **Port Forwarding** section (may be under Advanced â†’ NAT/Firewall)
4. Add new port forwarding rule:
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
1. Settings â†’ Network Settings â†’ Manual Proxy Configuration
2. SOCKS Host: `YOUR_PUBLIC_IP`
3. Port: `1080`
4. Check "SOCKS v5"
5. OK

### âš ï¸ Security Considerations

- âœ… **Use strong password** for SOCKS5 proxy
- âœ… **Change default username** from `arkproxy`
- âœ… **Consider changing port** from 1080 to something non-standard
- âš ï¸ **Dynamic IP**: Most home ISPs use dynamic public IPs that change periodically
- ðŸ’¡ **Use Telegram bot** to get your current public IP anytime with `/ip` command

---

## ðŸ› Common Issues & Fixes

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

**Issue**: Telegram bot shows "ðŸ”§ CPU Usage: Error"

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

## ðŸ“ Service Management Commands

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

## ðŸ”„ Update Scripts

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

## ðŸ“Š Performance & Resource Usage

### Resource Consumption

| Service | RAM Usage | CPU Usage | Storage |
|---------|-----------|-----------|---------|
| Telegram Bot | ~15-20 MB | < 1% | 177 KB |
| SOCKS5 Proxy | ~8-12 MB | < 1% (idle) | 149 KB |
| Auto Cleanup | 0 MB (runs once) | N/A | 46 KB |

### Battery Impact

When running as a server with screen off:
- âš¡ Battery drain: ~3-5% per hour (WiFi only)
- ðŸ”‹ Estimated runtime: 20-30 hours on full charge
- ðŸ’¡ Keep plugged in for 24/7 server use

---

## ðŸŽ¯ Use Cases

### Personal VPN Alternative
Use SOCKS5 proxy to browse securely through your home connection when on public WiFi.

### Remote Monitoring
Check your home public IP and network status from anywhere via Telegram.

### IoT Server
Lightweight server for simple automation tasks, running 24/7 on minimal power.

### Development Testing
Test mobile apps behind different network configurations.

---

## ðŸ¤ Contributing

Feel free to:
- ðŸ› Report bugs via GitHub Issues
- ðŸ’¡ Suggest features
- ðŸ”§ Submit pull requests
- â­ Star the repository if you find it useful!

---

## ðŸ“œ License

MIT License - feel free to use and modify!

---

## âš ï¸ Disclaimer

- This is designed for **personal use** on **your own network**
- Running public servers may violate your ISP's Terms of Service
- Ensure strong passwords for any publicly accessible services
- ArkOS (Ubuntu 19.10) is EOL - no security updates available
- Use at your own risk

---

## ðŸ“š Additional Resources

- **ArkOS Wiki**: https://github.com/christianhaitian/arkos/wiki
- **R36S Community**: https://www.reddit.com/r/SBCGaming/
- **Telegram Bot API**: https://core.telegram.org/bots
- **SOCKS5 Protocol**: https://en.wikipedia.org/wiki/SOCKS

---

**Made with â¤ï¸ for the ArkOS/R36S Community**

Questions? Issues? Open a GitHub issue or discussion!
#   a r k o s - s e r v e r 
 
 
