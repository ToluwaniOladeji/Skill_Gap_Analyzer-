from dataclasses import dataclass

from django.core.exceptions import ValidationError

from .models import LearningResource, RoleSkillRequirement


@dataclass(frozen=True)
class GapResult:
    skill_id: int
    skill_name: str
    skill_description: str
    rating: int
    required_level: int
    gap_score: int

    @property
    def met(self):
        return self.gap_score == 0


def compute_gap(role, ratings):
    requirements = list(
        RoleSkillRequirement.objects.select_related("skill")
        .filter(role=role)
        .order_by("skill__name")
    )
    if not requirements:
        raise ValidationError("The selected role has no skill requirements configured.")

    normalized = {}
    for skill_id, value in ratings.items():
        try:
            rating = int(value)
        except (TypeError, ValueError):
            raise ValidationError("Every skill rating must be a number from 1 to 5.")
        if rating < 1 or rating > 5:
            raise ValidationError("Every skill rating must be between 1 and 5.")
        normalized[int(skill_id)] = rating

    required_skill_ids = {item.skill_id for item in requirements}
    if set(normalized) != required_skill_ids:
        raise ValidationError("Please rate every required skill before submitting.")

    results = []
    met_count = 0
    for requirement in requirements:
        rating = normalized[requirement.skill_id]
        gap_score = requirement.get_gap(rating)
        if gap_score == 0:
            met_count += 1
        results.append(
            GapResult(
                skill_id=requirement.skill_id,
                skill_name=requirement.skill.name,
                skill_description=requirement.skill.description,
                rating=rating,
                required_level=requirement.required_level,
                gap_score=gap_score,
            )
        )

    readiness = round((met_count / len(requirements)) * 100, 2)
    ranked = sorted(results, key=lambda item: (-item.gap_score, item.skill_name))
    return ranked, readiness


def generate_learning_path(gap_results, resources_per_skill=3):
    path = []
    for gap in [item for item in gap_results if item.gap_score > 0]:
        resources = list(
            LearningResource.objects.filter(skill_id=gap.skill_id)
            .order_by("difficulty", "title")[:resources_per_skill]
        )
        if resources:
            path.append({"gap": gap, "resources": resources})
    return path


def top_learning_resources(gap_results, limit=5):
    resources = []
    for group in generate_learning_path(gap_results):
        for resource in group["resources"]:
            resources.append((group["gap"], resource))
            if len(resources) == limit:
                return resources
    return resources
