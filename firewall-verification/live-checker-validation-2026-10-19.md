# Live checker validation — 2026-10-19

Transcribed from user-run JSON reports and RouterVM counter snapshots supplied
for review. This summary is not a copy of the raw JSON or an independent remote
audit. Original reports remain on the corresponding VMs.

Checker SHA256: `7a2cf63283ab1786a21b9dbb6fc02e88133dd8886e7a08ccb24f10b565083824`.
Seven checker tests passed on Mint. The checker code was unchanged for this run.

| Node | Report timestamp (UTC) | PASS | NEEDS_ROUTER_EVIDENCE | FAIL |
|---|---|---:|---:|---:|
| client1 / klient1 | 06:50:20.138147 | 5 | 1 | 0 |
| client2 / klient2 | 06:50:28.383711 | 5 | 1 | 0 |
| agent-vm | 06:50:43.196089 | 4 | 2 | 0 |
| Total | | 14 | 4 | 0 |

All three reports passed source-address/default-gateway preflight. Each local
SSH positive control, UDP DNS query, TCP DNS query and direct IPv4 HTTPS request
passed; HTTPS returned HTTP/2 200. client1 and client2 connected to each other's
SSH port. Each of the four prohibited paths involving agent-vm timed out after
3.003 seconds and correctly remained NEEDS_ROUTER_EVIDENCE in the raw report.
No overall process exit codes were supplied; exit 2 is expected for these reports.

## Router evidence during the checker run

| Forward rule | Before packets / bytes | After packets / bytes | Increase |
|---|---:|---:|---:|
| LAN3 → LAN1/LAN2 drop | 6 / 360 | 12 / 720 | 6 / 360 |
| LAN1/LAN2 → LAN3 drop | 6 / 360 | 12 / 720 | 6 / 360 |
| LAN1 → LAN2 accept | 1 / 60 | 2 / 120 | 1 / 60 |
| LAN2 → LAN1 accept | 1 / 60 | 2 / 120 | 1 / 60 |
| LAN1 → WAN accept | 9 / 652 | 10 / 712 | 1 / 60 |
| LAN2 → WAN accept | 9 / 652 | 10 / 712 | 1 / 60 |
| LAN3 → WAN accept | 724 / 48048 | 725 / 48108 | 1 / 60 |

The new snapshots corroborate router dropping during the isolation-probe
interval and permitted fresh connections in both LAN1/LAN2 directions. Drop
counters group two paths each; they count packets, including retransmissions,
not independent test cases. They do not uniquely attribute every packet to a
particular probe. Reports are preserved as NEEDS_ROUTER_EVIDENCE rather than
rewritten as automated passes.

## Conclusion and remaining scope

The observed IPv4 TCP/22 policy matches the assignment and additional LAN3
boundary: LAN1 ↔ LAN2 remains allowed, with blocking corroborated in both
directions between LAN3 and the lab LANs. DNS and HTTPS remain functional.
Earlier manual NAT, DHCP and enabled/active service evidence is documented
[separately](evidence-2026-10-19.md); this replay does not renew that evidence.

No firewall or service settings were changed. Explicit LAN3 drops still bypass
the terminal logging rule; denial logging coverage, router SSH policy tests,
broader protocols and a new reboot persistence test remain outside this run.
