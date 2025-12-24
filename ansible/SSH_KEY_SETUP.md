# SSH Key Authentication Setup

Set up passwordless SSH from your Mac to your Raspberry Pi.

## 1. Check for existing SSH key

```bash
ls ~/.ssh/id_ed25519.pub 2>/dev/null || ls ~/.ssh/id_rsa.pub 2>/dev/null
```

If a file path is printed, skip to step 3.

## 2. Generate SSH key (if needed)

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Press Enter to accept the default location. Optionally set a passphrase.

## 3. Copy key to Raspberry Pi

```bash
ssh-copy-id pi@pi.local
```

Enter your Pi password when prompted. This copies your public key to the Pi.

## 4. Test passwordless login

```bash
ssh pi@pi.local
```

You should connect without being asked for a password.

## 5. Test Ansible connectivity

```bash
cd ansible
./run-playbook.sh -m ping raspberry_pi
```

Expected output:
```
pi | SUCCESS => {
    "ping": "pong"
}
```

## Troubleshooting

### "Permission denied (publickey)"

Ensure the key was copied correctly:
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub pi@pi.local
```

### Still asking for password

Check Pi's SSH config allows key auth:
```bash
ssh pi@pi.local "grep PubkeyAuthentication /etc/ssh/sshd_config"
```

Should show `PubkeyAuthentication yes` (or be commented out, which defaults to yes).

### Wrong key being used

Specify the key explicitly:
```bash
ssh -i ~/.ssh/id_ed25519 pi@pi.local
```

To make this permanent, add to `~/.ssh/config`:
```
Host pi.local
    User pi
    IdentityFile ~/.ssh/id_ed25519
```
