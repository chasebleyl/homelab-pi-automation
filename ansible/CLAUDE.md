# Ansible Setup

Deploys cb-discord-bots to Raspberry Pi. Target host: `pi@pi-postgres.local`.

## Quick Reference

```bash
# Full deployment (infra + app)
./run-playbook.sh playbooks/site.yml

# Code-only deployment (faster)
./run-playbook.sh playbooks/deploy.yml

# Database migrations only
./run-playbook.sh playbooks/db-migrate.yml

# Selective deployment with tags
./run-playbook.sh playbooks/site.yml --tags postgres
./run-playbook.sh playbooks/site.yml --tags bot,crons

# Ad-hoc commands
./run-playbook.sh -m ping raspberry_pi
./run-playbook.sh -m shell -a "systemctl status belica-bot" raspberry_pi
```

## Structure

```
ansible/
├── ansible.cfg              # Config: inventory path, SSH pipelining, become settings
├── run-playbook.sh          # Wrapper: activates venv, sources .env, runs ansible
├── requirements.yml         # Dependencies: community.general collection
├── inventory/
│   ├── hosts.yml            # Target host (reads ANSIBLE_PI_HOST from env)
│   └── group_vars/
│       └── raspberry_pi.yml # Static defaults (paths, packages, postgres tuning)
├── playbooks/
│   ├── site.yml             # Full deployment: common → postgres → belica-bot → crons
│   ├── deploy.yml           # Code-only: git pull, pip install, restart services
│   └── db-migrate.yml       # Run alembic migrations only
└── roles/
    ├── common/              # Base setup: apt, git clone, venv, .env deployment
    ├── postgres/            # PostgreSQL: install, config, db/user creation, migrations
    ├── belica-bot/          # Discord bot systemd service
    └── predecessor-crons/   # Cron worker systemd service
```

## Variable Flow

```
Root .env file
     │
     ▼ (load-env.yml reads & parses)
Ansible variables (discord_token, postgres_password, etc.)
     │
     ▼ (templates use variables)
Deployed files (.env on Pi, systemd units, postgres config)
```

**Source:** All secrets come from root `.env` file. Parsed by `roles/common/tasks/load-env.yml`.

**Static defaults** in `inventory/group_vars/raspberry_pi.yml`:
- `app_dir`: `/opt/cb-discord-bots`
- `venv_dir`: `/opt/cb-discord-bots/.venv`
- `postgres_version`: `15`
- `system_packages`: git, python3, python3-pip, python3-venv, etc.
- Postgres tuning: `shared_buffers=128MB`, `work_mem=4MB` (optimized for Pi)

## Roles

### common
Base system setup. Runs first on every deployment.
- Updates apt cache, installs `system_packages`
- Configures fail2ban for SSH protection
- Clones/updates repo to `app_dir`
- Creates venv, installs pip dependencies
- Deploys `.env` from template

**Tags:** `common`, `always`

**Templates:**
- `jail.local.j2` → `/etc/fail2ban/jail.local` (SSH brute-force protection)

### postgres
PostgreSQL installation and configuration.
- Installs PostgreSQL 15 + contrib
- Deploys `postgresql.conf.j2` (memory tuning) and `pg_hba.conf.j2` (auth)
- Creates database (`hobbydata`) and sets user password
- Runs alembic migrations

**Tags:** `postgres`, `database`, `db`

**Templates:**
- `postgresql.conf.j2` → `/etc/postgresql/15/main/conf.d/99-raspberry-pi.conf`
- `pg_hba.conf.j2` → `/etc/postgresql/15/main/pg_hba.conf`

### belica-bot
Discord bot as systemd service.
- Deploys `belica-bot.service` unit file
- Enables and starts service
- Waits for HTTP port (8080) readiness

**Tags:** `belica-bot`, `bot`, `app`

**Service config:** `MemoryMax=256M`, `CPUQuota=50%`, restarts on failure

### predecessor-crons
Cron workers as systemd service.
- Deploys `predecessor-crons.service` unit file
- Enables and starts service

**Tags:** `predecessor-crons`, `crons`, `app`

**Service config:** `MemoryMax=128M`, `CPUQuota=25%`, restarts on failure

## Adding New Features

### Adding a system package
Edit `inventory/group_vars/raspberry_pi.yml`:
```yaml
system_packages:
  - git
  - python3
  # ... existing
  - new-package
```

### Adding a new role
1. Create `roles/<name>/tasks/main.yml`
2. Create `roles/<name>/handlers/main.yml` (if needed)
3. Create `roles/<name>/templates/` (if needed)
4. Add role to `playbooks/site.yml`:
```yaml
roles:
  # ... existing roles
  - role: <name>
    tags: [<name>, <category>]
```

### Adding a new variable from .env
1. Add to root `.env.example`
2. Parse in `roles/common/tasks/load-env.yml`:
```yaml
- name: Set application variables from .env
  set_fact:
    my_new_var: "{{ env_vars.MY_NEW_VAR | default('default_value') }}"
```
3. Use in templates: `{{ my_new_var }}`

## Handlers

Handlers are triggered by `notify` and run at end of play (or on `meta: flush_handlers`).

| Role | Handler | Triggered By |
|------|---------|--------------|
| common | `Restart fail2ban` | jail.local changes |
| postgres | `Restart PostgreSQL` | Config changes |
| belica-bot | `Restart belica-bot` | Service file changes |
| predecessor-crons | `Restart predecessor-crons` | Service file changes |

## Useful Commands (on Pi)

```bash
# View logs
journalctl -u belica-bot -f
journalctl -u predecessor-crons -f
journalctl -u postgresql -f

# Restart services
sudo systemctl restart belica-bot
sudo systemctl restart predecessor-crons

# Check status
sudo systemctl status belica-bot predecessor-crons postgresql

# fail2ban commands
sudo fail2ban-client status              # List active jails
sudo fail2ban-client status sshd         # Show SSH jail details (bans, failures)
sudo fail2ban-client set sshd unbanip IP # Unban an IP address
sudo fail2ban-client reload              # Reload configuration
```
