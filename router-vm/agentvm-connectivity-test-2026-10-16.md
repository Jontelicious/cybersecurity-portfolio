# AgentVM LAN3 connectivity test — 2026-10-16

## Setup
- Source: Fedora 44 AgentVM, `enp1s0`, `10.1.30.10/24`
- Gateway: RouterVM `10.1.30.254`
- Method: `ping -c 3 -W 1` to four lab destinations

## Observations

| Destination | Purpose | Result |
| --- | --- | --- |
| `10.1.30.254` | RouterVM gateway | 3 received / 3 transmitted; 0% loss |
| `1.1.1.1` | External IPv4 connectivity | 3 received / 3 transmitted; 0% loss |
| `10.1.10.10` | LAN1 Client1 | 0 received / 3 transmitted; 100% loss |
| `10.1.20.10` | LAN2 Client2 | 0 received / 3 transmitted; 100% loss |

The screenshot supplied for this test shows the successful replies to the gateway and external destination and timeouts for the two other internal clients. These results **match the expected security policy**, but a ping timeout by itself is insufficient to attribute the failure to nftables. Firewall counter deltas and/or controlled packet traces are needed to confirm the enforcement point.

## Next verification
On RouterVM, inspect forward rules and counters:

```bash
sudo nft -a list chain inet filter forward
```

To establish causation more confidently, record counter values, repeat the LAN3-to-LAN1/LAN2 probes, and record deltas in the specific `enp9s0` → `enp7s0/enp8s0` drop rule. Make sure destinations are online, and consider a permitted reverse/control test.

## Evidence provenance
Results were transcribed from a user-provided Fedora terminal screenshot dated 2026-10-16. The screenshot is not yet committed to this repository; the report records the observed outputs only.

## Firewall counter verification — follow-up

After the six unsuccessful LAN3-to-client pings, the RouterVM `inet filter forward` chain was inspected with `sudo nft -a list chain inet filter forward`.

- Before the tests, the explicit `enp9s0` → `enp7s0/enp8s0` drop rule had **0 packets**.
- After the tests, the same rule had **6 packets / 504 bytes dropped**.
- The six-packet increase matches the three ICMP echo attempts to each of the two internal clients.
- The LAN3 → WAN allow rule showed **48 packets / 3,480 bytes accepted** at inspection time (cumulative counter; not all necessarily from this test).
- The reverse LAN1/LAN2 → LAN3 drop rule remained at **0 packets**, so reverse-direction isolation still requires testing.

**Conclusion:** This establishes strong evidence that nftables blocked the six observed LAN3-to-LAN1/LAN2 probes. It does not prove every protocol or all bidirectional paths are blocked. The evidence is a transcription of user-provided command output; no raw screenshot has been committed.

## Reverse-direction verification — Client1 to AgentVM

Client1 (`10.1.10.10`) sent three ICMP echo requests to AgentVM (`10.1.30.10`) using `ping -c 3 -W 1 10.1.30.10`. The user-provided screenshot shows **3 transmitted, 0 received, 100% loss**.

The RouterVM's reverse-direction isolation rule, `iifname { "enp7s0", "enp8s0" } oifname "enp9s0" counter drop`, increased from **0 to 3 packets (252 bytes)**. That matches the three attempted probes and provides direct firewall evidence for the Client1 → AgentVM denial.

**Verified scope:** AgentVM → Client1/Client2 and Client1 → AgentVM were blocked for tested ICMP echo requests. AgentVM → gateway and external IPv4 ping succeeded. Client2 → AgentVM was not separately tested; non-ICMP traffic and stateful connection behavior were not exhaustively assessed.

## Fresh post-restart isolation check — 2026-10-16

A later test following the RouterVM startup used `ping -c 3 -W 1 10.1.10.10` from AgentVM. Its console reported **3 transmitted, 0 received (100% loss)**. The RouterVM's `nft -a list chain inet filter forward` output then showed the explicit LAN3-to-LAN1/LAN2 drop rule at **3 packets / 252 bytes**, compared with **0 packets / 0 bytes** in the immediately preceding RouterVM screenshot. The rule-specific increase corresponds to the three ICMP attempts.

The routing screenshot at this time showed WAN and three LAN interfaces up, with the expected connected routes and default route. This verifies the tested **AgentVM → Client1 ICMP isolation path after restarting the VMs**; other protocols and directions were not repeated. Selected cropped screenshots for this post-restart check are committed: [AgentVM ping results](evidence/lan3-to-lan1-denied.png), [RouterVM drop counter](evidence/nftables-drop-counter.png), and [routing and pre-test counters](evidence/network-routes-firewall.png). These support this specific three-packet check; they do not supply raw image evidence for every earlier observation in this report.
