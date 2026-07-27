from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import path
from django.template.response import TemplateResponse

from .forms import UserChangeAdminForm, UserCreationAdminForm
from .models import (
    Assessment,
    AssessmentSkillRating,
    JobRole,
    LearningResource,
    RoleSkillRequirement,
    Skill,
    User,
)


class RoleSkillRequirementInline(admin.TabularInline):
    model = RoleSkillRequirement
    extra = 1


class LearningResourceInline(admin.TabularInline):
    model = LearningResource
    extra = 1


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeAdminForm
    add_form = UserCreationAdminForm
    list_display = ["email", "full_name", "is_staff", "latest_readiness_summary"]
    list_filter = ["is_staff", "is_superuser", "is_active"]
    ordering = ["email"]
    search_fields = ["email", "full_name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("full_name",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("full_name", "email", "password1", "password2")}),
    )

    def latest_readiness_summary(self, obj):
        latest = (
            Assessment.objects.filter(user=obj)
            .select_related("role")
            .order_by("role__name", "-created_at")
        )
        seen = set()
        parts = []
        for assessment in latest:
            if assessment.role_id not in seen:
                parts.append(f"{assessment.role.name}: {assessment.readiness_percentage:.0f}%")
                seen.add(assessment.role_id)
        return ", ".join(parts) if parts else "No assessments"


@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ["name", "requirement_count"]
    search_fields = ["name", "description"]
    inlines = [RoleSkillRequirementInline]

    def requirement_count(self, obj):
        return obj.requirements.count()


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name", "description"]
    inlines = [LearningResourceInline]


@admin.register(RoleSkillRequirement)
class RoleSkillRequirementAdmin(admin.ModelAdmin):
    list_display = ["role", "skill", "required_level"]
    list_filter = ["role", "required_level"]
    search_fields = ["role__name", "skill__name"]


@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ["title", "skill", "difficulty", "url"]
    list_filter = ["skill", "difficulty"]
    search_fields = ["title", "description", "skill__name"]


class AssessmentSkillRatingInline(admin.TabularInline):
    model = AssessmentSkillRating
    extra = 0
    readonly_fields = ["skill", "rating", "required_level", "gap_score"]
    can_delete = False


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "created_at", "readiness_percentage"]
    list_filter = ["role", "created_at"]
    search_fields = ["user__email", "user__full_name", "role__name"]
    readonly_fields = ["user", "role", "created_at", "readiness_percentage"]
    inlines = [AssessmentSkillRatingInline]

    def has_add_permission(self, request):
        return False


def graduate_progress_view(request):
    users = User.objects.filter(is_staff=False).prefetch_related("assessments__role")
    return TemplateResponse(
        request,
        "admin/analyzer/graduate_progress.html",
        {"title": "Graduate progress", "users": users},
    )


original_get_urls = admin.site.get_urls


def get_urls():
    return [
        path(
            "graduate-progress/",
            admin.site.admin_view(graduate_progress_view),
            name="graduate_progress",
        )
    ] + original_get_urls()


admin.site.get_urls = get_urls
admin.site.site_header = "Skill Gap Analyzer Admin"
admin.site.site_title = "Skill Gap Analyzer Admin"
admin.site.index_title = "Platform content management"
