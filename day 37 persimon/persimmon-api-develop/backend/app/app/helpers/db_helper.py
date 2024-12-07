import time

CURRENT_USER = "persimmon-dev@symphonize.com"


def get_metadata():
    timestamp = time.time()
    return {
        "audit": {
            "created_at": timestamp,
            "created_by": {"email": CURRENT_USER},
            "updated_at": timestamp,
            "updated_by": {"email": CURRENT_USER},
        },
    }


def update_meta(meta: dict, email: str):
    meta["audit"]["updated_at"] = time.time()
    meta["audit"]["updated_by"]["email"] = email
    return meta
