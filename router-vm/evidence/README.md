# RouterVM — verification screenshots (2026-10-16)

Images cropped from the owner's screenshots. The command results are unchanged. Review before public distribution; screenshots contain private virtual lab IPs and some terminal account context. No school/Tailscale device inventory is included.

- `network-routes-firewall.png`: WAN/LAN interface addressing, routing table, and active nftables forwarding rules. All counters shown at zero before generating test traffic.
- `lan3-to-lan1-denied.png`: AgentVM ICMP test to Client1; 3 requests transmitted and no responses. A timeout alone would not establish firewall enforcement.
- `nftables-drop-counter.png`: Matching RouterVM nftables isolation drop rule showing three dropped packets / 252 bytes; prior screenshot showed zero.
- `lan3-allowed-connectivity.png`: AgentVM gateway and external IPv4 reachability, 3/3 packets received on each path.

The evidence covers selected ICMP paths, not every protocol or all possible traffic patterns. These selected images are published in this public portfolio. Their presence does not establish that a complete privacy review has been performed; review any additional evidence before publication.
