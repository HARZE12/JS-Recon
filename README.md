# JS Recon

HAR-based JavaScript recon automation for bug bounty hunters.

Feed it a HAR file. Get organized output split by bug class — endpoints,
secrets, triage categories, and live API key validation — all in one run.

---

## Install

```bash
git clone https://github.com/HARZE12/JS-Recon.git
cd JS-Recon
bash setup.sh
```

The setup script installs Python dependencies and clones LinkFinder,
SecretFinder, trufflehog, and prettier automatically into a `tools/`
folder. After it finishes it prints the exact command to run.

If you want to install manually instead:

```bash
pip install -r requirements.txt
```

---

## Getting a HAR file

1. Open the target in your browser
2. Open DevTools and go to the Network tab
3. Enable Preserve log
4. Browse the app properly — log in, hit every feature you can reach
5. Right-click any request and hit "Save all as HAR with content"

Flows worth capturing before you export:

- Login and logout
- Account and profile settings
- Billing and payments
- File upload and download
- Webhooks and integrations
- OAuth and SSO flows
- Any admin or internal features you can access

The quality of the output depends on how thoroughly you browsed. A HAR
from a 30-second session produces garbage output.

---

## Usage

```bash
# if you used setup.sh
python js_recon.py target.har \
  --linkfinder tools/LinkFinder/linkfinder.py \
  --secretfinder tools/SecretFinder/SecretFinder.py

# basic (skips LinkFinder and SecretFinder if paths not given)
python js_recon.py target.har

# custom output folder
python js_recon.py target.har --output recon_target

# skip specific steps
python js_recon.py target.har --skip-lf --skip-sf --skip-th
```

---

## What it does

**Extract.** Pulls every JavaScript entry from the HAR by MIME type. A
typical HAR from a modern web app contains 20-80 JS files. All of them
get extracted automatically.

**Beautify.** Minified JS is unreadable. Each file gets run through
jsbeautifier, then prettier on top if you have it installed. The
beautified files are what every other step runs against.

**Endpoints via LinkFinder.** Runs LinkFinder against each JS file
individually and saves output per file under `endpoints/`. Splitting
output by file means you know exactly which JS file an endpoint came
from, which makes it easier to trace back when something looks worth
investigating.

**Secret scanning.** Two tools run back to back. SecretFinder covers
known patterns — AWS keys, JWTs, Stripe keys, Google tokens, and more.
trufflehog adds entropy analysis on top and catches credentials that
do not match any known format but statistically look wrong. They find
different things. Running both is worth the extra few seconds.

**Triage.** Every line of every beautified JS file gets checked against
13 regex pattern sets, one per bug class. The matching lines go into
separate files under `triage/` so you can look at one category at a
time instead of reading entire files. Instead of digging through 40 JS
files, you open `idor.txt` and see only the lines relevant to IDOR
across all of them.

**API key validation.** When the tool finds something shaped like an API
key it tests it live against the real service. Google tokens hit the
OAuth tokeninfo endpoint. Stripe keys hit `/v1/charges`. Slack tokens
hit `auth.test`. Anything that validates gets flagged in the summary
with a warning. Valid exposed API keys are usually critical severity on
bug bounty.

**Summary report.** After the run, `summary.txt` shows hit counts per
triage category and lists any validated keys at the top. Read this first
to know where to focus before opening individual files.

---

## Output

```
recon_<target>/
├── js/                    beautified JS files, one per HAR entry
├── endpoints/             LinkFinder output, one file per JS file
├── secrets/               SecretFinder and trufflehog findings
├── triage/
│   ├── idor.txt
│   ├── ssrf.txt
│   ├── xss.txt
│   ├── sqli.txt
│   ├── rce.txt
│   ├── lfi.txt
│   ├── oauth.txt
│   ├── admin.txt
│   ├── upload.txt
│   ├── webhook.txt
│   ├── redirect.txt
│   ├── debug.txt
│   └── secrets.txt
├── keys/
│   └── results.json       extracted keys with live validation results
└── summary.txt
```

---

## Triage categories

These are leads for manual review, not confirmed vulnerabilities. Expect
noise, especially from heavily-frameworked apps.

| File | Triggers on |
|------|-------------|
| idor.txt | userId, accountId, user_id, /api/resource/id paths |
| ssrf.txt | fetch(variable), XHR with dynamic URL, localhost, 169.254.169.254 |
| xss.txt | innerHTML=, outerHTML=, document.write(), eval(), dangerouslySetInnerHTML |
| sqli.txt | SELECT/INSERT/UPDATE/DELETE string concatenation, WHERE clause + variable |
| rce.txt | exec(), execSync(), child_process, spawn() |
| lfi.txt | ../../ traversal, require('../'), /etc/passwd, /proc/self |
| oauth.txt | client_id, client_secret, access_token, refresh_token, provider URLs |
| admin.txt | /admin/ paths, isAdmin, is_admin, role === 'admin', superuser |
| upload.txt | FormData, multipart/form-data, .files[0] |
| webhook.txt | webhook URLs, hooks.slack.com, discord.com/api/webhooks |
| redirect.txt | window.location=, window.location.href=, redirect_uri, returnUrl |
| debug.txt | console.log with token/key/password, debugger statements, TODO/FIXME |
| secrets.txt | AKIA keys, api_key=, password=, Authorization Bearer, private key blocks |

---

## Where to start reviewing

Open `summary.txt` first. It tells you which categories had hits and how
many. Start with the highest count categories that match your target.

After that, the most useful files are usually:

```
triage/idor.txt         user and account ID references
triage/oauth.txt        OAuth parameters, token handling, redirect URIs
triage/admin.txt        admin routes and client-side role checks
triage/secrets.txt      hardcoded credentials and tokens
endpoints/              per-file endpoint lists, look for undocumented routes
keys/results.json       any valid keys need an immediate report
```

The `debug.txt` category is easy to overlook but worth checking.
Developers who leave `console.log(authToken)` or `debugger` in
production code sometimes left other things in that should not be there.

---

## Optional dependencies

All tools below are optional. If one is not installed that step is
silently skipped. Use the skip flags if you want to be explicit.

| Tool | Install |
|------|---------|
| LinkFinder | `git clone https://github.com/GerbenJavado/LinkFinder` |
| SecretFinder | `git clone https://github.com/m4ll0k/SecretFinder` |
| trufflehog | `pip install trufflehog` |
| prettier | `npm install -g prettier` |

```
--skip-lf       skip LinkFinder
--skip-sf       skip SecretFinder
--skip-th       skip trufflehog
--skip-triage   skip regex triage
--skip-keys     skip API key validation
```

---

## Common issues

**No JS files found.** The HAR does not contain JavaScript responses. Try
again with Preserve log enabled, cache disabled, and more app flows
covered in a logged-in session.

**LinkFinder or SecretFinder not found.** Pass the path with `--linkfinder`
and `--secretfinder`, or clone them to their default locations.

**ModuleNotFoundError: jsbeautifier.** Run `pip install -r requirements.txt`.

**Prettier not found.** Prettier is optional. jsbeautifier runs without it.

---

## Disclaimer

Only use this on targets where you have permission to test. Follow the
scope and rules of the program you are working on. The key validation
step makes live HTTP requests to third-party APIs — check whether the
program allows that before running it.

---

## License

MIT
