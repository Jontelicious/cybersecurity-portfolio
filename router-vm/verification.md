# RouterVM verification checklist

This checklist distinguishes the **original two-LAN assignment** from the **current three-LAN policy**. The configurations have different inter-LAN access rules. Do not present original results as proof of the current ruleset.

## Current policy (three LANs, October 2026)

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

## Original coursework policy (historical)

The original two-LAN exercise **blocked LAN1 ↔ LAN2** while allowing each LAN to reach WAN. Those earlier checks and drop logs were valid for that *older* configuration, not for the current three-LAN firewall.

The [two-LAN nftables teaching example](configs/nftables-example.md) is also historical and must not be treated as a copy of the live ruleset.

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

## Remaining checks

- [ ] Fresh LAN1 ↔ LAN2 permitted-flow tests under the current policy
- [ ] Fresh Client2 → AgentVM denied-flow test
- [ ] Broader TCP/UDP and stateful traffic checks where needed
- [ ] Full startup/persistence validation for DHCP, DNS, nftables and guest routing
- [ ] Review all images and tracked configuration text before public release

## Publication hygiene

Keep school networking details, keys, credentials, actual personal-device MACs, and unredacted logs out of the repository. The example RFC1918 addresses shown here belong to an isolated virtual lab; decide whether to preserve or generalize them before public release.
