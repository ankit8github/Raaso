import uuid
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.models import Attendance, Match, User


@dataclass
class MatchingConfig:
    max_intent_score: int = 35
    max_dance_score: int = 25
    max_vibes_score: int = 25
    max_group_size_score: int = 15

    # Intent compatibility map (symmetric matrix weights 0.0 to 1.0)
    intent_compatibilities: dict[tuple[str, str], float] = field(
        default_factory=lambda: {
            ("hardcore_garba", "hardcore_garba"): 1.0,
            ("social_casual", "social_casual"): 1.0,
            ("chilling_food", "chilling_food"): 1.0,
            ("learning", "learning"): 1.0,
            ("hardcore_garba", "social_casual"): 0.6,
            ("social_casual", "chilling_food"): 0.75,
            ("social_casual", "learning"): 0.75,
            ("hardcore_garba", "learning"): 0.4,
            ("hardcore_garba", "chilling_food"): 0.25,
            ("chilling_food", "learning"): 0.5,
        }
    )

    dance_level_ranks: dict[str, int] = field(
        default_factory=lambda: {
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3,
            "pro": 3,
            "expert": 3,
        }
    )


class MatchingEngine:
    def __init__(self, config: MatchingConfig | None = None) -> None:
        self.config = config or MatchingConfig()

    def parse_vibes(self, vibes_str: str | None) -> set[str]:
        if not vibes_str:
            return set()
        return {
            v.strip().lower()
            for v in vibes_str.replace(";", ",").split(",")
            if v.strip()
        }

    def score_intent(self, intent_a: str, intent_b: str) -> tuple[int, str | None]:
        norm_a = intent_a.strip().lower()
        norm_b = intent_b.strip().lower()

        if norm_a == norm_b:
            score = self.config.max_intent_score
            label = norm_a.replace("_", " ").title()
            return score, f"Both share '{label}' intent"

        # Check symmetric key in table
        weight = (
            self.config.intent_compatibilities.get((norm_a, norm_b))
            or self.config.intent_compatibilities.get((norm_b, norm_a))
            or 0.35
        )
        score = int(round(self.config.max_intent_score * weight))
        return score, "Complementary event intents"

    def score_dance_level(
        self, level_a: str, level_b: str
    ) -> tuple[int, str | None]:
        norm_a = level_a.strip().lower()
        norm_b = level_b.strip().lower()

        rank_a = self.config.dance_level_ranks.get(norm_a, 2)
        rank_b = self.config.dance_level_ranks.get(norm_b, 2)

        diff = abs(rank_a - rank_b)
        if diff == 0:
            score = self.config.max_dance_score
            label = norm_a.capitalize()
            return score, f"Exact dance level match ({label})"
        elif diff == 1:
            score = int(round(self.config.max_dance_score * 0.65))
            return score, "Comfortable adjacent dance levels"
        else:
            score = int(round(self.config.max_dance_score * 0.25))
            return score, "Great mix of beginner & experienced dancers"

    def score_vibes(
        self, vibes_a_str: str | None, vibes_b_str: str | None
    ) -> tuple[int, str | None]:
        vibes_a = self.parse_vibes(vibes_a_str)
        vibes_b = self.parse_vibes(vibes_b_str)

        if not vibes_a or not vibes_b:
            # Neutral / flexible score
            return int(round(self.config.max_vibes_score * 0.6)), "Open to all event vibes"

        common = vibes_a.intersection(vibes_b)
        union = vibes_a.union(vibes_b)

        if common:
            jaccard = len(common) / len(union)
            score = int(
                round(
                    self.config.max_vibes_score
                    * min(1.0, 0.4 + (0.6 * jaccard) + 0.1 * len(common))
                )
            )
            score = min(score, self.config.max_vibes_score)
            formatted = ", ".join(tag.replace("_", " ").title() for tag in sorted(common)[:3])
            return score, f"Shared vibes: {formatted}"
        else:
            score = int(round(self.config.max_vibes_score * 0.3))
            return score, "Diverse festival vibes"

    def score_group_size(
        self, pref_a: int | None, pref_b: int | None
    ) -> tuple[int, str | None]:
        if pref_a is None or pref_b is None:
            return int(round(self.config.max_group_size_score * 0.7)), "Flexible group size preference"

        diff = abs(pref_a - pref_b)
        if diff == 0:
            return self.config.max_group_size_score, f"Both prefer group size of {pref_a}"
        elif diff == 1:
            return int(round(self.config.max_group_size_score * 0.85)), "Closely aligned squad size preference"
        elif diff <= 3:
            return int(round(self.config.max_group_size_score * 0.55)), "Compatible group size preference"
        else:
            return int(round(self.config.max_group_size_score * 0.25)), "Different squad size preferences"

    def calculate_match_score(
        self, attendance_a: Attendance, attendance_b: Attendance
    ) -> tuple[int, list[str]]:
        # Hard constraints
        if attendance_a.event_id != attendance_b.event_id:
            return 0, ["Different events"]

        if attendance_a.user_id == attendance_b.user_id:
            return 0, ["Same user"]

        intent_score, intent_reason = self.score_intent(
            attendance_a.intent, attendance_b.intent
        )
        dance_score, dance_reason = self.score_dance_level(
            attendance_a.dance_level, attendance_b.dance_level
        )
        vibes_score, vibes_reason = self.score_vibes(
            attendance_a.vibes, attendance_b.vibes
        )
        size_score, size_reason = self.score_group_size(
            attendance_a.group_size_preference,
            attendance_b.group_size_preference,
        )

        total_score = min(
            100, intent_score + dance_score + vibes_score + size_score
        )

        reasons = [
            r
            for r in [intent_reason, dance_reason, vibes_reason, size_reason]
            if r is not None
        ]
        return total_score, reasons

    def find_matches_for_attendance(
        self,
        db: Session,
        attendance: Attendance,
        limit: int = 20,
    ) -> list[dict]:
        """Finds and ranks matches for a given attendance in the same event."""
        # Query candidate attendances for the same event excluding the user
        stmt = (
            select(Attendance)
            .where(
                Attendance.event_id == attendance.event_id,
                Attendance.user_id != attendance.user_id,
            )
        )
        candidates = db.scalars(stmt).all()

        scored_matches = []
        for candidate in candidates:
            score, reasons = self.calculate_match_score(attendance, candidate)
            user = db.get(User, candidate.user_id)
            if not user:
                continue

            scored_matches.append(
                {
                    "attendance_id": attendance.id,
                    "matched_attendance_id": candidate.id,
                    "score": score,
                    "matched_user": user,
                    "matched_attendance": candidate,
                    "reasons": reasons,
                }
            )

        # Sort descending by score
        scored_matches.sort(key=lambda x: x["score"], reverse=True)
        return scored_matches[:limit]


matching_service = MatchingEngine()

