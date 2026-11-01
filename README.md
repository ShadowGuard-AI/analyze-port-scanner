![Banner](banner.png)

# analyze-port-scanner

I wrote this tool to do two related jobs: scan a host's TCP ports
myself, and analyze scan results another tool already produced. Either
way, what comes out is a short, readable list of what is open and what
deserves a second look, instead of a wall of raw scanner output.

## What it does

- `scan` probes a host with plain TCP connect attempts and reports
  the ports that complete a handshake, with service names.
- `analyze` reads an existing scan output file and summarizes it per
  host. I parse nmap normal output, nmap grepable output, and plain
  `host:port` lines. Lines I cannot understand are counted and
  reported as skipped, never guessed at.
- Both modes flag the ports I always want called out by name:
  Telnet, FTP, SMB, RDP, VNC, and exposed database ports such as
  MySQL, PostgreSQL, Redis, and MongoDB.
- Both modes can emit JSON with `--json` and write to a file with
  `--output`.

## Install

```bash
git clone https://github.com/ShadowGuard-AI/analyze-port-scanner.git
cd analyze-port-scanner
```

Python 3, standard library only. There is nothing to install.

## Usage

Scan a host (a common-services port set is the default):

```bash
python3 main.py scan 127.0.0.1 --ports 22,80,443
```

```
Scanned 127.0.0.1 (127.0.0.1): 3 ports probed, 0 open
  nothing open in the probed set
```

Analyze a scan file someone hands me:

```bash
python3 main.py analyze scan-results.txt
```

```
Analyzed scan-results.txt: 6 port rows across 3 hosts, 5 open
192.0.2.10:
  22/tcp open ssh
  23/tcp open telnet  <- Telnet, plaintext remote shell
  80/tcp closed http
192.0.2.20:
  443/tcp open https
  3306/tcp open mysql  <- MySQL or MariaDB
192.0.2.30:
  6379/tcp open redis  <- Redis, often unauthenticated
(1 lines not understood and skipped)
```

## Parameters

`scan`:

- `host`: hostname or IP address to scan.
- `--ports`: comma list of ports and ranges, for example
  `22,80,8000-8100`. Default is a common-services set.
- `--port-range`: one more range to add, for example `1-1024`.
- `--timeout`: seconds per connect attempt. Default 0.6.
- `--json`: emit JSON instead of text.
- `--output`: write the report to this file instead of stdout.

`analyze`:

- `file`: the scan output file to parse.
- `--json`: emit JSON instead of text.
- `--output`: write the report to this file instead of stdout.
  If the output path resolves to the input file, I refuse and exit
  non-zero rather than overwrite the scan I was handed.

Run `python3 main.py --help` or `python3 main.py scan --help` for the
full text.

## Exit codes

- `0`: the run did its work. A scan that probed its ports and found
  nothing open says so and still exits 0, because the probing
  happened.
- `2`: the run processed nothing or was refused: an unresolvable
  host, no ports selected, a missing input file, a scan file with no
  parseable results, or an `--output` that points at the input file.

## License

MIT. See [LICENSE](LICENSE).
Copyright (c) Gavin K (@Epsilon0xCell).
