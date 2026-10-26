# RouterVM verification checklist

The **original two-LAN assignment required LAN1 ↔ LAN2 communication**. An earlier configuration blocked that traffic, which was a deviation from the requirement. The later three-LAN policy allows LAN1 ↔ LAN2 and adds LAN3 isolation. This checklist separates the dated evidence below; historical results are not proof of a later ruleset.

## Historical three-LAN ICMP observations — 2026-10-16

| Source | Destination | Expected | Verification |
| --- | --- | --- | --- |
| AgentVM / LAN3 | RouterVM gateway on LAN3 | Allowed | Observed 3/3 ICMP replies |
| AgentVM / LAN3 | External IPv4 test endpoint | Allowed through forwarding/NAT | Observed 3/3 ICMP replies |
| AgentVM / LAN3 | Client1 / LAN1 | Denied | 0/3 ICMP replies; matching nftables counter +3 |
| AgentVM / LAN3 | Client2 / LAN2 | Denied | Previously tested 0/3; matching LAN3 drop counter increase |
| Client1 / LAN1 | AgentVM / LAN3 | Denied | Previously tested 0/3; reverse drop counter +3 |
| Client2 / LAN2 | AgentVM / LAN3 | Denied | Not separately tested |
| Client1 / LAN1 | Client2 / LAN2 | **Allowed under active rule configuration** | No fresh positive connectivity test documented |
| Client2 / LAN2 | Client1 / LAN1 | **Allowed under active rule configuration** | No fresh positive connectivity test documented |
| LAN1, LAN2, LAN3 | WAN | Allowed via configured policy | AgentVM tested; current client1/client2 WAN tests not repeated |
| LAN clients | RouterVM DHCP/DNS | Allowed where configured | Historical LAN1/LAN2 checks; review LAN3 independently |

Source of test observations: [LAN3 connectivity and counter results](agentvm-connectivity-test-2026-10-16.md). The [active nftables snapshot](configs/active-nftables-snapshot-2026-10-16.md) documents the reviewed policy; rule presence alone does not establish real-world reachability.

## Later three-LAN verification — 2026-10-19

The [firewall policy verification project](../firewall-verification/README.md) records later IPv4 checks. These supplement the ICMP history above; they do not retroactively establish that an untested ICMP path was tested.

| Area | Documented result | Evidence scope |
| --- | --- | --- |
| LAN1 ↔ LAN2 | Fresh TCP/22 connections succeeded in both directions; each directional accept counter increased by one packet | Two IPv4 TCP paths |
| LAN3 ↔ LAN1/LAN2 | All four TCP/22 probes timed out; each grouped isolation drop counter increased by 6 packets / 360 bytes | Router blocking corroborated during the probe interval; grouped counters do not attribute each probe individually |
| DNS | UDP and TCP queries to each VM's router gateway returned NOERROR with A answers | Router-provided resolution for the tested name |
| WAN connectivity and NAT | Each VM received HTTP/2 200 over IPv4 HTTPS; separate paired ingress/egress SYN captures showed RouterVM source NAT | Selected sessions and translation at RouterVM, before upstream libvirt NAT |
| DHCP and services | Client1/Client2 DISCOVER/OFFER/REQUEST/ACK; AgentVM REQUEST/ACK; nftables and dnsmasq enabled and active | Server-side evidence; no forced renewals or new reboot test |

See [manual evidence](../firewall-verification/evidence-2026-10-19.md), [live checker validation](../firewall-verification/live-checker-validation-2026-10-19.md), and the [test matrix](../firewall-verification/test-matrix.md). The later [logging retest](../firewall-verification/logging-validation-2026-10-19.md) recorded path-specific kernel journal entries for all four prohibited TCP/22 paths, alongside matching drop counters. The raw checker statuses remain NEEDS_ROUTER_EVIDENCE rather than automated passes.

These are point-in-time results for selected IPv4 paths. Arbitrary TCP/UDP ports, IPv6, stateful edge cases and full reboot persistence remain unverified.

## Assignment requirement and historical configuration deviation

The school assignment **required LAN1 ↔ LAN2 forwarding to be allowed**. The earlier two-LAN configuration instead blocked it while allowing each LAN to reach WAN. Its checks and drop logs document observed behavior, but that blocking did **not** satisfy the assignment. The later three-LAN policy preserves the required LAN1/LAN2 communication and adds LAN3 isolation.

The [two-LAN nftables teaching example](configs/nftables-example.md) reproduces the historical blocking configuration; it is not an assignment-compliant template or a copy of the live ruleset.

## Read-only router checks

```bash
ip -br addr
ip route
cat /proc/sys/net/ipv4/ip_forward
sudo nft -a list chain inet filter forward
sudo nft list ruleset
sudo dnsmasq --test
systemctl is-active dnsmasq
systemctl is-enabled nftables
```

To test reachability, use controlled ICMP or other authorized traffic from the relevant VM, compare counters before/after, and verify the destination is running. **Ping timeout alone does not prove firewall enforcement.**

## Evidence record template

| Date | Source | Destination | Expected | Observed | Rule counter delta | Screenshot |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-10-16 | AgentVM | Client1 | Deny | 0/3 ICMP replies | LAN3 drop +3 (252 bytes) | [Ping](evidence/lan3-to-lan1-denied.png), [counter](evidence/nftables-drop-counter.png) |
| 2026-10-16 | AgentVM | RouterVM gateway | Allow | 3/3 ICMP replies | Not isolated | [Allowed paths](evidence/lan3-allowed-connectivity.png) |
| 2026-10-16 | AgentVM | External IPv4 | Allow | 3/3 ICMP replies | Not separately attributed | [Allowed paths](evidence/lan3-allowed-connectivity.png) |

## Completed follow-up and remaining checks

- [x] Fresh LAN1 ↔ LAN2 IPv4 TCP/22 connections succeeded in both directions on 2026-10-19, with directional accept-counter increases
- [x] Fresh Client2 → AgentVM IPv4 TCP/22 denial probe recorded on 2026-10-19, with corroborating router counters and path-specific journal evidence in the logging retest
- [ ] Broader TCP/UDP and stateful traffic checks where needed
- [ ] Full startup/persistence validation for DHCP, DNS, nftables and guest routing
- [ ] Review all images and tracked configuration text before public release

## Publication hygiene

Keep school networking details, keys, credentials, actual personal-device MACs, and unredacted logs out of the repository. The example RFC1918 addresses shown here belong to an isolated virtual lab; decide whether to preserve or generalize them before public release.
