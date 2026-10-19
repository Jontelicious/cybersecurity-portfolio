# LAN3 denial logging change and retest — 2026-10-19

Evidence transcribed from user-run terminal output. Times below are RouterVM
local time, CEST (UTC+02:00). Raw checker reports remain on their respective VMs;
MAC addresses and unrelated terminal context are omitted from this summary.

## Change

Separate logging rules were added immediately before the existing unconditional
LAN3 isolation drops in `/etc/nftables.conf`, then loaded with
`systemctl reload nftables`. The resulting active chain was supplied for review.
LAN1 ↔ LAN2 accept rules, WAN forwarding and the established/related rule stayed
in place. The checker itself was unchanged.

```nft
iifname $AGENT_IF oifname { $LAN1_IF, $LAN2_IF } limit rate 5/second burst 5 packets log prefix "NFT AGENT TO LAB: "
iifname $AGENT_IF oifname { $LAN1_IF, $LAN2_IF } counter drop

iifname { $LAN1_IF, $LAN2_IF } oifname $AGENT_IF limit rate 5/second burst 5 packets log prefix "NFT LAB TO AGENT: "
iifname { $LAN1_IF, $LAN2_IF } oifname $AGENT_IF counter drop
```

This is an excerpt for the existing forward chain and existing variable
definitions, not a standalone replacement ruleset. Each logging rule has its own
limit; every packet reaching the following matching drop rule is still dropped.
Reloading reset the rule counters; earlier counter totals must not be carried
across this boundary.

## Checker replay

Checker SHA256: `7a2cf63283ab1786a21b9dbb6fc02e88133dd8886e7a08ccb24f10b565083824`.

| Node | Report timestamp UTC | Output file on VM | PASS | NEEDS_ROUTER_EVIDENCE | FAIL |
|---|---|---|---:|---:|---:|
| client1 / klient1 | 07:05:14.939787 | ~/client1-logging-results.json | 5 | 1 | 0 |
| client2 / klient2 | 07:05:22.657373 | ~/client2-logging-results.json | 5 | 1 | 0 |
| agent-vm | 07:05:32.174412 | ~/agent-logging-results.json | 4 | 2 | 0 |

All source/default-gateway preflights succeeded. Local SSH controls, LAN1 ↔ LAN2
SSH, UDP/TCP DNS and IPv4 HTTPS passed. All three HTTPS requests returned HTTP/2
200. The four prohibited connections timed out after 3.003 seconds each. Their
raw statuses remain NEEDS_ROUTER_EVIDENCE; the following evidence supports the
reviewer's router-blocking conclusion without rewriting those reports.

## Path-specific kernel journal evidence

All listed entries were TCP SYN packets with destination port 22 and length 60.

| Source | Destination | IN → OUT | Prefix | Local timestamps | Source port |
|---|---|---|---|---|---:|
| 10.1.10.10 | 10.1.30.10 | enp7s0 → enp9s0 | NFT LAB TO AGENT | 09:05:14, :15, :16 | 52437 |
| 10.1.20.10 | 10.1.30.10 | enp8s0 → enp9s0 | NFT LAB TO AGENT | 09:05:22, :23, :24 | 39655 |
| 10.1.30.10 | 10.1.10.10 | enp9s0 → enp7s0 | NFT AGENT TO LAB | 09:05:32, :33, :34 | 34831 |
| 10.1.30.10 | 10.1.20.10 | enp9s0 → enp8s0 | NFT AGENT TO LAB | 09:05:35, :36, :37 | 48849 |

Logs were retrieved with `journalctl -k` and the two prefixes. The twelve entries
identify every tested prohibited source/destination pair, with one initial SYN
and two retransmissions per connection attempt. Together with the adjacent drop
rules and counters, this provides stronger attribution than timeout alone.

## Counter cross-check

The initial post-reload snapshot showed zero for both isolation drops and both
LAN1/LAN2 directional accepts. The supplied retest snapshot showed:

| Rule | Packets | Bytes |
|---|---:|---:|
| LAN3 → LAN1/LAN2 drop | 6 | 360 |
| LAN1/LAN2 → LAN3 drop | 6 | 360 |
| LAN1 → LAN2 accept | 1 | 60 |
| LAN2 → LAN1 accept | 1 | 60 |

These totals match the logged isolation packets and successful fresh LAN1/LAN2
connections. The grouped counters alone still do not identify individual paths;
the journal now supplies that detail.

## Result and limits

LAN3 denial logging is verified for all four tested IPv4 TCP/22 paths, while
assignment-required LAN1 ↔ LAN2 access and DNS/HTTPS remain functional. This
closes the previously documented missing LAN3 logging coverage for these probes.

The rate-limit configuration is loaded, but sustained traffic exceeding the
limit was not tested. This does not establish that every denied packet will be
logged. Other INPUT/FORWARD denial paths, IPv6, arbitrary ports/protocols and a
new reboot persistence test remain unverified. Earlier NAT/DHCP evidence is
separate. No host firewalld relaxation was needed.
