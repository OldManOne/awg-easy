# awg-easy

Prototype of a `wg-easy`-like control plane adapted for **AmneziaWG**.

## Current scope (MVP bootstrap)

- FastAPI backend with peer CRUD endpoints.
- SQLite persistence for peers.
- AmneziaWG-like config rendering with AWG parameters (`Jc`, `Jmin`, `Jmax`, `S1`, `S2`).
- Input validation for CIDR and AWG value ranges.
- Environment-driven server endpoint/public key settings.
- API tests with pytest.

## API

- `GET /health`
- `GET /api/peers`
- `GET /api/peers/{peer_id}`
- `POST /api/peers`
- `PUT /api/peers/{peer_id}`
- `GET /api/peers/{peer_id}/config`
- `DELETE /api/peers/{peer_id}`

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload --port 8080
```

Then open: `http://localhost:8080/docs`

## Configuration

Environment variables:

- `AWG_SERVER_PUBLIC_KEY` (default: `REPLACE_WITH_SERVER_PUBLIC_KEY`)
- `AWG_SERVER_ENDPOINT` (default: `vpn.example.com:51820`)

## Run tests

```bash
pytest -q
```

## Important notes

- Key generation tries to use local `wg` tooling (`wg genkey`, `wg pubkey`, `wg genpsk`) and falls back to random placeholder keys if unavailable.
- This is still a development prototype and not production hardened yet.
