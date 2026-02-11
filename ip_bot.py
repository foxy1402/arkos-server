#!/usr/bin/env python3
"""
ArkOS Telegram Bot - System Status Reporter
Responds to /ip command with public IP, CPU, RAM, and battery status
"""

import subprocess
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Configuration
BOT_TOKEN = 'YOUR-BOT-TOKEN'
AUTHORIZED_USER = TELEGRAM-UID

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_public_ip():
    """Get public IP address using curl"""
    try:
        result = subprocess.run(
            ['curl', '-s', 'ifconfig.me'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip() or "Unable to fetch IP"
    except Exception as e:
        logger.error(f"Error getting IP: {e}")
        return "Error fetching IP"


def get_cpu_usage():
    """Get CPU usage percentage"""
    try:
        # Use top to get CPU idle percentage, then calculate usage
        result = subprocess.run(
            ['top', '-bn1'],
            capture_output=True,
            text=False,  # Get bytes instead
            timeout=5
        )
        output = result.stdout.decode('utf-8', errors='ignore')  # Ignore invalid UTF-8
        for line in output.split('\n'):
            if 'Cpu(s)' in line or '%Cpu' in line:
                # Parse CPU idle from top output
                parts = line.split(',')
                for part in parts:
                    if 'id' in part:  # idle percentage
                        idle = float(part.split()[0].replace('%', ''))
                        usage = 100 - idle
                        return f"{usage:.1f}%"
        return "N/A"
    except Exception as e:
        logger.error(f"Error getting CPU usage: {e}")
        return "Error"


def get_ram_usage():
    """Get RAM usage percentage"""
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            mem_total = 0
            mem_available = 0
            for line in lines:
                if line.startswith('MemTotal:'):
                    mem_total = int(line.split()[1])
                elif line.startswith('MemAvailable:'):
                    mem_available = int(line.split()[1])
            
            if mem_total > 0:
                mem_used = mem_total - mem_available
                usage_percent = (mem_used / mem_total) * 100
                return f"{usage_percent:.0f}%"
        return "N/A"
    except Exception as e:
        logger.error(f"Error getting RAM usage: {e}")
        return "Error"


def get_battery_info():
    """Get battery percentage and charging status"""
    try:
        # Read battery capacity
        with open('/sys/class/power_supply/battery/capacity', 'r') as f:
            capacity = f.read().strip()
        
        # Read charging status
        with open('/sys/class/power_supply/battery/status', 'r') as f:
            status = f.read().strip()
        
        # Determine icon based on charging status
        icon = "⚡" if "Charging" in status else "🔋"
        
        return f"{icon} {capacity}%"
    except Exception as e:
        logger.error(f"Error getting battery info: {e}")
        return "🔋 N/A"


def start(update, context):
    """Handle /start command"""
    user_id = update.effective_user.id
    logger.info(f"Start command from user {user_id}")
    
    if user_id != AUTHORIZED_USER:
        update.message.reply_text("⛔ Unauthorized")
        return
    
    update.message.reply_text(
        "🤖 *ArkOS R36S Status Bot*\n\n"
        "Commands:\n"
        "/ip - Get system status (IP, CPU, RAM, Battery)\n"
        "/start - Show this message",
        parse_mode='Markdown'
    )


def ip_command(update, context):
    """Handle /ip command"""
    user_id = update.effective_user.id
    logger.info(f"IP command from user {user_id}")
    
    if user_id != AUTHORIZED_USER:
        update.message.reply_text("⛔ Unauthorized")
        return
    
    # Get system information
    public_ip = get_public_ip()
    cpu_usage = get_cpu_usage()
    ram_usage = get_ram_usage()
    battery = get_battery_info()
    
    # Format response
    message = (
        "🌐 *ArkOS R36S Status*\n\n"
        f"📍 Public IP: `{public_ip}`\n"
        f"🔧 CPU Usage: {cpu_usage}\n"
        f"💾 RAM Usage: {ram_usage}\n"
        f"Battery: {battery}"
    )
    
    update.message.reply_text(message, parse_mode='Markdown')


def error_handler(update, context):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Start the bot"""
    logger.info("Starting ArkOS IP Bot...")
    
    # Create updater and dispatcher
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("ip", ip_command))
    dispatcher.add_error_handler(error_handler)
    
    # Start bot
    updater.start_polling()
    logger.info("Bot is running! Press Ctrl+C to stop.")
    updater.idle()


if __name__ == '__main__':
    main()
