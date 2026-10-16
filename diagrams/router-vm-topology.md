# RouterVM network topology — current layout

This diagram reflects the interfaces and routes reported on 2026-10-16. LAN3 was added for the isolated AgentVM network. The AgentVM's DHCP lease was subsequently verified from its Fedora console: `10.1.30.10/24` with default gateway `10.1.30.254`.

```mermaid
flowchart TD
    Internet["External networks"]
    Upstream["libvirt NAT<br/>Gateway 192.168.122.1"]
    Router["Debian RouterVM<br/>WAN enp1s0: 192.168.122.89<br/>LAN1 enp7s0: 10.1.10.254<br/>LAN2 enp8s0: 10.1.20.254<br/>LAN3 enp9s0: 10.1.30.254"]
    C1["Client1 Debian<br/>10.1.10.10"]
    C2["Client2 Debian<br/>10.1.20.10"]
    Agent["Fedora AgentVM<br/>10.1.30.10/24 (DHCP)"]
    Internet <--> Upstream
    Upstream <--> Router
    Router <--> |"LAN1 10.1.10.0/24"| C1
    Router <--> |"LAN2 10.1.20.0/24"| C2
    Router <--> |"LAN3 10.1.30.0/24"| Agent
```

## Current firewall policy (separate from the original coursework exercise)

- All three LANs have explicit permission to forward new traffic to WAN, with IPv4 masquerading for their respective subnets.
- LAN1 ↔ LAN2 forwarding is explicitly **allowed** in the active ruleset.
- LAN3 ↔ LAN1/LAN2 forwarding is explicitly **denied** for new connections.
- Stateful established/related rules precede segment-specific rules.
- Input and forward chains default to drop, with rate-limited logging for unmatched traffic.

See [the active nftables snapshot](../router-vm/configs/active-nftables-snapshot-2026-10-16.md). These are ruleset observations, not proof of newly executed connectivity tests. The original two-LAN assignment used different inter-LAN policy.
