import base64
import os
import subprocess

from app.models import Peer


def _random_key() -> str:
    return base64.b64encode(os.urandom(32)).decode("utf-8")[:44]


def _wg_keypair() -> tuple[str, str]:
    private = subprocess.check_output(["wg", "genkey"], text=True).strip()
    public = subprocess.check_output(["wg", "pubkey"], input=private, text=True).strip()
    return private, public


def _wg_psk() -> str:
    return subprocess.check_output(["wg", "genpsk"], text=True).strip()


def generate_peer_keys() -> tuple[str, str, str]:
    """Generate keys using local `wg` when available, fallback to random placeholders."""
    try:
        private_key, public_key = _wg_keypair()
        preshared_key = _wg_psk()
        return private_key, public_key, preshared_key
    except (subprocess.CalledProcessError, FileNotFoundError):
        return _random_key(), _random_key(), _random_key()


def render_awg_config(peer: Peer, endpoint: str, server_public_key: str) -> str:
    return f"""[Interface]
PrivateKey = {peer.private_key}
Address = {peer.allowed_ips.split('/')[0]}
DNS = 1.1.1.1
Jc = {peer.awg_jc}
Jmin = {peer.awg_jmin}
Jmax = {peer.awg_jmax}
S1 = {peer.awg_s1}
S2 = {peer.awg_s2}

[Peer]
PublicKey = {server_public_key}
PresharedKey = {peer.preshared_key}
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = {endpoint}
PersistentKeepalive = 25
"""
