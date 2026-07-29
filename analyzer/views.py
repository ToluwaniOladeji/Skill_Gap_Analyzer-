from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EmailAuthenticationForm, ProfileForm, RegistrationForm
from .models import Assessment, AssessmentSkillRating, JobRole, RoleSkillRequirement
from .pdf import assessment_report_response
from .services import compute_gap, generate_learning_path


def healthz(request):
    return HttpResponse("ok")

def landing(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome. Your account is ready.")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    recent = (
        Assessment.objects.filter(user=request.user)
        .select_related("role")
        .values("role_id", "role__name")
        .annotate(latest=Max("created_at"))
        .order_by("role__name")
    )
    cards = []
    for item in recent:
        assessment = (
            Assessment.objects.filter(
                user=request.user, role_id=item["role_id"], created_at=item["latest"]
            )
            .select_related("role")
            .first()
        )
        if assessment:
            cards.append(assessment)
    return render(
        request,
        "analyzer/dashboard.html",
        {
            "cards": cards,
            "show_onboarding": not Assessment.objects.filter(user=request.user).exists(),
            "breadcrumbs": [("Dashboard", "")],
        },
    )


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("profile")
    return render(
        request,
        "analyzer/profile.html",
        {"form": form, "breadcrumbs": [("Dashboard", "dashboard"), ("Profile", "")]},
    )


@login_required
def select_role(request):
    roles = JobRole.objects.prefetch_related("requirements").all()
    return render(
        request,
        "analyzer/select_role.html",
        {"roles": roles, "breadcrumbs": [("Dashboard", "dashboard"), ("Start Assessment", "")]},
    )


@login_required
def assessment_form(request, role_id):
    role = get_object_or_404(JobRole, pk=role_id)
    requirements = (
        RoleSkillRequirement.objects.select_related("skill")
        .filter(role=role)
        .order_by("skill__name")
    )
    if not requirements.exists():
        messages.error(request, "This role does not have skill requirements yet.")
        return redirect("select_role")
    return render(
        request,
        "analyzer/assessment_form.html",
        {
            "role": role,
            "requirements": requirements,
            "breadcrumbs": [
                ("Dashboard", "dashboard"),
                ("Start Assessment", "select_role"),
                (role.name, ""),
            ],
        },
    )


@login_required
@transaction.atomic
def submit_assessment(request):
    if request.method != "POST":
        return redirect("select_role")
    role = get_object_or_404(JobRole, pk=request.POST.get("role_id"))
    ratings = {
        key.removeprefix("rating_"): value
        for key, value in request.POST.items()
        if key.startswith("rating_")
    }
    try:
        gap_results, readiness = compute_gap(role, ratings)
    except ValidationError as exc:
        messages.error(request, exc.messages[0])
        return redirect("assessment_form", role_id=role.id)

    assessment = Assessment.objects.create(
        user=request.user, role=role, readiness_percentage=readiness
    )
    AssessmentSkillRating.objects.bulk_create(
        [
            AssessmentSkillRating(
                assessment=assessment,
                skill_id=result.skill_id,
                rating=result.rating,
                required_level=result.required_level,
                gap_score=result.gap_score,
            )
            for result in gap_results
        ]
    )
    messages.success(request, "Assessment submitted. Your results are ready.")
    return redirect("results", assessment_id=assessment.id)


def _owned_assessment(request, assessment_id):
    assessment = get_object_or_404(
        Assessment.objects.select_related("role", "user"), pk=assessment_id
    )
    if assessment.user_id != request.user.id:
        raise Http404("Assessment not found.")
    return assessment


@login_required
def results(request, assessment_id):
    assessment = _owned_assessment(request, assessment_id)
    ratings = list(assessment.ratings.select_related("skill").order_by("-gap_score", "skill__name"))
    gap_results = [
        type(
            "StoredGapResult",
            (),
            {
                "skill_id": item.skill_id,
                "skill_name": item.skill.name,
                "skill_description": item.skill.description,
                "rating": item.rating,
                "required_level": item.required_level,
                "gap_score": item.gap_score,
                "met": item.gap_score == 0,
            },
        )()
        for item in ratings
    ]
    learning_path = [] if assessment.readiness_percentage == 100 else generate_learning_path(gap_results)
    return render(
        request,
        "analyzer/results.html",
        {
            "assessment": assessment,
            "ratings": ratings,
            "learning_path": learning_path,
            "breadcrumbs": [
                ("Dashboard", "dashboard"),
                ("History", "history"),
                ("Results", ""),
            ],
        },
    )


@login_required
def download_report(request, assessment_id):
    assessment = _owned_assessment(request, assessment_id)
    return assessment_report_response(assessment)


@login_required
def history(request):
    assessments = (
        Assessment.objects.filter(user=request.user)
        .select_related("role")
        .order_by("-created_at")
    )
    return render(
        request,
        "analyzer/history.html",
        {"assessments": assessments, "breadcrumbs": [("Dashboard", "dashboard"), ("History", "")]},
    )


@login_required
def progress(request):
    roles = JobRole.objects.filter(assessments__user=request.user).distinct().order_by("name")
    selected_role = None
    assessments = []
    chart_labels = []
    chart_scores = []
    comparison = []
    role_id = request.GET.get("role")
    if role_id:
        selected_role = get_object_or_404(roles, pk=role_id)
    elif roles.exists():
        selected_role = roles.first()

    if selected_role:
        assessments = list(
            Assessment.objects.filter(user=request.user, role=selected_role)
            .prefetch_related("ratings__skill")
            .order_by("created_at")
        )
        chart_labels = [item.created_at.strftime("%Y-%m-%d") for item in assessments]
        chart_scores = [float(item.readiness_percentage) for item in assessments]
        if len(assessments) >= 2:
            first = {rating.skill_id: rating for rating in assessments[0].ratings.all()}
            latest = {rating.skill_id: rating for rating in assessments[-1].ratings.all()}
            for skill_id, latest_rating in latest.items():
                first_rating = first.get(skill_id)
                if first_rating:
                    comparison.append(
                        {
                            "skill": latest_rating.skill.name,
                            "first": first_rating.rating,
                            "latest": latest_rating.rating,
                            "change": latest_rating.rating - first_rating.rating,
                        }
                    )
            comparison.sort(key=lambda item: item["skill"])

    return render(
        request,
        "analyzer/progress.html",
        {
            "roles": roles,
            "selected_role": selected_role,
            "assessments": assessments,
            "chart_labels": chart_labels,
            "chart_scores": chart_scores,
            "comparison": comparison,
            "breadcrumbs": [("Dashboard", "dashboard"), ("Progress", "")],
        },
    )
