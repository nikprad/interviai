import json
from pathlib import Path


# backend/app/data/
DATA_DIR = Path(__file__).parent / "data"

CURRICULUM_FILE = DATA_DIR / "curriculum.json"
CANDIDATES_FILE = DATA_DIR / "candidates.json"


def load_json(file_path: Path, default):
    """
    Safely load a JSON file.

    If the file doesn't exist, is empty, or contains invalid JSON,
    return the provided default value.
    """
    if not file_path.exists():
        return default

    try:
        if file_path.stat().st_size == 0:
            return default

        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return default


# Load the organizer-provided data
CURRICULUM = load_json(CURRICULUM_FILE, {})
CANDIDATES = load_json(CANDIDATES_FILE, [])


def candidate_by_id(candidate_id: str):
    """
    Find and normalize a candidate from the organizer-provided data.
    """

    candidates_list = CANDIDATES

    if isinstance(CANDIDATES, dict):
        candidates_list = (
            CANDIDATES.get("candidates")
            or CANDIDATES.get("data")
            or []
        )

    if not isinstance(candidates_list, list):
        return None

    for candidate in candidates_list:

        if not isinstance(candidate, dict):
            continue

        # Organizer data stores ID inside "member"
        member = candidate.get("member", {})

        actual_id = (
            member.get("id")
            or candidate.get("id")
            or candidate.get("candidate_id")
            or candidate.get("candidateId")
        )

        if str(actual_id) != str(candidate_id):
            continue

        # Convert completed/passed missions into curriculum day numbers
        completed_days = []

        for mission in candidate.get("missions", []):
            if not isinstance(mission, dict):
                continue

            if mission.get("passed") is True:
                day = mission.get("day")

                if day is not None:
                    completed_days.append(day)

        # Return a normalized candidate object
        return {
            "id": actual_id,
            "name": member.get("name", candidate.get("name", "")),
            "job_role": member.get(
                "jobRole",
                candidate.get("jobRole", "")
            ),
            "years_experience": member.get(
                "yearsExperience",
                candidate.get("yearsExperience")
            ),
            "education": member.get(
                "education",
                candidate.get("education", "")
            ),
            "status": candidate.get("status", ""),
            "completed_days": sorted(set(completed_days)),
            "missions": candidate.get("missions", []),
            "signals": candidate.get("signals", {}),
        }

    return None