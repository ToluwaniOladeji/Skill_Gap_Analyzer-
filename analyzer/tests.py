from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import (
    Assessment,
    AssessmentSkillRating,
    JobRole,
    LearningResource,
    RoleSkillRequirement,
    Skill,
)
from .services import compute_gap, generate_learning_path


@override_settings(SECURE_SSL_REDIRECT=False)
class AnalyzerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="graduate@example.com",
            full_name="Graduate User",
            password="pass12345",
        )
        self.other = get_user_model().objects.create_user(
            email="other@example.com",
            full_name="Other User",
            password="pass12345",
        )
        self.role = JobRole.objects.create(
            name="Web Developer", description="Builds web applications."
        )
        self.skills = [
            Skill.objects.create(name=f"Skill {index}", description="Description")
            for index in range(1, 16)
        ]
        for skill in self.skills:
            RoleSkillRequirement.objects.create(
                role=self.role, skill=skill, required_level=3
            )
        LearningResource.objects.create(
            skill=self.skills[0],
            title="Resource",
            url="https://example.com/resource",
            difficulty=LearningResource.BEGINNER,
            description="Learn the skill.",
        )

    def test_compute_gap_and_readiness(self):
        ratings = {skill.id: 3 for skill in self.skills}
        ratings[self.skills[0].id] = 1
        results, readiness = compute_gap(self.role, ratings)
        self.assertEqual(readiness, round((14 / 15) * 100, 2))
        self.assertEqual(results[0].skill_id, self.skills[0].id)
        self.assertEqual(results[0].gap_score, 2)

    def test_learning_path_uses_only_positive_gap_resources(self):
        ratings = {skill.id: 3 for skill in self.skills}
        ratings[self.skills[0].id] = 1
        results, _ = compute_gap(self.role, ratings)
        path = generate_learning_path(results)
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0]["resources"][0].skill_id, self.skills[0].id)

    def test_assessment_submission_creates_permanent_records(self):
        self.client.login(email="graduate@example.com", password="pass12345")
        payload = {"role_id": self.role.id}
        payload.update({f"rating_{skill.id}": "3" for skill in self.skills})
        for _ in range(2):
            response = self.client.post(reverse("submit_assessment"), payload)
            self.assertEqual(response.status_code, 302)
        self.assertEqual(Assessment.objects.filter(user=self.user, role=self.role).count(), 2)
        self.assertEqual(AssessmentSkillRating.objects.count(), 30)

    def test_results_are_restricted_to_owner(self):
        assessment = Assessment.objects.create(
            user=self.other, role=self.role, readiness_percentage=100
        )
        self.client.login(email="graduate@example.com", password="pass12345")
        response = self.client.get(reverse("results", args=[assessment.id]))
        self.assertEqual(response.status_code, 404)

    def test_login_required_for_platform_pages(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])
