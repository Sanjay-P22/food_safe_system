import hashlib
import json


GENESIS_HASH = "0" * 64


def calculate_event_hash(event):
    """
    Calculate the SHA-256 hash using the original serialization
    format to maintain compatibility with existing event hashes.
    """
    event_data = {
        "product_id": event.product_id,
        "event_type": event.event_type,
        "location": event.location,
        "description": event.description,
        "event_date": event.event_date.isoformat(),
        "previous_hash": event.previous_hash,
    }

    serialized_data = json.dumps(event_data, sort_keys=True)

    return hashlib.sha256(
        serialized_data.encode("utf-8")
    ).hexdigest()


def verify_hash_chain(product):
    """
    Verify each event's previous-hash link and stored hash.
    """

    events = product.supply_chain_events.order_by("id")
    expected_previous_hash = GENESIS_HASH

    for event in events:
        if event.previous_hash != expected_previous_hash:
            return False

        calculated_hash = calculate_event_hash(event)

        if event.event_hash != calculated_hash:
            return False

        expected_previous_hash = event.event_hash

    return True


def get_hash_chain_status(product):
    """
    Return a status suitable for the product verification page.
    """

    events = product.supply_chain_events.order_by("id")

    if not events.exists():
        return {
            "status": "NOT_YET_VERIFIED",
            "message": "No supply-chain events have been recorded.",
            "is_valid": False,
        }

    if verify_hash_chain(product):
        return {
            "status": "VERIFIED",
            "message": "Hash chain is valid.",
            "is_valid": True,
        }

    return {
        "status": "INVALID",
        "message": (
            "Hash-chain verification failed. "
            "Event data or links may have been modified."
        ),
        "is_valid": False,
    }

