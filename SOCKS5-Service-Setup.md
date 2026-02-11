# SOCKS5 Proxy Service Setup with Environment Variables

## Step 1: Copy the Updated Service File

```bash
cd /tmp/arkos-server
sudo cp socks5proxy.service /etc/systemd/system/
```

## Step 2: Edit Your Credentials

**IMPORTANT**: Change the default username and password!

```bash
sudo nano /etc/systemd/system/socks5proxy.service
```

Find these lines and change the values:
```ini
Environment="SOCKS5_USER=arkproxy"        # ← Change this!
Environment="SOCKS5_PASS=arkproxy2026"    # ← Change this!
```

Example:
```ini
Environment="SOCKS5_USER=myusername"
Environment="SOCKS5_PASS=SuperSecure123!"
```

**Optional**: Adjust other settings if needed:
- `SOCKS5_PORT=1080` - Change port number
- `SOCKS5_MAX_CONN=50` - Max concurrent connections
- `SOCKS5_TIMEOUT=30` - Connection timeout in seconds
- `SOCKS5_IDLE_TIMEOUT=300` - Idle timeout in seconds (5 minutes)

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

## Step 3: Reload and Restart the Service

```bash
# Reload systemd to read the new service file
sudo systemctl daemon-reload

# Restart the service with new settings
sudo systemctl restart socks5proxy.service

# Check if it's running
sudo systemctl status socks5proxy.service
```

## Step 4: Verify Logs

```bash
# View recent logs
sudo journalctl -u socks5proxy.service -n 50

# Follow logs in real-time
sudo journalctl -u socks5proxy.service -f
```

You should see:
```
SOCKS5 Proxy started on 0.0.0.0:1080
Username: myusername
Max connections: 50
Connection timeout: 30s
Idle timeout: 300s
```

## Future Changes

To change credentials later, just edit the service file again:

```bash
sudo nano /etc/systemd/system/socks5proxy.service
# Change Environment variables
sudo systemctl daemon-reload
sudo systemctl restart socks5proxy.service
```

## Environment Variable Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `SOCKS5_HOST` | `0.0.0.0` | Listen address (0.0.0.0 = all interfaces) |
| `SOCKS5_PORT` | `1080` | Port number |
| `SOCKS5_USER` | `arkproxy` | Username for authentication |
| `SOCKS5_PASS` | `arkproxy2026` | Password for authentication |
| `SOCKS5_MAX_CONN` | `50` | Maximum concurrent connections |
| `SOCKS5_TIMEOUT` | `30` | Connection timeout (seconds) |
| `SOCKS5_IDLE_TIMEOUT` | `300` | Idle connection timeout (seconds) |

## Security Tips

✅ **Use a strong password** - At least 12+ characters  
✅ **Change default username** - Don't use "arkproxy"  
✅ **Unique credentials** - Don't reuse passwords from other services  
✅ **Monitor logs** - Check for unauthorized access attempts  
✅ **Firewall** - Only expose to trusted networks if possible  

## Troubleshooting

**Service won't start:**
```bash
sudo journalctl -u socks5proxy.service -n 50
```

**Check if port is in use:**
```bash
netstat -tuln | grep 1080
```

**Test connection:**
```bash
curl --socks5-hostname username:password@localhost:1080 https://ifconfig.me
```
