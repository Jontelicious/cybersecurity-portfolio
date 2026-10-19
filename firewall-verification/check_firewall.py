"""Client-side IPv4 lab probes. Does not change firewall or network settings."""
import argparse
import hashlib
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import socket
import subprocess
import sys
import time

NODES = {
    'client1': ('10.1.10.10', '10.1.10.254'),
    'client2': ('10.1.20.10', '10.1.20.254'),
    'agent-vm': ('10.1.30.10', '10.1.30.254'),
}


def command(argv, timeout):
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return dict(argv=argv, exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
    except subprocess.TimeoutExpired:
        return dict(argv=argv, error='command_timeout')
    except OSError as error:
        return dict(argv=argv, error=f'{type(error).__name__}: {error}')


def tcp_probe(source, destination, port=22, timeout=3):
    started = time.monotonic()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            connection.settimeout(timeout)
            connection.bind((source, 0))
            connection.connect((destination, port))
        observed = 'connected'
        detail = None
    except (socket.timeout, TimeoutError) as error:
        observed, detail = 'timeout', str(error)
    except OSError as error:
        observed, detail = 'socket_error', f'{type(error).__name__}: {error}'
    return dict(source=source, destination=destination, port=port, observed=observed,
                detail=detail, seconds=round(time.monotonic() - started, 3))


def classify_tcp(probe, expected):
    observed = probe['observed']
    if expected == 'allow':
        status = 'PASS' if observed == 'connected' else 'FAIL'
    elif observed == 'connected':
        status = 'FAIL'
    else:
        # A timeout/rejection never proves which firewall caused it.
        status = 'NEEDS_ROUTER_EVIDENCE'
    return {**probe, 'expected': expected, 'status': status}


def dns_ok(result, gateway):
    output = result.get('stdout', '')
    return (result.get('exit_code') == 0 and 'status: NOERROR' in output
            and bool(re.search(r'^example\.com\.\s+\d+\s+IN\s+A\s+[0-9.]+\s*$', output, re.M))
            and f'SERVER: {gateway}#53' in output)


def collect(node):
    source, gateway = NODES[node]
    report = dict(node=node, hostname=socket.gethostname(), source=source, gateway=gateway,
        recorded_at=datetime.now(timezone.utc).isoformat(),
        checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), tests=[],
        scope='IPv4 TCP/22 peer probes, UDP/TCP DNS to router, direct HTTPS. '
              'NAT, DHCP, service persistence and router-drop attribution require separate evidence.')
    addresses = command(['ip', '-j', '-4', 'addr', 'show'], 5)
    routes = command(['ip', '-j', '-4', 'route', 'show', 'default'], 5)
    report['preflight'] = dict(addresses=addresses, default_routes=routes)
    try:
        local = json.loads(addresses['stdout'])
        defaults = json.loads(routes['stdout'])
        source_present = any(address.get('local') == source for interface in local
                             for address in interface.get('addr_info', []))
        gateway_present = any(route.get('gateway') == gateway for route in defaults)
    except (ValueError, KeyError, TypeError):
        source_present = gateway_present = False
    if not source_present or not gateway_present:
        report['setup_error'] = 'Expected source IPv4 address/default gateway not confirmed; probes skipped.'
        return report
    report['tests'].append(dict(name='local SSH positive control', **classify_tcp(tcp_probe(source, source), 'allow')))
    for peer, (destination, _) in NODES.items():
        if peer == node:
            continue
        expected = 'block' if 'agent-vm' in (node, peer) else 'allow'
        report['tests'].append(dict(name=f'{node} to {peer} SSH',
            **classify_tcp(tcp_probe(source, destination), expected)))
    for protocol in ('udp', 'tcp'):
        argv = ['dig', '-r', '-4', '-b', source]
        if protocol == 'tcp':
            argv.append('+tcp')
        else:
            argv.append('+notcp')
            argv.append('+ignore')  # Do not silently retry UDP DNS over TCP.
        argv += ['@' + gateway, 'example.com', 'A', '+time=2', '+tries=1']
        result = command(argv, 5)
        report['tests'].append(dict(name=f'router DNS {protocol}', status='PASS' if dns_ok(result, gateway) else 'FAIL', evidence=result))
    result = command(['curl', '-q', '-4', '--noproxy', '*', '--interface', source,
        '-I', '--silent', '--show-error', '--connect-timeout', '5', '--max-time', '15',
        '--write-out', '\nHTTP_STATUS=%{http_code}\n', 'https://example.com'], 18)
    status = re.search(r'^HTTP_STATUS=(\d{3})$', result.get('stdout', ''), re.M)
    passed = result.get('exit_code') == 0 and status is not None and 200 <= int(status[1]) < 300
    report['tests'].append(dict(name='IPv4 HTTPS without proxy', status='PASS' if passed else 'FAIL', evidence=result))
    return report


def exit_status(report):
    if report.get('setup_error'):
        return 2
    if any(test['status'] == 'FAIL' for test in report['tests']):
        return 1
    if any(test['status'] == 'NEEDS_ROUTER_EVIDENCE' for test in report['tests']):
        return 2
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', required=True, choices=NODES)
    parser.add_argument('--output', type=Path, help='New JSON output file; refuses overwrite')
    args = parser.parse_args()
    # Reserve the report before probing; a path error must not trigger tests.
    stream = args.output.open('x') if args.output else None
    try:
        report = collect(args.node)
        encoded = json.dumps(report, indent=2) + '\n'
        if stream:
            stream.write(encoded)
        print(encoded, end='')
    finally:
        if stream:
            stream.close()
    return exit_status(report)


if __name__ == '__main__':
    sys.exit(main())
