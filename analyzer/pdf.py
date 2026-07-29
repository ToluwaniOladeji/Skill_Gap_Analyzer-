from django.http import HttpResponse
from django.template.loader import render_to_string

from .services import generate_learning_path


def _stored_gap_results(assessment):
    ratings = assessment.ratings.select_related("skill").order_by("-gap_score", "skill__name")
    return [
        type(
            "StoredGapResult",
            (),
            {
                "skill_id": rating.skill_id,
                "skill_name": rating.skill.name,
                "skill_description": rating.skill.description,
                "rating": rating.rating,
                "required_level": rating.required_level,
                "gap_score": rating.gap_score,
                "met": rating.gap_score == 0,
            },
        )()
        for rating in ratings
    ]


def assessment_report_response(assessment):
    try:
        from weasyprint import HTML
    except (ImportError, OSError) as exc:
        return HttpResponse(
            "PDF generation requires WeasyPrint and its native GTK/Pango libraries. "
            f"Server detail: {exc}",
            status=503,
            content_type="text/plain",
        )

    gap_results = _stored_gap_results(assessment)
    learning_groups = generate_learning_path(gap_results)
    top_resources = []
    for group in learning_groups:
        for resource in group["resources"]:
            top_resources.append({"gap": group["gap"], "resource": resource})
            if len(top_resources) == 5:
                break
        if len(top_resources) == 5:
            break

    html = render_to_string(
        "analyzer/report_pdf.html",
        {
            "assessment": assessment,
            "ratings": assessment.ratings.select_related("skill").order_by(
                "-gap_score", "skill__name"
            ),
            "top_resources": top_resources,
        },
    )
    pdf = HTML(string=html).write_pdf()
    filename = f"skill-gap-report-{assessment.id}.pdf"
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
