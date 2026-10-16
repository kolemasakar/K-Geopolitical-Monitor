"""No-send consumer authorization contract. No keys, transport or runtime permissions."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ConsumerGrant:
    consumer: str
    contract: str
    scope: str
    enabled: bool = False


def authorize_export(consumer, contract, scope, *, grants=(), source_state="UNKNOWN", verification="UNVERIFIED", dry_run=True):
    """Deny unless an exact, explicit active grant and acceptable evidence are present.

    This deliberately never transmits anything. A returned approval is only a
    *contract result*, not authorization to enable a production transport.
    """
    if not dry_run:
        raise PermissionError("network consumer delivery disabled")
    if source_state != "COMPLETE" or verification not in {"VERIFIED","DISPUTED"}:
        raise PermissionError("insufficient source or verification quality")
    if scope != "news-research" and verification != "VERIFIED":
        raise PermissionError("disputed evidence restricted to research scope")
    if not all(isinstance(x,str) and x and len(x)<=128 for x in (consumer,contract,scope)):
        raise ValueError("invalid identity")
    if not any(isinstance(g,ConsumerGrant) and g.enabled and
               (g.consumer,g.contract,g.scope)==(consumer,contract,scope) for g in grants):
        raise PermissionError("consumer not enrolled for exact scope")
    return {"consumer":consumer,"contract":contract,"scope":scope,"offline_approved":True,"sent":False}
