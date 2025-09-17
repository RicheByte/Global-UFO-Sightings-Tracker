#!/usr/bin/env bash
# TE: Hardened Kali VM Setup Script (idempotent)
# TE: Run this inside your Kali VM. Do NOT run on your host machine.
# TE: Make a VM snapshot BEFORE running. Some items (disk encryption, VM settings)
# TE: must be done manually through your hypervisor UI and cannot be fully automated.
# TE: This script focuses on OS-level hardening: user creation, SSH hardening,
# TE: firewall (UFW), fail2ban, AppArmor, disable IPv6, basic audit & logging, package updates.
# TE: Review the script before running. You are responsible for changes to your system.
# TE: Usage: sudo bash hardened_kali_setup.sh

set -euo pipefail
LOG="/var/log/hardening-script.log"

echo "TE: Starting Kali hardening script. Logging to $LOG"
exec > >(tee -a "$LOG") 2>&1

# TE: Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "TE: Please run as root (sudo). Exiting."
  exit 1
fi

# TE: ------- CONFIGURABLE VARIABLES -------
PENTEST_USER="pentest"
SSH_ALLOWED_USER="${PENTEST_USER}"
SSH_PORT=22          # TE: change if you want non-standard SSH port and update UFW rules below
ENABLE_SSH=false     # TE: set to true if you need SSH access to the VM
# TE: If you use SSH, ensure you copy your public key to ~${PENTEST_USER}/.ssh/authorized_keys manually
# TE: or use the putty/ssh-copy-id equivalents from your host.

# TE: ------- Update system & install basic packages -------
echo "TE: Updating system packages and installing required software..."
apt-get update -y
apt-get -y full-upgrade
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  curl git vim ufw tor proxychains4 fail2ban apparmor apparmor-utils auditd

# TE: ------- Create non-root user & sudo privileges -------
if id -u "$PENTEST_USER" >/dev/null 2>&1; then
  echo "TE: User $PENTEST_USER already exists. Skipping creation."
else
  echo "TE: Creating user $PENTEST_USER with sudo privileges."
  # TE: create user without password prompt (you may want to set/rotate password manually)
  adduser --disabled-password --gecos "" "$PENTEST_USER"
  usermod -aG sudo "$PENTEST_USER"
  echo "TE: Set a password for $PENTEST_USER now (recommended):"
  passwd "$PENTEST_USER" || true
fi

# TE: ------- SSH Hardening -------
if [ "$ENABLE_SSH" = true ]; then
  echo "TE: Enabling and hardening SSH (you set ENABLE_SSH=true)."
  sed -i 's/^#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config || true
  sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config || true
  sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config || true
  sed -i 's/^PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config || true
  # TE: Restrict to the allowed user
  if grep -q "^AllowUsers" /etc/ssh/sshd_config; then
    sed -i "s/^AllowUsers.*/AllowUsers ${SSH_ALLOWED_USER}/" /etc/ssh/sshd_config
  else
    echo "AllowUsers ${SSH_ALLOWED_USER}" >> /etc/ssh/sshd_config
  fi
  systemctl restart sshd || service ssh restart || true
else
  echo "TE: SSH hardening skipped (ENABLE_SSH=false). If you need SSH, set ENABLE_SSH=true and re-run."
fi

# TE: ------- UFW Firewall -------
echo "TE: Configuring UFW (Uncomplicated Firewall)..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# TE: If SSH is enabled, allow it but restrict to source if desired (manual edit suggested)
if [ "$ENABLE_SSH" = true ]; then
  ufw allow "${SSH_PORT}/tcp"
  echo "TE: Allowed SSH port ${SSH_PORT} through UFW (ENABLE_SSH=true)."
fi

# TE: Optional: add extra safe rules here (example commented)
# TE: ufw allow from 192.168.56.1 to any port 22 proto tcp
ufw logging on
ufw --force enable
ufw status verbose

# TE: ------- fail2ban -------
echo "TE: Ensuring fail2ban is enabled and running..."
systemctl enable --now fail2ban || true
# TE: Add a simple SSH jail if SSH is enabled
if [ "$ENABLE_SSH" = true ]; then
  cat > /etc/fail2ban/jail.d/sshd-local.conf <<'EOF'
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = %(sshd_log)s
maxretry = 5
bantime  = 3600
EOF
  systemctl restart fail2ban || true
fi

# TE: ------- AppArmor -------
echo "TE: Enabling AppArmor and loading default profiles..."
systemctl enable --now apparmor || true
aa-status || true

# TE: ------- Auditd -------
echo "TE: Enabling auditd for basic auditing..."
systemctl enable --now auditd || true

# TE: ------- Disable unused services -------
echo "TE: Listing enabled services (you should review and disable what you don't need)..."
systemctl list-unit-files --type=service --state=enabled | tee /tmp/enabled-services.txt
echo "TE: To disable a service: sudo systemctl disable --now <service>"

# TE: ------- Disable IPv6 to prevent leaks -------
echo "TE: Disabling IPv6 to reduce leakage risk..."
sysctl_conf="/etc/sysctl.d/99-disable-ipv6.conf"
cat > "$sysctl_conf" <<'EOF'
# TE: Disable IPv6 to avoid IPv6 leaks when using Tor/VPN
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1
EOF
sysctl --system

# TE: ------- Proxychains/Tor basic config -------
echo "TE: Ensuring proxychains uses Tor's SOCKS5 by default."
# TE: backup existing config
if [ -f /etc/proxychains4.conf ]; then
  cp /etc/proxychains4.conf /etc/proxychains4.conf.bak || true
fi

cat > /etc/proxychains4.conf <<'EOF'
# TE: ProxyChains config - dynamic_chain (will try proxies in order)
# TE: Enable proxy_dns if you want DNS queries proxied through SOCKS
dynamic_chain
tcp_read_time_out 15000
tcp_connect_time_out 8000
# TE: proxy_dns will attempt to proxy DNS lookups; enable if you need it
proxy_dns
[ProxyList]
# TE: Tor local socks port
socks5  127.0.0.1 9050
EOF

# TE: Enable & start Tor service if installed
if command -v tor >/dev/null 2>&1; then
  systemctl enable --now tor || true
  echo "TE: Tor started (systemd)."
else
  echo "TE: Tor not found; installed earlier? check apt logs."
fi

# TE: ------- Log hardening notes & file permissions -------
echo "TE: Setting secure permissions for critical files..."
chmod 600 /etc/ssh/sshd_config || true
chmod 600 /etc/proxychains4.conf || true

# TE: ------- Optional: Set immutable bit on critical configs (commented out) -------
# TE: Uncomment to enable but be careful: you'll need to remove the bit to edit files later.
# chattr +i /etc/ssh/sshd_config
# chattr +i /etc/proxychains4.conf

# TE: ------- Clean up & final messages -------
echo "TE: Cleaning cached apt files..."
apt-get autoremove -y
apt-get autoclean -y

echo "TE: Hardening complete. Manual actions still required:"
echo "TE:  - Verify and set a strong password for user: $PENTEST_USER (if you didn't set it)."
echo "TE:  - If you need SSH, add your public key to ~${PENTEST_USER}/.ssh/authorized_keys on the VM."
echo "TE:  - Configure disk encryption (LUKS) and VM-level settings (snapshots, disable shared folders, disable clipboard) via your hypervisor."
echo "TE:  - Review /tmp/enabled-services.txt and disable services you don't need."
echo "TE:  - Test for DNS/IP leaks using safe test websites from the VM."
echo "TE: NOTE: Do not route the entire VM through Tor unless you know the implications and have an isolated snapshot."

echo "TE: Script finished at $(date). Check $LOG for details."
