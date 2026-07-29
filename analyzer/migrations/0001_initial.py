from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("full_name", models.CharField(max_length=150)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now)),
                ("groups", models.ManyToManyField(blank=True, related_name="user_set", related_query_name="user", to="auth.group")),
                ("user_permissions", models.ManyToManyField(blank=True, related_name="user_set", related_query_name="user", to="auth.permission")),
            ],
            options={"ordering": ["email"]},
        ),
        migrations.CreateModel(
            name="JobRole",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                ("description", models.TextField()),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Skill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                ("description", models.TextField()),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="LearningResource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("url", models.URLField()),
                ("difficulty", models.CharField(choices=[("Beginner", "Beginner"), ("Intermediate", "Intermediate"), ("Advanced", "Advanced")], max_length=20)),
                ("description", models.TextField()),
                ("skill", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="learning_resources", to="analyzer.skill")),
            ],
            options={"ordering": ["skill__name", "difficulty", "title"]},
        ),
        migrations.CreateModel(
            name="RoleSkillRequirement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("required_level", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="requirements", to="analyzer.jobrole")),
                ("skill", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="role_requirements", to="analyzer.skill")),
            ],
            options={"ordering": ["role__name", "skill__name"]},
        ),
        migrations.CreateModel(
            name="Assessment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("readiness_percentage", models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ("role", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="assessments", to="analyzer.jobrole")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="assessments", to="analyzer.user")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="AssessmentSkillRating",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rating", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ("required_level", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ("gap_score", models.PositiveSmallIntegerField(default=0)),
                ("assessment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ratings", to="analyzer.assessment")),
                ("skill", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ratings", to="analyzer.skill")),
            ],
            options={"ordering": ["-gap_score", "skill__name"]},
        ),
        migrations.AddIndex(
            model_name="assessment",
            index=models.Index(fields=["user", "role", "-created_at"], name="analyzer_as_user_id_6b639e_idx"),
        ),
        migrations.AddConstraint(
            model_name="roleskillrequirement",
            constraint=models.UniqueConstraint(fields=("role", "skill"), name="unique_requirement_per_role_skill"),
        ),
        migrations.AddConstraint(
            model_name="roleskillrequirement",
            constraint=models.CheckConstraint(check=models.Q(("required_level__gte", 1), ("required_level__lte", 5)), name="required_level_between_1_and_5"),
        ),
        migrations.AddConstraint(
            model_name="assessmentskillrating",
            constraint=models.UniqueConstraint(fields=("assessment", "skill"), name="unique_rating_per_assessment_skill"),
        ),
        migrations.AddConstraint(
            model_name="assessmentskillrating",
            constraint=models.CheckConstraint(check=models.Q(("rating__gte", 1), ("rating__lte", 5)), name="rating_between_1_and_5"),
        ),
    ]
