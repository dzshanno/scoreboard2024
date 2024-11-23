# File: config/wifi_config.py


class WifiConfig:
    AP_CONFIG = {
        "ssid": "Hockey-Scoreboard",
        "wpa_passphrase": None,  # Will be generated on first run
        "country_code": "GB",
        "hw_mode": "g",
        "channel": 7,
        "auth_algs": 1,  # 1=wpa, 2=wep, 3=both
        "wpa": 2,  # WPA2 only
        "wpa_key_mgmt": "WPA-PSK",
        "rsn_pairwise": "CCMP",  # AES encryption
        "ignore_broadcast_ssid": 0,
    }

    DHCP_CONFIG = {
        "interface": "wlan0",
        "ip_range_start": "192.168.4.2",
        "ip_range_end": "192.168.4.20",
        "subnet_mask": "255.255.255.0",
        "lease_time": "24h",
    }
