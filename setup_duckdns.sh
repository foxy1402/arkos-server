#!/bin/bash
# DuckDNS Auto-Update Crontab Setup
# Replace YOUR_DOMAIN and YOUR_TOKEN with your actual DuckDNS credentials

DOMAIN="YOUR_DOMAIN"
TOKEN="YOUR_TOKEN"

(crontab -l 2>/dev/null; echo "*/5 * * * * curl -s 'https://www.duckdns.org/update?domains=$DOMAIN&token=$TOKEN&ip=' > /tmp/duck.log 2>&1") | crontab -
echo "Crontab updated. Current crontab:"
crontab -l
