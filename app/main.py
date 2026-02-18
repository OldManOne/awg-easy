from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.awg import generate_peer_keys, render_awg_config
from app.database import Base, engine, get_db
from app.models import Peer
from app.schemas import PeerConfigOut, PeerCreate, PeerOut, PeerUpdate
from app.settings import SERVER_ENDPOINT, SERVER_PUBLIC_KEY

app = FastAPI(title="awg-easy", version="0.2.0")
Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/peers", response_model=list[PeerOut])
def list_peers(db: Session = Depends(get_db)):
    return db.query(Peer).order_by(Peer.id.asc()).all()


@app.get("/api/peers/{peer_id}", response_model=PeerOut)
def get_peer(peer_id: int, db: Session = Depends(get_db)):
    peer = db.query(Peer).filter(Peer.id == peer_id).first()
    if not peer:
        raise HTTPException(status_code=404, detail="Peer not found")
    return peer


@app.post("/api/peers", response_model=PeerOut, status_code=201)
def create_peer(payload: PeerCreate, db: Session = Depends(get_db)):
    exists = db.query(Peer).filter(Peer.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=409, detail="Peer with this name already exists")

    private_key, public_key, preshared_key = generate_peer_keys()
    peer = Peer(
        name=payload.name,
        private_key=private_key,
        public_key=public_key,
        preshared_key=preshared_key,
        allowed_ips=payload.allowed_ips,
        awg_jc=payload.awg_jc,
        awg_jmin=payload.awg_jmin,
        awg_jmax=payload.awg_jmax,
        awg_s1=payload.awg_s1,
        awg_s2=payload.awg_s2,
    )
    db.add(peer)
    db.commit()
    db.refresh(peer)
    return peer


@app.put("/api/peers/{peer_id}", response_model=PeerOut)
def update_peer(peer_id: int, payload: PeerUpdate, db: Session = Depends(get_db)):
    peer = db.query(Peer).filter(Peer.id == peer_id).first()
    if not peer:
        raise HTTPException(status_code=404, detail="Peer not found")

    name_owner = db.query(Peer).filter(Peer.name == payload.name, Peer.id != peer_id).first()
    if name_owner:
        raise HTTPException(status_code=409, detail="Peer with this name already exists")

    peer.name = payload.name
    peer.allowed_ips = payload.allowed_ips
    peer.awg_jc = payload.awg_jc
    peer.awg_jmin = payload.awg_jmin
    peer.awg_jmax = payload.awg_jmax
    peer.awg_s1 = payload.awg_s1
    peer.awg_s2 = payload.awg_s2

    db.commit()
    db.refresh(peer)
    return peer


@app.get("/api/peers/{peer_id}/config", response_model=PeerConfigOut)
def get_peer_config(peer_id: int, db: Session = Depends(get_db)):
    peer = db.query(Peer).filter(Peer.id == peer_id).first()
    if not peer:
        raise HTTPException(status_code=404, detail="Peer not found")

    return {
        "peer": peer,
        "config": render_awg_config(
            peer=peer,
            endpoint=SERVER_ENDPOINT,
            server_public_key=SERVER_PUBLIC_KEY,
        ),
    }


@app.delete("/api/peers/{peer_id}", status_code=204)
def delete_peer(peer_id: int, db: Session = Depends(get_db)):
    peer = db.query(Peer).filter(Peer.id == peer_id).first()
    if not peer:
        raise HTTPException(status_code=404, detail="Peer not found")
    db.delete(peer)
    db.commit()
