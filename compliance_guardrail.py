import re

BANNED = [
    "guarantee", "guaranteed", "risk-free", "high return", "best deal",
    "fast approval", "instant funding", "make money", "no credit check"
]

def sanitize(message: str):
    lowered = message.lower()
    for word in BANNED:
        if word in lowered:
            return {
                "allowed": False,
                "reason": f"Banned phrase detected: {word}",
                "safe_message": "We help connect eligible business owners with third-party funding providers. All financing is subject to provider approval."
            }
    return {"allowed": True, "safe_message": message}
