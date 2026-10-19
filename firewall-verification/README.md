# RouterVM firewall policy verification

A repeatable IPv4 verification project for a Debian router with two communicating
lab networks and a separately isolated agent network. The school assignment
explicitly requires LAN1 ↔ LAN2 forwarding. LAN3 isolation is an additional lab
requirement; LAN1/LAN2 communication is intentional, not a firewall defect.

## Verified manually on 2026-10-19

| Area | Observed evidence | Scope |
|---|---|---|
| LAN1 ↔ LAN2 | Fresh TCP/22 connections succeeded in both directions; each directional accept counter increased by one packet | Two IPv4 TCP paths |
| LAN3 ↔ LAN1/LAN2 | Four TCP/22 probes timed out; the two grouped RouterVM drop counters each increased by 6 packets / 360 bytes | Corroborated blocking during the probe interval; grouped counters do not identify each probe individually |
| DNS | UDP and TCP queries to each LAN's router address returned NOERROR and A answers | Router-provided resolution of example.com |
| Internet | Each VM received HTTP/2 200 over IPv4 HTTPS with proxies bypassed | Connectivity and working return traffic for these sessions |
| NAT | Paired LAN-ingress/WAN-egress SYN packets show each source translated to 192.168.122.89 | RouterVM source NAT, before any subsequent Mint/libvirt NAT |
| DHCP | client1/client2 completed DISCOVER/OFFER/REQUEST/ACK; agent-vm had REQUEST/ACK entries | Server-side journal and lease evidence; no forced renewals |
| Services | nftables and dnsmasq both enabled and active | Startup configuration and current state; no new reboot test |

[Detailed evidence and limitations](evidence-2026-10-19.md) ·
[Test matrix](test-matrix.md) · [Checker](check_firewall.py)

## Network

| Node | IPv4 | Default gateway / DNS |
|---|---|---|
| client1 (hostname klient1) | 10.1.10.10/24 | 10.1.10.254 |
| client2 (hostname klient2) | 10.1.20.10/24 | 10.1.20.254 |
| agent-vm | 10.1.30.10/24 | 10.1.30.254 |

Router interfaces: WAN enp1s0=192.168.122.89/24; LAN1 enp7s0; LAN2 enp8s0;
LAN3 enp9s0. WAN gateway is 192.168.122.1. Documented dynamic pools are
.100–.200 on each LAN with 12-hour leases. client1/client2 have reserved .10
addresses with infinite leases; agent-vm has reserved .10 with a 12-hour lease.

## Run the checker

Requires Linux, Python 3, iproute2, dig and curl. These were found on all three
VMs. Run as an ordinary user directly on the selected VM, not inside Hermes's
container or on Mint. From this project directory on Mint, copy the reviewed script using existing SSH:

```bash
scp check_firewall.py bastion@10.1.10.10:check_firewall.py
scp check_firewall.py bastion@10.1.20.10:check_firewall.py
scp check_firewall.py bastion@10.1.30.10:check_firewall.py
```

Then, respectively on each VM:

```bash
python3 -B check_firewall.py --node client1 --output client1-results.json
python3 -B check_firewall.py --node client2 --output client2-results.json
python3 -B check_firewall.py --node agent-vm --output agent-results.json
```

Each command belongs on its matching VM. The script verifies the expected source
address and default gateway before probing, binds TCP/DNS/HTTPS probes to that
source address, checks local SSH, probes the two other clients' TCP/22 ports,
queries the router over UDP/TCP DNS, and makes one HTTPS HEAD request to
example.com. It makes a small, fixed set of connections; it does not scan ports,
authenticate to SSH, change rules, restart services or renew DHCP. Output files
must be new: choose a new name for each repeat. TLS verification remains enabled.

Results use three statuses:

- PASS: an expected allowed connection or application check succeeded.
- FAIL: a required allowed check failed, or a prohibited peer connection succeeded.
- NEEDS_ROUTER_EVIDENCE: a prohibited connection timed out or returned a socket
  error. This is not automatically a confirmed block. A host firewall, route,
  service failure or other cause could explain it.

Exit codes: 0 means all automated checks passed; 1 means at least one FAIL;
2 means a setup problem or manual router evidence is still needed (also used by
argparse for invalid arguments). Expected isolation probes normally produce exit
2. Read the JSON and error text; do not interpret a nonzero exit as automatically
meaning broken isolation. Missing tools fail the relevant checks explicitly.

The script has **not yet been run on the actual lab VMs**. The manual results
above predate the script. Local validation: seven tests, including a real loopback
connection and mocked complete probe results; no external network/model calls.

```bash
python3 -B -m unittest discover -s tests -v
```

## Router-side evidence for each repeat

Before and after the peer probes, save the forward chain on RouterVM:

```bash
sudo nft -a list chain inet filter forward
```

Do not reset counters or reload the firewall between snapshots. Compare the rules
by interface/verdict, not permanently by handle: handles can change after reload.
LAN3 isolation rules group both other LANs. To attribute a particular path more
precisely, snapshot counters around one probe at a time, keeping background
traffic quiet, or use a targeted packet capture. The script cannot automatically
attribute these grouped counter changes or assess conntrack policy exceptions.

For NAT, start this on RouterVM and then run the fixed-address HTTPS request on
one client at a time. The address below is a historical example.com address,
not a promise of future availability; verify/update the target for future runs.

```bash
sudo timeout 60 tcpdump -pni any -nn -c 30 \
  'ip and tcp dst port 443 and (tcp[tcpflags] & (tcp-syn|tcp-ack) = tcp-syn) and dst host 104.20.23.154'
```

```bash
curl -4 --noproxy '*' --resolve example.com:443:104.20.23.154 \
  -I --connect-timeout 5 --max-time 15 https://example.com
```

Capture a LAN-ingress and WAN-egress SYN pair matching destination, sequence and
port. This separate fixed-IP test provides NAT evidence; ordinary successful
HTTPS alone does not locate the translation. The -p capture option avoids the
irrelevant promiscuous-mode warning for the any device. A timeout exit from the
capture can simply indicate that the observation window ended.

## Remaining work and limits

- Review one automated report from each actual VM, alongside new counter evidence.
- RouterVM INPUT policy permits LAN DNS/DHCP and WAN-subnet SSH; those SSH policy
  directions, unsolicited WAN ingress and denial logging have not been tested in
  this verification session.
- The explicit LAN3 drop rules have counters but no log statement. They bypass
  the final forward-chain logging rule. Do not claim every dropped packet is
  logged based on the presence of that final rule.
- AgentVM firewalld permits SSH from Mint's 10.1.30.1 only; RouterVM's .254 source
  is rejected. This is a separate host boundary. It was preserved, not loosened
  to make a positive control pass. RouterVM can reach client1/client2 SSH;
  agent-vm's local SSH listener and Mint SSH access are confirmed.
- IPv6, arbitrary protocols/ports, spoofing, VM/container breakout and established
  sessions surviving policy changes remain outside these tests. RouterVM accepts
  established/related forwarding before the isolation rules.
- No school credentials, VPN data or desktop screenshots are included. Evidence
  is transcribed from user-run terminal output, not an independent remote audit.
