from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must provide an email address.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return self.full_name or self.email

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split()[0] if self.full_name else self.email


class JobRole(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class RoleSkillRequirement(models.Model):
    role = models.ForeignKey(
        JobRole, on_delete=models.CASCADE, related_name="requirements"
    )
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name="role_requirements"
    )
    required_level = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        ordering = ["role__name", "skill__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["role", "skill"], name="unique_requirement_per_role_skill"
            ),
            models.CheckConstraint(
                check=models.Q(required_level__gte=1) & models.Q(required_level__lte=5),
                name="required_level_between_1_and_5",
            ),
        ]

    def __str__(self):
        return f"{self.role} requires {self.skill} at {self.required_level}"

    def get_gap(self, rating):
        return max(0, self.required_level - int(rating))


class Assessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assessments")
    role = models.ForeignKey(JobRole, on_delete=models.PROTECT, related_name="assessments")
    created_at = models.DateTimeField(auto_now_add=True)
    readiness_percentage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "role", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.role} - {self.readiness_percentage:.0f}%"


class AssessmentSkillRating(models.Model):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="ratings"
    )
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT, related_name="ratings")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    required_level = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    gap_score = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-gap_score", "skill__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["assessment", "skill"], name="unique_rating_per_assessment_skill"
            ),
            models.CheckConstraint(
                check=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name="rating_between_1_and_5",
            ),
        ]

    def __str__(self):
        return f"{self.skill}: {self.rating}/{self.required_level}"

    def compute_gap(self):
        self.gap_score = max(0, self.required_level - self.rating)
        return self.gap_score


class LearningResource(models.Model):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    DIFFICULTY_CHOICES = [
        (BEGINNER, BEGINNER),
        (INTERMEDIATE, INTERMEDIATE),
        (ADVANCED, ADVANCED),
    ]

    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name="learning_resources"
    )
    title = models.CharField(max_length=180)
    url = models.URLField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    description = models.TextField()

    class Meta:
        ordering = ["skill__name", "difficulty", "title"]

    def __str__(self):
        return f"{self.title} ({self.skill})"
