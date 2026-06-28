# Configure remote Linux server using Claude Code

You don’t need to give Claude Code (or anyone) your root password; And you don’t need to SSH as root directly to get safe root-level automation.

We login into the server as user "lev" and SSH key.
Then we use `sudo` for privileged operations
and, if needed, configure
**passwordless sudo for that account**, not root SSH.

You want three things simultaneously:
- Claude Code can run privileged commands to configure Nginx/PostgreSQL/etc.
- You do not share or hard‑code the root password with Claude.
- Root login over SSH stays either disabled or tightly controlled.

You do not need an SSH key “for root” or to expose the root password to Claude

The safest approach is:
- keep using `lev` + SSH key,
- give `lev` the right sudo privileges,
- let Claude Code issue `sudo` commands within your session while you approve them

Given you want Claude Code to drive many commands, it’s safer to keep root SSH disabled and let it operate via `lev + sudo`

## Recommended pattern:

1. **Continue SSH as `lev` using your existing key**
2. **Make sure `lev` is in the sudo group**
3. **Decide on sudo password policy**
   - **normal** — you will need to type your password
   - **passwordless sudo** — edit `/etc/sudoers` via `visudo` to add a line like:
     - `lev ALL=(ALL) NOPASSWD: /usr/bin/apt, /usr/sbin/service nginx, /usr/bin/systemctl, /usr/bin/certbot`
       for a **restricted set** of commands; or
     - `lev ALL=(ALL) NOPASSWD:ALL` if you really want full passwordless sudo.

   This way, Claude can run `sudo apt install nginx`, `sudo systemctl restart nginx`, `sudo certbot`, etc. without ever knowing the root password; sudo elevates `lev` to root for those commands.

4. **Keep root SSH disabled or “without-password” only**
   Leave `PermitRootLogin no` (Ubuntu default), or at most `PermitRootLogin without-password` with your own personal key, but don’t use that as Claude’s primary entry point.

5. **Run Claude Code attached to the `lev` session**
   You SSH as `lev`, start Claude Code (or attach your local Claude Code terminal to that directory), and let it propose and run commands. Its permission model already pauses and requests approval before running shell commands or editing files, which is a good safety layer.

[clarista](https://www.clarista.io/blog/claude-code-best-practices)


---

## Concrete `visudo` snippet (Nginx / PostgreSQL / Certbot)

Don't edit the main `/etc/sudoers` directly. Use a **drop-in file** under
`/etc/sudoers.d/` — it survives package upgrades and a syntax error there can't
brick all of sudo. Create/edit it with `visudo` so the file is syntax-checked
before it is saved:

```
sudo visudo -f /etc/sudoers.d/claude-lev
sudo chmod 0440 /etc/sudoers.d/claude-lev   # visudo sets this; confirm it
sudo visudo -c                              # validate the whole sudoers tree
```

First, confirm the real binary paths on THIS box — they vary by distro/install
method (apt vs snap, /usr/bin vs /bin vs /usr/sbin):

```
command -v apt apt-get systemctl certbot nginx tee
# e.g. certbot may be /usr/bin/certbot OR /snap/bin/certbot
```

Then put this in `/etc/sudoers.d/claude-lev` (adjust paths to match the output
above). Absolute paths are required — a bare command name is silently ignored:

```sudoers
# === Passwordless sudo surface for the automation account "lev" ===========
# Scope: package mgmt + our Nginx/PostgreSQL/Certbot service stack only.
# Everything NOT listed here still requires a password (or is impossible),
# which is the point: sensitive actions stay manual.

# Hygiene: fixed PATH so a listed binary can't be shadowed by a planted one.
Defaults:lev secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Defaults:lev !visiblepw

# --- Package management (apt) --------------------------------------------
# NOTE: passwordless apt is effectively root (maintainer scripts run as root).
# That is expected/acceptable for an automation account; it is the main reason
# you still want command review on by default in Claude Code.
Cmnd_Alias APT = /usr/bin/apt, /usr/bin/apt-get, /usr/bin/dpkg --configure -a, \
                 /usr/bin/unattended-upgrade

# --- Nginx: service control + config test/reload -------------------------
Cmnd_Alias SVC_NGINX = /usr/bin/systemctl start nginx,   /usr/bin/systemctl stop nginx, \
                       /usr/bin/systemctl restart nginx, /usr/bin/systemctl reload nginx, \
                       /usr/bin/systemctl enable nginx,  /usr/bin/systemctl disable nginx, \
                       /usr/bin/systemctl --no-pager status nginx
Cmnd_Alias NGINX_CFG = /usr/sbin/nginx -t, /usr/sbin/nginx -s reload

# --- PostgreSQL: service control (top-level + per-instance unit) ----------
Cmnd_Alias SVC_PG = /usr/bin/systemctl start postgresql,   /usr/bin/systemctl stop postgresql, \
                    /usr/bin/systemctl restart postgresql, /usr/bin/systemctl reload postgresql, \
                    /usr/bin/systemctl enable postgresql,  /usr/bin/systemctl disable postgresql, \
                    /usr/bin/systemctl --no-pager status postgresql, \
                    /usr/bin/systemctl restart postgresql@*, /usr/bin/systemctl reload postgresql@*, \
                    /usr/bin/systemctl --no-pager status postgresql@*

# --- TLS certificates (certbot) ------------------------------------------
# TRUST NOTE: certbot --deploy-hook/--pre-hook run arbitrary commands as root.
# That is inherent to certbot; only grant this if you trust it to renew certs.
Cmnd_Alias CERTBOT = /usr/bin/certbot

# --- Read-only inspection ------------------------------------------------
# --no-pager is REQUIRED here: journalctl/systemctl open a pager (less) by
# default, and a pager gives an interactive "!sh" shell escape -> root shell.
Cmnd_Alias INSPECT = /usr/bin/journalctl --no-pager *, \
                     /usr/bin/systemctl --no-pager status *, \
                     /usr/bin/ss *, /usr/bin/lsof *

# Grant the surface, passwordless, running as root:
lev ALL=(root) NOPASSWD: APT, SVC_NGINX, NGINX_CFG, SVC_PG, CERTBOT, INSPECT

# (OPTIONAL) Let Claude write Nginx vhost/config files as root without a shell.
# `tee` is the safe primitive here: it only writes stdin to the named file and
# cannot spawn an editor/shell. sudoers wildcards do NOT match "/", so the path
# is pinned under /etc/nginx and ".." traversal won't match. Uncomment if you
# want config edits automated too (still worth reviewing each diff):
# Cmnd_Alias NGINX_WRITE = /usr/bin/tee /etc/nginx/sites-available/*, \
#                          /usr/bin/tee /etc/nginx/conf.d/*, \
#                          /usr/bin/tee -a /etc/nginx/sites-available/*
# lev ALL=(root) NOPASSWD: NGINX_WRITE
```

After saving, test as `lev`:

```
sudo -l                              # lists exactly the allowed commands
sudo nginx -t                        # should run WITHOUT a password prompt
sudo systemctl reload nginx          # should run WITHOUT a password prompt
sudo cat /etc/sudoers                # should PROMPT or be denied (good)
```

## Safe sudo surface — what Claude may automate vs. what stays manual

ALLOWED (passwordless, in the snippet above):

| Area        | Commands Claude can run                                              |
|-------------|---------------------------------------------------------------------|
| Packages    | `apt` / `apt-get` install/update/upgrade/remove, `dpkg --configure -a` |
| Nginx       | start/stop/restart/reload/enable/disable, `nginx -t`, `nginx -s reload`, status |
| PostgreSQL  | start/stop/restart/reload/enable/disable (incl. `postgresql@*` instance unit), status |
| Certbot     | `certbot` (issue/renew/install certs)                               |
| Inspect     | `journalctl --no-pager`, `systemctl status --no-pager`, `ss`, `lsof` |
| (optional)  | write `/etc/nginx/sites-available/*` & `conf.d/*` via `tee`          |

MANUAL-ONLY (never put in the passwordless surface — require a password, or do
them yourself over your own SSH session):

- **`sshd_config`** — editing `/etc/ssh/sshd_config` and restarting `ssh`/`sshd`
  (a bad edit can lock you out of the box).
- **sudoers itself** — `visudo`, any write to `/etc/sudoers` or `/etc/sudoers.d/*`
  (this is what bounds everything else; it must not be self-modifiable).
- **User/identity** — `useradd`/`usermod`/`userdel`, `passwd`, `chpasswd`,
  group changes, `su`, `sudo -i`, `sudo bash/sh` (interactive root shells).
- **Firewall / network** — `ufw`, `iptables`/`nftables`, routing (easy to lock
  yourself out remotely).
- **Disk / filesystem** — `dd`, `mkfs`, `fdisk`/`parted`, `mount`, fstab edits.
- **Generic file-write-as-root** — `tee`/`cp`/`mv`/`sed -i`/editors targeting
  paths OUTSIDE `/etc/nginx` (these are root-equivalent: they can overwrite
  sudoers, sshd_config, PAM, etc.). Only the pinned `/etc/nginx/...` tee rule
  above is allowed, and only if you opt in.

Rule of thumb: anything that can (a) grant privileges, (b) change who can log
in, or (c) write an arbitrary root-owned file is **manual**. Service lifecycle,
package installs, cert renewals, and read-only inspection are **automatable**.
