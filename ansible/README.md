# Ansible Deployment for cb-discord-bots

Ansible playbooks and roles for deploying the Discord bot infrastructure to a Raspberry Pi.

## Prerequisites

1. **Local machine**: Install Ansible
   ```bash
   pip install ansible
   ```

2. **Raspberry Pi**:
   - Raspberry Pi OS (Debian-based)
   - SSH enabled with key-based authentication
   - User `pi` with sudo privileges

3. **Network**: Pi accessible from your machine

## Quick Start

### 1. Configure everything in root `.env`

All configuration lives in one file — the monorepo root `.env`:

```bash
# Copy the example and fill in your values
cp .env.example .env
```

Then edit `.env`:

```bash
# App secrets
DISCORD_TOKEN=your_bot_token_here
DB_PASSWORD=your_secure_password

# Ansible deployment settings
ANSIBLE_PI_HOST=pi.local    # Your Pi's hostname
ANSIBLE_PI_USER=pi                    # SSH user
ANSIBLE_REPO_URL=https://github.com/you/cb-discord-bots.git
```

### 2. Test connectivity

```bash
cd ansible
./run-playbook.sh -m ping raspberry_pi
```

### 3. Deploy everything

```bash
cd ansible
./run-playbook.sh playbooks/site.yml
```

That's it! One file, one command.

## Wrapper Script

The `run-playbook.sh` script automatically sources your `.env` before running Ansible:

```bash
# Full deployment
./run-playbook.sh playbooks/site.yml

# Code-only deploy (faster)
./run-playbook.sh playbooks/deploy.yml

# Run database migrations
./run-playbook.sh playbooks/db-migrate.yml

# With extra options
./run-playbook.sh playbooks/site.yml -e "upgrade_packages=true"
./run-playbook.sh playbooks/site.yml --check  # Dry run
```

### Alternative: Manual sourcing

If you prefer not to use the wrapper:

```bash
cd ansible
source ../.env
ansible-playbook playbooks/site.yml
```

## Playbooks

| Playbook | Description | Use case |
|----------|-------------|----------|
| `site.yml` | Full deployment | Initial setup, infrastructure changes |
| `deploy.yml` | Code-only deploy | Fast updates after code changes |
| `db-migrate.yml` | Run migrations | Database schema updates |

## Configuration

### All settings in `.env`

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_TOKEN` | Yes | - | Discord bot token |
| `DB_PASSWORD` | Yes | postgres | PostgreSQL password |
| `ANSIBLE_PI_HOST` | No | pi.local | Raspberry Pi hostname or IP |
| `ANSIBLE_PI_USER` | No | pi | SSH username |
| `ANSIBLE_REPO_URL` | Yes | - | Git repository URL |
| `ANSIBLE_REPO_BRANCH` | No | main | Git branch to deploy |

See `.env.example` for the full list.

### Static defaults (rarely need changing)

`inventory/group_vars/raspberry_pi.yml` contains only static infrastructure defaults:
- Application paths (`/opt/cb-discord-bots`)
- PostgreSQL version and tuning
- System packages to install

## Roles

| Role | Description |
|------|-------------|
| `common` | Base system setup, Python, git clone, .env deployment |
| `postgres` | PostgreSQL installation and configuration |
| `belica-bot` | Discord bot systemd service |
| `predecessor-crons` | Cron worker systemd service |

## Managing Services on the Pi

After deployment:

```bash
# View logs
journalctl -u belica-bot -f
journalctl -u predecessor-crons -f

# Restart services
sudo systemctl restart belica-bot
sudo systemctl restart predecessor-crons

# Check status
sudo systemctl status belica-bot
sudo systemctl status predecessor-crons
```

## Troubleshooting

### SSH connection issues
```bash
# Test SSH manually
ssh pi@pi.local

# Check your .env has the right host
grep ANSIBLE_PI_HOST ../.env
```

### Service won't start
```bash
# Check logs on Pi
journalctl -u belica-bot -n 50 --no-pager

# Check .env file on Pi
cat /opt/cb-discord-bots/.env
```

### Database connection issues
```bash
# On the Pi, test PostgreSQL
sudo -u postgres psql -c "\\l"
sudo -u postgres psql -d predecessor -c "\\dt"
```
