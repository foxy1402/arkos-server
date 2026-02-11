#!/bin/bash
# ArkOS Auto Cleanup Script
# Runs on boot to minimize SD card wear

LOG_FILE="/tmp/cleanup.log"
echo "$(date): Starting ArkOS cleanup..." > $LOG_FILE

# Clean APT cache
apt-get clean >> $LOG_FILE 2>&1
echo "✓ APT cache cleaned" >> $LOG_FILE

# Clean pip cache
rm -rf /home/ark/.cache/pip/* >> $LOG_FILE 2>&1
echo "✓ Pip cache cleaned" >> $LOG_FILE

# Clean Python bytecode
find /opt/scripts -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find /home/ark -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
echo "✓ Python bytecode cleaned" >> $LOG_FILE

# Clean tmp files older than 1 day
find /tmp -type f -mtime +1 -delete 2>/dev/null
find /var/tmp -type f -mtime +1 -delete 2>/dev/null

# Clean DuckDNS log (if exists)
rm -f /tmp/duck.log 2>/dev/null

echo "✓ Old temp files cleaned" >> $LOG_FILE

# Clean thumbnail cache
rm -rf /home/ark/.cache/thumbnails/* 2>/dev/null
echo "✓ Thumbnail cache cleaned" >> $LOG_FILE

# Limit log file sizes (keep last 100 lines)
for logfile in /var/log/*.log; do
    if [ -f "$logfile" ] && [ $(wc -l < "$logfile") -gt 100 ]; then
        tail -n 100 "$logfile" > "$logfile.tmp" && mv "$logfile.tmp" "$logfile"
    fi
done
echo "✓ Log files trimmed" >> $LOG_FILE

# Clean package manager lists (safe to delete, will regenerate on apt update)
rm -rf /var/lib/apt/lists/* >> $LOG_FILE 2>&1
mkdir -p /var/lib/apt/lists/partial
echo "✓ APT lists cleaned" >> $LOG_FILE

echo "$(date): Cleanup completed!" >> $LOG_FILE

# Show summary
df -h / | tail -n 1 >> $LOG_FILE
