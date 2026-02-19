from pathlib import Path
from datetime import datetime
from typing import Dict


USER_MEMORY_FILE = Path("USER_MEMORY.md")
COMPANY_MEMORY_FILE = Path("COMPANY_MEMORY.md")


def memory_gate(user_input: str) -> Dict:
    """
    Decides whether a memory should be written.
    Returns decision object.
    """

    text = user_input.lower()

    # USER memory signals
    if any(phrase in text for phrase in ["i prefer", "i want", "remember that", "from now on"]):
        return {
            "should_write": True,
            "target": "USER",
            "summary": user_input.strip(),
            "confidence": 0.8,
            "reason": "User preference or stable instruction detected."
        }

    # COMPANY memory signals
    if any(word in text for word in ["judge", "requirement", "challenge requires", "submission rule"]):
        return {
            "should_write": True,
            "target": "COMPANY",
            "summary": user_input.strip(),
            "confidence": 0.75,
            "reason": "Reusable project-level learning detected."
        }

    return {
        "should_write": False,
        "target": None,
        "summary": "",
        "confidence": 0.0,
        "reason": "No high-signal pattern detected."
    }


def write_memory(decision: Dict):
    if not decision["should_write"]:
        return

    file_path = USER_MEMORY_FILE if decision["target"] == "USER" else COMPANY_MEMORY_FILE

    timestamp = datetime.now().strftime("%Y-%m-%d")

    entry = f"""
## {timestamp}
- fact: {decision['summary']}
  confidence: {decision['confidence']}
  reason: {decision['reason']}
"""

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(entry)
