# Active nftables policy — snapshot reviewed 2026-10-16

This is a **sanitized transcription of the user-provided `sudo nft -a list ruleset` output**, with runtime handles and counters omitted for readability. It is documentation, **not an independently verified backup of the firewall file**, and should not be deployed without reviewing the running interface addressing and persistent configuration.

## Observed policy

| Flow | Rule action |
| --- | --- |
| LAN1 (`enp7s0`) → WAN (`enp1s0`) | Accept |
| LAN2 (`enp8s0`) → WAN | Accept |
| LAN3 (`enp9s0`) → WAN | Accept |
| LAN1 ↔ LAN2 | Accept |
| LAN3 → LAN1/LAN2 | Drop |
| LAN1/LAN2 → LAN3 | Drop |
| Other unmatched forwarded traffic | Rate-limited log and drop |

The NAT rules include `10.1.10.0/24`, `10.1.20.0/24`, and `10.1.30.0/24`. **An IP source subnet in NAT does not independently prove the corresponding interface address or active client connectivity.** Verify LAN3 with `ip -br addr` and `ip route`.

## Transcribed policy

```nft
table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;
        iifname "lo" accept
        ct state established,related accept
        ct state invalid drop
        iifname { "enp7s0", "enp8s0", "enp9s0" } udp dport 67 accept
        iifname { "enp7s0", "enp8s0", "enp9s0" } udp dport 53 accept
        iifname { "enp7s0", "enp8s0", "enp9s0" } tcp dport 53 accept
        iifname "enp1s0" ip saddr 192.168.122.0/24 tcp dport 22 accept
        ip protocol icmp accept
        meta l4proto ipv6-icmp accept
        counter log prefix "NFT INPUT DROP: " limit rate 5/second burst 5 packets drop
    }
    chain forward {
        type filter hook forward priority filter; policy drop;
        ct state established,related counter accept
        ct state invalid counter drop
        iifname "enp9s0" oifname { "enp7s0", "enp8s0" } counter drop
        iifname { "enp7s0", "enp8s0" } oifname "enp9s0" counter drop
        iifname "enp9s0" oifname "enp1s0" counter accept
        iifname "enp7s0" oifname "enp1s0" counter accept
        iifname "enp8s0" oifname "enp1s0" counter accept
        iifname "enp7s0" oifname "enp8s0" counter accept
        iifname "enp8s0" oifname "enp7s0" counter accept
        counter log prefix "NFT FORWARD DROP: " limit rate 5/second burst 5 packets drop
    }
}
table ip nat {
    chain postrouting {
        type nat hook postrouting priority srcnat; policy accept;
        oifname "enp1s0" ip saddr 10.1.10.0/24 masquerade
        oifname "enp1s0" ip saddr 10.1.20.0/24 masquerade
        oifname "enp1s0" ip saddr 10.1.30.0/24 masquerade
    }
}
```

## Interpretation and verification caveats

- LAN3 is explicitly separated from LAN1/LAN2 for **new** routed flows, while LAN1 ↔ LAN2 is explicitly allowed.
- Stateful `established,related` acceptance precedes the segment-specific drops. Existing connection-tracking entries may continue to be accepted after a ruleset change.
- The observed counters for LAN1 ↔ LAN2 and LAN3-related forward rules were zero. They do **not** demonstrate that either an allowed or blocked test was performed after this policy was loaded.
- The input drop rule had 83 packets / 9,014 bytes at capture time. Forward drop rule counters were zero. Counter values are a point-in-time observation, not a comprehensive security assessment.
- Dropped traffic may not always appear in logs because logging is rate-limited.
- IPv6 needs separate review if IPv6 is enabled: the NAT table here is IPv4-specific.

## Recommended next checks

```bash
ip -br addr
ip route
sudo nft -a list ruleset
sudo systemctl is-enabled nftables
```

Then run positive and negative tests from designated lab clients, observe new firewall counter values, and note the date and source. A failed ping by itself is insufficient to prove firewall isolation.

**Historical context:** the original coursework configuration had two mutually isolated LANs. This snapshot describes a later, modified ruleset with a third LAN and different inter-LAN permissions. Keep the original exercise's results separate from tests of this updated policy.
