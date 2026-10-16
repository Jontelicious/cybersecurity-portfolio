# nftables configuration example (sanitized)

This is a **reconstructed teaching example** based on the verified RouterVM design, **not a verbatim export** of `/etc/nftables.conf`. Review against the running VM before deploying. It assumes three IPv4 interfaces and a separate upstream libvirt NAT network.

```nft
#!/usr/sbin/nft -f
flush ruleset

define WAN_IF = "enp1s0"
define LAN1_IF = "enp7s0"
define LAN2_IF = "enp8s0"
define LAN1_NET = 10.1.10.0/24
define LAN2_NET = 10.1.20.0/24
define MGMT_NET = 192.168.122.0/24

table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        iifname "lo" accept
        ct state established,related accept
        ct state invalid drop

        iifname { $LAN1_IF, $LAN2_IF } udp dport 67 accept
        iifname { $LAN1_IF, $LAN2_IF } udp dport 53 accept
        iifname { $LAN1_IF, $LAN2_IF } tcp dport 53 accept
        iifname $WAN_IF ip saddr $MGMT_NET tcp dport 22 accept

        ip protocol icmp accept
        meta l4proto ipv6-icmp accept
    }

    chain forward {
        type filter hook forward priority 0; policy drop;
        ct state established,related accept
        ct state invalid drop

        iifname $LAN1_IF oifname $WAN_IF ip saddr $LAN1_NET accept
        iifname $LAN2_IF oifname $WAN_IF ip saddr $LAN2_NET accept
        # No inter-LAN allow rule: packets between LAN1 and LAN2 hit policy drop.
    }
}

table ip nat {
    chain postrouting {
        type nat hook postrouting priority srcnat; policy accept;
        oifname $WAN_IF ip saddr { $LAN1_NET, $LAN2_NET } masquerade
    }
}
```

## Notes and limitations

- The running lab also used logging during verification. Logging rules are **not reconstructed here** because their exact placement, rate limits, and prefixes were not confirmed.
- Default-deny applies separately to incoming router traffic and forwarded transit traffic.
- The input rules intentionally include lab-management SSH access from the upstream virtual network; this is not a recommended exposure pattern for an untrusted WAN.
- IPv6 forwarding policy, DNS resolver behavior, and persistence should be assessed separately.
- Apply changes only from a recoverable VM console or with a rollback plan to avoid locking yourself out.

## Safely compare with the VM

Read-only inspection commands:

```bash
sudo nft -a list ruleset
ip -br addr
ip route
sudo dnsmasq --test
```

If you choose to export the real configuration for documentation, **review it locally first** and remove any secrets, public endpoints, or information belonging to your school before committing.
