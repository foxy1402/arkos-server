# ArkOS Developer Guide (R36S)

## System Overview

**Device**: R36S Handheld Gaming Console (Panel 3 variant)  
**OS**: ArkOS 2.0 (Based on Ubuntu 19.10 - EOL)  
**Kernel**: Linux 4.4.189  
**Architecture**: aarch64 (ARM Cortex-A35, 4 cores @ 1.5GHz)  
**RAM**: ~1GB available  
**Storage**: MicroSD card (slow I/O, limited write cycles)  
**Network**: WiFi only (no ethernet)

## Key Characteristics

### Power Management
- **Screen auto-sleep**: Display turns off after idle period to save battery
- **System keeps running**: SSH, services, and background processes continue when screen is off
- **Ideal for server use**: Can run 24/7 headless with screen off
- **Low power consumption**: Great for lightweight background tasks

### Display Architecture
- **Framebuffer-based**: No X11 server by default
- **EmulationStation**: Runs as systemd service with elevated VT/framebuffer access
- **Kernel VT restrictions**: User processes CANNOT access `/dev/tty0` or framebuffer directly
- **SDL2**: EmulationStation uses SDL2 in framebuffer mode
- **Panel 3 DTB**: Critical device tree file (`rk3326-r35s-linux.dtb`, 90,483 bytes)

### Architecture Restrictions
❌ **What DOES NOT work:**
- X11 applications (VT access denied even with sudo)
- Desktop environments (LXDE, Openbox, etc.)
- Framebuffer apps requiring VT access (links2, etc.)
- Display managers (LightDM, GDM, etc.)

✅ **What DOES work:**
- Headless services (web servers, bots, APIs)
- Background Python/Node.js scripts
- SSH access (local network + internet)
- EmulationStation tools (must use specific pattern)

## SSH Access

### Connection
```bash
ssh ark@192.168.0.179
# Password: ark
```

### Enable SSH (if disabled)
- Navigate to Options → Advanced → Services → SSH
- Or from terminal: `sudo systemctl enable ssh && sudo systemctl start ssh`

### Best Practices
- ✅ **Always develop via SSH** - screen sleep won't affect your connection
- ✅ **Use tmux/screen** for persistent sessions
- ✅ **Test scripts via SSH** before creating EmulationStation tools
- ⚠️ **WiFi connection** may drop - use stable network or connect via hotspot

## Package Management

### Update Package Lists
```bash
sudo apt update
```

### Install Packages
```bash
sudo apt install <package-name> -y
```

### Remove Packages
```bash
sudo apt remove --purge <package-name> -y
sudo apt autoremove -y  # Clean up dependencies
```

### Check Installed Packages
```bash
dpkg -l | grep <package-name>
```

### Note: Ubuntu 19.10 is EOL
- Many packages are outdated
- Security updates stopped
- Some PPAs may not work
- Consider building from source for latest versions

## Python Development

### Available Python
```bash
python3 --version  # Python 3.7.x
```

### Install Python Packages
```bash
# System-wide
sudo apt install python3-<package>

# Or use pip
sudo apt install python3-pip
pip3 install <package>
```

### Create Systemd Service for Python Script
```bash
# 1. Create your script
sudo nano /opt/scripts/mybot.py

# 2. Make it executable
sudo chmod +x /opt/scripts/mybot.py

# 3. Create systemd service
sudo nano /etc/systemd/system/mybot.service
```

**Service file template:**
```ini
[Unit]
Description=My Python Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ark
WorkingDirectory=/opt/scripts
ExecStart=/usr/bin/python3 /opt/scripts/mybot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable mybot.service
sudo systemctl start mybot.service
sudo systemctl status mybot.service
```

## EmulationStation Tools

### Tool Location
```bash
/opt/system/Tools/
```

### How It Works
- Any `.sh` script in this directory appears in EmulationStation Tools menu
- Scripts run with elevated privileges when launched from menu
- Apps/tools inherit EmulationStation's VT/display access

### Tool Script Template
```bash
#!/bin/bash
# Tool Name - Description

# Ensure root privileges
if [ "$(id -u)" -ne 0 ]; then
    exec sudo -- "$0" "$@"
fi

CURR_TTY="/dev/tty1"  # Output to console
export TERM=linux

# Start gamepad mapper for button control
if command -v /opt/inttools/gptokeyb &> /dev/null; then
    pkill -f "gptokeyb -1 mytool.sh" 2>/dev/null || true
    /opt/inttools/gptokeyb -1 "mytool.sh" -c "/opt/inttools/keys.gptk" >/dev/null 2>&1 &
fi

# Cleanup on exit
trap 'pkill -f "gptokeyb -1 mytool.sh"; exit 0' EXIT INT TERM

# Your tool logic here
printf "Hello from tool!\n" > "$CURR_TTY"

# Cleanup handled by trap
```

### Gamepad Button Mapping (gptokeyb)
```
SELECT (back) = ESC
START = Enter
A = Enter
B = Backspace
L1 = Page Up
R1 = Page Down
D-Pad = Arrow keys
```

### Important Notes
- ⚠️ **Tools without exit mechanism trap users** - always include way to exit
- ⚠️ **Can't detect gamepad input reliably** - `read` command doesn't work with gptokeyb
- ✅ **Best for quick actions** - show info and auto-exit
- ✅ **Use systemd services for persistent tasks** - not EmulationStation tools

## Useful Commands

### Process Management
```bash
# View running processes
ps aux | grep <name>
htop  # Interactive process viewer (if installed)

# Kill process
sudo pkill -9 -f "process-name"

# Kill by PID
sudo kill -9 <PID>
```

### System Info
```bash
# CPU usage
top -bn1 | grep "Cpu(s)"

# Memory usage
free -h
cat /proc/meminfo

# Disk usage
df -h

# System uptime
uptime

# Temperature (if available)
cat /sys/class/thermal/thermal_zone0/temp
```

### Network
```bash
# Check WiFi connection
nmcli dev status
nmcli connection show

# Get IP address
ip addr show wlan0
hostname -I

# Get public IP
curl -s ifconfig.me
curl -s icanhazip.com

# Test internet connectivity
ping -c 4 8.8.8.8
```

### Service Management
```bash
# List all services
systemctl list-units --type=service

# Check service status
systemctl status <service-name>

# Start/stop/restart service
sudo systemctl start <service-name>
sudo systemctl stop <service-name>
sudo systemctl restart <service-name>

# Enable/disable on boot
sudo systemctl enable <service-name>
sudo systemctl disable <service-name>

# View service logs
journalctl -u <service-name> -f  # Follow logs
journalctl -u <service-name> --since "10 minutes ago"
```

### File Operations
```bash
# Find files
find /path -name "filename"
find /opt/system -name "*.sh"

# Search file contents
grep -r "search term" /path/
grep -i "case insensitive" file.txt

# Disk usage by directory
du -sh /path/*
du -h --max-depth=1 /opt/
```

## Development Best Practices

### For Background Services
✅ **Use systemd services** - reliable, auto-restart, logs  
✅ **Set `Restart=always`** - recovers from crashes  
✅ **Log to journald** - use `systemctl status` and `journalctl`  
✅ **Test before enabling** - verify script works standalone first  
✅ **Use absolute paths** - `/usr/bin/python3`, not just `python3`

### For Network Services
✅ **Wait for network** - use `After=network-online.target`  
✅ **Handle disconnections** - implement retry logic  
✅ **Use lightweight libraries** - limited RAM available  
✅ **Avoid intensive operations** - slow CPU, SD card I/O

### Storage Considerations
⚠️ **SD card has limited write cycles**  
- Minimize frequent writes (logging, caching)
- Use `/tmp/` for temporary files (RAM disk)
- Rotate logs or limit size
- Consider disabling swap if not needed

**Auto-cleanup service installed:**  
✅ Runs on boot to protect SD card lifespan  
✅ Cleans: APT cache, pip cache, Python bytecode, old temp files, thumbnails  
✅ Check cleanup results: `cat /tmp/cleanup.log`  
✅ Manually run cleanup: `sudo /opt/scripts/cleanup.sh`

### Resource Limits
⚠️ **Limited RAM (~1GB)**  
- Keep services lightweight
- Avoid memory leaks
- Monitor with `free -h` and `htop`

⚠️ **Slow CPU**  
- Avoid heavy processing
- Use efficient algorithms
- Offload intensive tasks to remote servers

## Example: Telegram Bot for IP Reporting

### Install Dependencies
```bash
sudo apt update
sudo apt install python3-pip -y
pip3 install python-telegram-bot requests
```

### Create Bot Script
```bash
sudo mkdir -p /opt/scripts
sudo nano /opt/scripts/ip_bot.py
```

**Script content:**
```python
#!/usr/bin/env python3
import logging
from telegram.ext import Updater, CommandHandler
import requests

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except:
        return "Unable to fetch IP"

def ip_command(update, context):
    public_ip = get_public_ip()
    update.message.reply_text(f"Public IP: {public_ip}")

def main():
    # Replace with your bot token
    updater = Updater("YOUR_BOT_TOKEN_HERE", use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("ip", ip_command))
    
    updater.start_polling()
    logger.info("Bot started!")
    updater.idle()

if __name__ == '__main__':
    main()
```

### Create Systemd Service
```bash
sudo nano /etc/systemd/system/ipbot.service
```

**Service content:**
```ini
[Unit]
Description=Telegram IP Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ark
WorkingDirectory=/opt/scripts
ExecStart=/usr/bin/python3 /opt/scripts/ip_bot.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

### Enable and Start
```bash
sudo chmod +x /opt/scripts/ip_bot.py
sudo systemctl daemon-reload
sudo systemctl enable ipbot.service
sudo systemctl start ipbot.service
sudo systemctl status ipbot.service
```

### Monitor Logs
```bash
journalctl -u ipbot.service -f
```

## Troubleshooting

### Service won't start
```bash
# Check status
sudo systemctl status <service>

# Check logs
journalctl -u <service> -n 50

# Test script manually
/usr/bin/python3 /path/to/script.py

# Check permissions
ls -l /path/to/script.py
```

### WiFi disconnects
```bash
# Reconnect WiFi
nmcli connection up <connection-name>

# Auto-reconnect in script
while true; do
    # Your code here
    sleep 10
done
```

### Out of memory
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Kill memory hog
sudo pkill -f "process-name"
```

### SD card full
```bash
# Check disk usage
df -h

# Find large files
du -h / | sort -h | tail -20

# Clean apt cache
sudo apt clean
```

## Security Considerations

⚠️ **Default credentials**: Change default password (`passwd`)  
⚠️ **EOL OS**: No security updates for Ubuntu 19.10  
⚠️ **Exposed SSH**: Use strong passwords or SSH keys  
⚠️ **Public-facing services**: Be cautious exposing ports to internet  
⚠️ **API tokens**: Store securely, not in code  

## Backup Critical Files

Always backup before experiments:
```bash
# Panel 3 display driver (CRITICAL)
/boot/rk3326-r35s-linux.dtb  # 90,483 bytes

# System configuration
/etc/systemd/system/

# Custom scripts
/opt/scripts/
/opt/system/Tools/
```

## Resources

- **ArkOS Wiki**: https://github.com/christianhaitian/arkos/wiki
- **ArkOS GitHub**: https://github.com/christianhaitian/arkos
- **PortMaster**: Pre-built portable apps for ARM devices
- **EmulationStation**: https://emulationstation.org/

---

**Summary**: ArkOS on R36S is excellent for lightweight headless services (bots, scripts, automation) but NOT suitable for desktop apps or GUI applications due to kernel VT restrictions. Always develop via SSH and use systemd services for persistent background tasks.
