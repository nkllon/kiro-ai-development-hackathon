#!/bin/bash
# Setup Redis on Vonnegut for Beast Mode Network
# Ubuntu 22.04 / POP!_OS

echo "🧬 Setting up Redis on Vonnegut for Beast Mode Network..."

# Update package list
sudo apt update

# Install Redis
echo "📦 Installing Redis..."
sudo apt install -y redis-server

# Configure Redis for network access
echo "🔧 Configuring Redis for network access..."

# Backup original config
sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.backup

# Configure Redis to listen on all interfaces
sudo sed -i 's/bind 127.0.0.1 ::1/bind 0.0.0.0/' /etc/redis/redis.conf

# Disable protected mode for local network access
sudo sed -i 's/protected-mode yes/protected-mode no/' /etc/redis/redis.conf

# Set a password (optional but recommended)
echo "requirepass beastmode2025" | sudo tee -a /etc/redis/redis.conf

# Enable Redis service
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Check Redis status
echo "📊 Redis status:"
sudo systemctl status redis-server --no-pager -l

# Test Redis connectivity
echo "🔍 Testing Redis connectivity..."
redis-cli ping

# Show Redis info
echo "ℹ️ Redis server info:"
redis-cli info server | head -10

# Open firewall for Redis (if UFW is enabled)
echo "🔥 Configuring firewall..."
if sudo ufw status | grep -q "Status: active"; then
    sudo ufw allow 6379/tcp
    echo "✅ Opened port 6379 for Redis"
else
    echo "ℹ️ UFW not active, no firewall rules needed"
fi

echo ""
echo "✅ Redis setup complete!"
echo "🌐 Redis should now be accessible from:"
echo "   - Local: redis://127.0.0.1:6379"
echo "   - Network: redis://$(hostname -I | awk '{print $1}'):6379"
echo ""
echo "🔐 Password: beastmode2025"
echo ""
echo "🧬 Ready for Beast Mode network coordination!"