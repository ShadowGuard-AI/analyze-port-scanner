#!/usr/bin/env python3
"""analyze-port-scanner: I scan a host's TCP ports, and I read scan
results other tools already produced, so a pile of port output turns
into a short list of what is actually open and worth a second look.

Two jobs, one file:
  scan     probe a host myself with plain TCP connects
  analyze  parse an existing scan output file (nmap normal, nmap
           grepable, or plain host:port lines) and summarize it

Standard library only. I do not hide behind dependencies for socket
work the stdlib already does well.
"""

import argparse
import concurrent.futures
import json
import re
import socket
import sys
from pathlib import Path

# Ports I always call out by name in a summary. These are the ones
# that change the conversation when they are open to the world:
# remote shells, file sharing, databases, and plaintext legacy
# protocols that should not be exposed anymore.
NOTABLE = {
    21: "FTP, plaintext file transfer",
    23: "Telnet, plaintext remote shell",
    445: "SMB, Windows file sharing",
    1433: "Microsoft SQL Server",
    3306: "MySQL or MariaDB",
    3389: "RDP, Windows remote desktop",
    5432: "PostgreSQL",
    5900: "VNC remote desktop",
    6379: "Redis, often unauthenticated",
    9200: "Elasticsearch HTTP API",
    27017: "MongoDB",
}

DEFAULT_PORTS = "21,22,23,25,53,80,110,143,443,445,993,995,1723,3306," \
                "3389,5432,5900,6379,8000,8080,8443,9200,27017"


def service_name(port):
    """Best-effort service name from the system table, else 'unknown'."""
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"


def parse_ports(spec, port_range):
    """Turn --ports and --port-range into one sorted list of ints."""
    ports = set()
    if spec:
        for chunk in spec.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            if "-" in chunk:
                lo, _, hi = chunk.partition("-")
                ports.update(range(int(lo), int(hi) + 1))
            else:
                ports.add(int(chunk))
    if port_range:
        lo, _, hi = port_range.partition("-")
        ports.update(range(int(lo), int(hi) + 1))
    bad = [p for p in ports if not 1 <= p <= 65535]
    if bad:
        raise ValueError(f"ports out of range 1-65535: {sorted(bad)}")
    return sorted(ports)


def probe(host, port, timeout):
    """One TCP connect. Open means the handshake completed."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return port
    except OSError:
        return None


def run_scan(args):
    try:
        ports = parse_ports(args.ports, args.port_range)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not ports:
        print("error: no ports selected to probe", file=sys.stderr)
        return 2
    # Resolve once up front so a bad hostname fails loudly instead of
    # looking like a host with every port closed.
    try:
        target = socket.gethostbyname(args.host)
    except OSError as exc:
        print(f"error: cannot resolve {args.host}: {exc}", file=sys.stderr)
        return 2
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=64) as pool:
        results = pool.map(lambda p: probe(target, p, args.timeout), ports)
        for port in results:
            if port is not None:
                open_ports.append(port)
    rows = [{"host": args.host, "address": target, "port": p,
             "service": service_name(p)} for p in sorted(open_ports)]
    report = {"mode": "scan", "host": args.host, "address": target,
              "probed": len(ports), "open": rows}
    emit(report, args)
    return 0


# --- analyze: parsers for output other scanners already produced ---

NMAP_NORMAL = re.compile(r"^(\d+)/tcp\s+(open|closed|filtered)\b\s*(\S*)")
NMAP_HOST = re.compile(r"^Nmap scan report for\s+(\S+)")
GREPABLE_PORTS = re.compile(r"Ports:\s*(.+)$")
PLAIN_LINE = re.compile(
    r"^(?P<host>[\w.\-]+)[:\s,]+(?P<port>\d{1,5})[/\s,]*(?:tcp|udp)?"
    r"[/\s,]*(?P<state>open|closed|filtered)?", re.I)


def parse_scan_text(text):
    """Parse scan output into {host: {port: (state, service)}}.

    I wrote this against real nmap normal and grepable output plus
    the plain one-port-per-line files quick scripts tend to leave
    behind. Lines I cannot understand are counted, never guessed at.
    """
    hosts = {}
    skipped = 0
    current = "unknown"
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = NMAP_HOST.match(line)
        if m:
            current = m.group(1).strip("()")
            hosts.setdefault(current, {})
            continue
        m = GREPABLE_PORTS.search(line)
        if m and "/" in m.group(1):
            host_match = re.match(r"Host:\s*(\S+)", line)
            host = host_match.group(1) if host_match else current
            hosts.setdefault(host, {})
            for entry in m.group(1).split(","):
                fields = entry.strip().split("/")
                if len(fields) >= 3 and fields[0].isdigit():
                    port = int(fields[0])
                    service = fields[4] if len(fields) > 4 else ""
                    hosts[host][port] = (fields[1], service or service_name(port))
            continue
        m = NMAP_NORMAL.match(line)
        if m:
            port = int(m.group(1))
            hosts.setdefault(current, {})[port] = (
                m.group(2), m.group(3) or service_name(port))
            continue
        m = PLAIN_LINE.match(line)
        if m and 1 <= int(m.group("port")) <= 65535:
            host = m.group("host")
            state = (m.group("state") or "open").lower()
            hosts.setdefault(host, {})[int(m.group("port"))] = (
                state, service_name(int(m.group("port"))))
            continue
        skipped += 1
    return hosts, skipped


def run_analyze(args):
    path = Path(args.file)
    if not path.is_file():
        print(f"error: no such file: {path}", file=sys.stderr)
        return 2
    hosts, skipped = parse_scan_text(path.read_text(errors="replace"))
    total_rows = sum(len(v) for v in hosts.values())
    if total_rows == 0:
        # A file with nothing parseable is a run that processed
        # nothing, and I report that as a failure, not a clean scan.
        print(f"error: no scan results parsed from {path} "
              f"({skipped} lines not understood)", file=sys.stderr)
        return 2
    hosts_out = {}
    open_total = 0
    for host in sorted(hosts):
        rows = []
        for port in sorted(hosts[host]):
            state, service = hosts[host][port]
            if state == "open":
                open_total += 1
            rows.append({"port": port, "state": state,
                         "service": service,
                         "note": NOTABLE.get(port, "")})
        hosts_out[host] = rows
    report = {"mode": "analyze", "file": str(path), "hosts": hosts_out,
              "ports_seen": total_rows, "open_total": open_total,
              "lines_skipped": skipped}
    emit(report, args, input_path=path)
    return 0


def render_text(report):
    lines = []
    if report["mode"] == "scan":
        lines.append(f"Scanned {report['host']} ({report['address']}): "
                     f"{report['probed']} ports probed, "
                     f"{len(report['open'])} open")
        for row in report["open"]:
            note = NOTABLE.get(row["port"], "")
            suffix = f"  <- {note}" if note else ""
            lines.append(f"  {row['port']}/tcp open {row['service']}{suffix}")
        if not report["open"]:
            lines.append("  nothing open in the probed set")
    else:
        lines.append(f"Analyzed {report['file']}: "
                     f"{report['ports_seen']} port rows across "
                     f"{len(report['hosts'])} hosts, "
                     f"{report['open_total']} open")
        for host, rows in report["hosts"].items():
            lines.append(f"{host}:")
            for row in rows:
                suffix = f"  <- {row['note']}" if row["note"] else ""
                lines.append(f"  {row['port']}/tcp {row['state']} "
                             f"{row['service']}{suffix}")
        if report["lines_skipped"]:
            lines.append(f"({report['lines_skipped']} lines not understood "
                         f"and skipped)")
    return "\n".join(lines) + "\n"


def emit(report, args, input_path=None):
    text = json.dumps(report, indent=2) + "\n" if args.json \
        else render_text(report)
    if args.output:
        out = Path(args.output)
        if input_path is not None and \
                out.resolve() == input_path.resolve():
            # I will not let an analysis quietly overwrite the scan
            # file it was read from.
            print("error: --output resolves to the input file; "
                  "refusing to overwrite it", file=sys.stderr)
            raise SystemExit(2)
        out.write_text(text)
    else:
        sys.stdout.write(text)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="analyze-port-scanner",
        description="Scan a host's TCP ports, or analyze scan results "
                    "another tool already produced.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="probe a host with TCP connects")
    p_scan.add_argument("host", help="hostname or IP address to scan")
    p_scan.add_argument("--ports", default=DEFAULT_PORTS,
                        help="comma list or ranges, e.g. 22,80,8000-8100 "
                             "(default: a common-services set)")
    p_scan.add_argument("--port-range", default="",
                        help="additional range like 1-1024")
    p_scan.add_argument("--timeout", type=float, default=0.6,
                        help="seconds per connect attempt (default 0.6)")
    p_scan.add_argument("--json", action="store_true",
                        help="emit JSON instead of text")
    p_scan.add_argument("--output", help="write the report to this file")
    p_scan.set_defaults(func=run_scan)

    p_an = sub.add_parser("analyze", help="summarize an existing scan file")
    p_an.add_argument("file", help="scan output file to parse")
    p_an.add_argument("--json", action="store_true",
                      help="emit JSON instead of text")
    p_an.add_argument("--output", help="write the report to this file")
    p_an.set_defaults(func=run_analyze)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
