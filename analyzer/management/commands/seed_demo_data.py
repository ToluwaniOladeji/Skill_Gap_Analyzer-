from django.core.management.base import BaseCommand

from analyzer.models import JobRole, LearningResource, RoleSkillRequirement, Skill


ROLE_DATA = {
    "Web Developer": {
        "description": "Builds responsive, secure, database-backed web applications.",
        "skills": {
            "HTML": 4,
            "CSS": 4,
            "JavaScript": 4,
            "Python": 3,
            "Django": 4,
            "SQL": 3,
            "Git": 3,
            "Responsive Design": 4,
            "REST APIs": 3,
            "Web Security Basics": 3,
            "Testing Fundamentals": 3,
            "Bootstrap": 3,
            "Deployment Basics": 3,
            "Debugging": 4,
            "Accessibility": 3,
        },
    },
    "Data Analyst": {
        "description": "Turns business data into reliable insights, dashboards, and decisions.",
        "skills": {
            "Python": 4,
            "SQL": 4,
            "Spreadsheet Analysis": 4,
            "Statistics": 3,
            "Data Cleaning": 4,
            "Data Visualization": 4,
            "Power BI": 3,
            "Pandas": 4,
            "Business Communication": 3,
            "Dashboard Design": 3,
            "Critical Thinking": 4,
            "Database Concepts": 3,
            "Experiment Design": 2,
            "Presentation Skills": 3,
            "Data Ethics": 3,
        },
    },
    "IT Support Specialist": {
        "description": "Supports users, devices, networks, and common workplace systems.",
        "skills": {
            "Networking Fundamentals": 4,
            "Operating Systems": 4,
            "Troubleshooting": 4,
            "Customer Support": 4,
            "Cybersecurity Awareness": 3,
            "Hardware Basics": 3,
            "Cloud Fundamentals": 3,
            "Ticketing Systems": 3,
            "Active Directory": 3,
            "Technical Documentation": 3,
            "Backup and Recovery": 3,
            "Mobile Device Support": 3,
            "Email Administration": 3,
            "Remote Support Tools": 3,
            "IT Asset Management": 2,
        },
    },
}


DESCRIPTIONS = {
    "HTML": "Structure semantic web pages with accessible markup.",
    "CSS": "Style layouts, typography, and responsive interfaces.",
    "JavaScript": "Create interactive behavior in the browser.",
    "Python": "Write readable scripts and backend logic.",
    "Django": "Build secure web applications using Django models, views, forms, and templates.",
    "SQL": "Query, join, filter, aggregate, and update relational data.",
    "Git": "Track changes and collaborate using branches, commits, and pull requests.",
    "Responsive Design": "Build interfaces that adapt across desktop, tablet, and mobile screens.",
    "REST APIs": "Design and consume HTTP APIs using resources, status codes, and JSON.",
    "Web Security Basics": "Understand authentication, authorization, CSRF, injection, and secure sessions.",
    "Testing Fundamentals": "Write and run tests that verify expected software behavior.",
    "Bootstrap": "Use Bootstrap components and utilities to build consistent templates.",
    "Deployment Basics": "Configure environment variables, static files, and production hosting basics.",
    "Debugging": "Trace errors, inspect logs, and isolate root causes.",
    "Accessibility": "Use labels, contrast, keyboard navigation, and semantic structure.",
    "Spreadsheet Analysis": "Use formulas, pivot tables, and structured worksheets for analysis.",
    "Statistics": "Apply descriptive statistics, distributions, correlation, and uncertainty.",
    "Data Cleaning": "Prepare messy data by handling missing values, duplicates, and inconsistent formats.",
    "Data Visualization": "Choose charts that communicate patterns honestly and clearly.",
    "Power BI": "Create reports and dashboards with modeled data.",
    "Pandas": "Manipulate tabular data with Python dataframes.",
    "Business Communication": "Explain analytical findings to non-technical stakeholders.",
    "Dashboard Design": "Design focused dashboards with clear metrics and filters.",
    "Critical Thinking": "Evaluate assumptions, evidence quality, and alternative explanations.",
    "Database Concepts": "Understand tables, keys, normalization, and relationships.",
    "Experiment Design": "Plan comparisons that produce meaningful evidence.",
    "Presentation Skills": "Present insights with structure, clarity, and audience awareness.",
    "Data Ethics": "Handle data responsibly with privacy, fairness, and transparency.",
    "Networking Fundamentals": "Understand IP addressing, DNS, DHCP, routing, and common protocols.",
    "Operating Systems": "Support Windows, Linux, and common user environment issues.",
    "Troubleshooting": "Use systematic diagnosis to resolve technical problems.",
    "Customer Support": "Communicate clearly and patiently with users.",
    "Cybersecurity Awareness": "Recognize phishing, malware, access risks, and basic controls.",
    "Hardware Basics": "Identify and support common computer components and peripherals.",
    "Cloud Fundamentals": "Understand cloud accounts, storage, identity, and basic services.",
    "Ticketing Systems": "Record, prioritize, update, and close support requests.",
    "Active Directory": "Support users, groups, permissions, and domain-based identity.",
    "Technical Documentation": "Write clear procedures, incident notes, and knowledge-base articles.",
    "Backup and Recovery": "Protect and restore data after accidental loss or device failure.",
    "Mobile Device Support": "Support common Android and iOS device configuration issues.",
    "Email Administration": "Support mailbox, client, spam, and account access issues.",
    "Remote Support Tools": "Use approved tools to assist users remotely.",
    "IT Asset Management": "Track equipment ownership, condition, and lifecycle.",
}


# Real course links per skill and difficulty, pulled from reputable platforms
# (MDN, freeCodeCamp, Coursera, Microsoft Learn, official docs, etc).
# Skills not listed here fall back to the placeholder example.com URL below.
#
# NOTE: A few soft-skill entries (Business Communication, Critical Thinking,
# Data Ethics, Experiment Design, Presentation Skills) have fewer dedicated
# standalone courses online than the technical skills do. Those links are a
# best-effort match — worth a quick manual check before you rely on them,
# since course catalogs on these platforms shift more often than reference
# docs do.
LEARNING_RESOURCES = {
    "HTML": {
        "Beginner": "https://www.freecodecamp.org/learn/2022/responsive-web-design/",
        "Intermediate": "https://developer.mozilla.org/en-US/docs/Web/HTML",
        "Advanced": "https://web.dev/learn/html/",
    },
    "CSS": {
        "Beginner": "https://www.w3schools.com/css/",
        "Intermediate": "https://developer.mozilla.org/en-US/docs/Web/CSS",
        "Advanced": "https://web.dev/learn/css/",
    },
    "JavaScript": {
        "Beginner": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
        "Intermediate": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
        "Advanced": "https://javascript.info/",
    },
    "Python": {
        "Beginner": "https://www.coursera.org/specializations/python",
        "Intermediate": "https://realpython.com/",
        "Advanced": "https://realpython.com/tutorials/advanced/",
    },
    "Django": {
        "Beginner": "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
        "Intermediate": "https://docs.djangoproject.com/en/stable/topics/db/models/",
        "Advanced": "https://docs.djangoproject.com/en/stable/topics/class-based-views/",
    },
    "SQL": {
        "Beginner": "https://www.w3schools.com/sql/",
        "Intermediate": "https://mode.com/sql-tutorial/",
        "Advanced": "https://mode.com/sql-tutorial/advanced-sql/",
    },
    "Git": {
        "Beginner": "https://git-scm.com/book/en/v2/Getting-Started-Git-Basics",
        "Intermediate": "https://www.atlassian.com/git/tutorials",
        "Advanced": "https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell",
    },
    "Responsive Design": {
        "Beginner": "https://www.freecodecamp.org/learn/2022/responsive-web-design/",
        "Intermediate": "https://web.dev/learn/design/",
        "Advanced": "https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design",
    },
    "REST APIs": {
        "Beginner": "https://developer.mozilla.org/en-US/docs/Glossary/REST",
        "Intermediate": "https://www.freecodecamp.org/learn/back-end-development-and-apis/",
        "Advanced": "https://restfulapi.net/",
    },
    "Web Security Basics": {
        "Beginner": "https://owasp.org/www-project-top-ten/",
        "Intermediate": "https://developer.mozilla.org/en-US/docs/Web/Security",
        "Advanced": "https://cheatsheetseries.owasp.org/",
    },
    "Testing Fundamentals": {
        "Beginner": "https://developer.mozilla.org/en-US/docs/Learn/Tools_and_testing/Understanding_client-side_web_dev_tools/Testing",
        "Intermediate": "https://realpython.com/python-testing/",
        "Advanced": "https://www.obeythetestinggoat.com/",
    },
    "Bootstrap": {
        "Beginner": "https://www.w3schools.com/bootstrap5/",
        "Intermediate": "https://getbootstrap.com/docs/5.3/getting-started/introduction/",
        "Advanced": "https://getbootstrap.com/docs/5.3/customize/overview/",
    },
    "Deployment Basics": {
        "Beginner": "https://docs.djangoproject.com/en/stable/howto/deployment/checklist/",
        "Intermediate": "https://devcenter.heroku.com/articles/django-app-configuration",
        "Advanced": "https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu",
    },
    "Debugging": {
        "Beginner": "https://developer.mozilla.org/en-US/docs/Learn/Common_questions/Tools_and_setup/What_are_browser_developer_tools",
        "Intermediate": "https://realpython.com/python-debugging-pdb/",
        "Advanced": "https://django-debug-toolbar.readthedocs.io/",
    },
    "Accessibility": {
        "Beginner": "https://web.dev/learn/accessibility/",
        "Intermediate": "https://developer.mozilla.org/en-US/docs/Web/Accessibility",
        "Advanced": "https://www.w3.org/WAI/ARIA/apg/",
    },
    "Spreadsheet Analysis": {
        "Beginner": "https://learn.microsoft.com/en-us/training/browse/?products=office-excel",
        "Intermediate": "https://exceljet.net/formulas",
        "Advanced": "https://www.coursera.org/specializations/excel",
    },
    "Statistics": {
        "Beginner": "https://www.khanacademy.org/math/statistics-probability",
        "Intermediate": "https://www.coursera.org/specializations/statistics-with-python",
        "Advanced": "https://seeing-theory.brown.edu/",
    },
    "Data Cleaning": {
        "Beginner": "https://www.coursera.org/learn/data-processing",
        "Intermediate": "https://realpython.com/python-data-cleaning-numpy-pandas/",
        "Advanced": "https://www.kaggle.com/learn/data-cleaning",
    },
    "Data Visualization": {
        "Beginner": "https://www.coursera.org/learn/visualize-data",
        "Intermediate": "https://www.kaggle.com/learn/data-visualization",
        "Advanced": "https://d3js.org/getting-started",
    },
    "Power BI": {
        "Beginner": "https://learn.microsoft.com/en-us/training/modules/get-started-with-power-bi/",
        "Intermediate": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi",
        "Advanced": "https://www.coursera.org/professional-certificates/microsoft-power-bi-data-analyst",
    },
    "Pandas": {
        "Beginner": "https://pandas.pydata.org/docs/getting_started/index.html",
        "Intermediate": "https://www.kaggle.com/learn/pandas",
        "Advanced": "https://realpython.com/pandas-python-explore-dataset/",
    },
    "Business Communication": {
        "Beginner": "https://www.coursera.org/learn/business-communication",
        "Intermediate": "https://www.coursera.org/learn/business-communication",
        "Advanced": "https://www.coursera.org/specializations/improve-english",
    },
    "Dashboard Design": {
        "Beginner": "https://www.tableau.com/learn/training",
        "Intermediate": "https://learn.microsoft.com/en-us/power-bi/create-reports/service-dashboard-create",
        "Advanced": "https://www.tableau.com/learn/training/20232",
    },
    "Critical Thinking": {
        "Beginner": "https://www.coursera.org/learn/philosophy",
        "Intermediate": "https://www.coursera.org/learn/problem-solving",
        "Advanced": "https://www.coursera.org/learn/mindware",
    },
    "Database Concepts": {
        "Beginner": "https://www.khanacademy.org/computing/computer-programming/sql",
        "Intermediate": "https://www.coursera.org/learn/database-design",
        "Advanced": "https://www.coursera.org/learn/database-management",
    },
    "Experiment Design": {
        "Beginner": "https://www.khanacademy.org/math/statistics-probability/designing-studies",
        "Intermediate": "https://www.coursera.org/learn/experimentation",
        "Advanced": "https://www.coursera.org/learn/abtesting",
    },
    "Presentation Skills": {
        "Beginner": "https://www.coursera.org/learn/presentation-skills",
        "Intermediate": "https://www.coursera.org/specializations/public-speaking",
        "Advanced": "https://www.coursera.org/learn/public-speaking-capstone",
    },
    "Data Ethics": {
        "Beginner": "https://www.edx.org/learn/data-analysis/university-of-michigan-data-science-ethics",
        "Intermediate": "https://www.edx.org/learn/data-analysis/university-of-michigan-data-science-ethics",
        "Advanced": "https://www.edx.org/learn/data-analysis/university-of-michigan-data-science-ethics",
    },
    "Networking Fundamentals": {
        "Beginner": "https://www.coursera.org/learn/computer-networking",
        "Intermediate": "https://www.coursera.org/learn/computer-networking",
        "Advanced": "https://learn.microsoft.com/en-us/training/paths/azure-fundamentals/",
    },
    "Operating Systems": {
        "Beginner": "https://www.coursera.org/learn/os-power-user",
        "Intermediate": "https://www.coursera.org/learn/os-power-user",
        "Advanced": "https://learn.microsoft.com/en-us/training/paths/manage-devices-in-microsoft-intune/",
    },
    "Troubleshooting": {
        "Beginner": "https://www.coursera.org/learn/technical-support-fundamentals",
        "Intermediate": "https://www.coursera.org/learn/technical-support-fundamentals",
        "Advanced": "https://www.coursera.org/learn/system-administration-it-infrastructure-services/",
    },
    "Customer Support": {
        "Beginner": "https://www.coursera.org/learn/technical-support-fundamentals",
        "Intermediate": "https://academy.hubspot.com/courses/customer-service",
        "Advanced": "https://academy.hubspot.com/courses/customer-service",
    },
    "Cybersecurity Awareness": {
        "Beginner": "https://www.coursera.org/learn/it-security",
        "Intermediate": "https://www.coursera.org/learn/it-security",
        "Advanced": "https://owasp.org/www-project-top-ten/",
    },
    "Hardware Basics": {
        "Beginner": "https://www.coursera.org/learn/technical-support-fundamentals",
        "Intermediate": "https://www.comptia.org/certifications/a",
        "Advanced": "https://www.comptia.org/certifications/a",
    },
    "Cloud Fundamentals": {
        "Beginner": "https://learn.microsoft.com/en-us/training/paths/azure-fundamentals/",
        "Intermediate": "https://aws.amazon.com/training/classroom/aws-cloud-practitioner-essentials/",
        "Advanced": "https://www.coursera.org/learn/system-administration-it-infrastructure-services/",
    },
    "Ticketing Systems": {
        "Beginner": "https://www.atlassian.com/software/jira/service-management/tutorials",
        "Intermediate": "https://www.atlassian.com/software/jira/service-management/tutorials",
        "Advanced": "https://www.atlassian.com/software/jira/service-management/tutorials",
    },
    "Active Directory": {
        "Beginner": "https://learn.microsoft.com/en-us/training/modules/introduction-to-ad-ds/",
        "Intermediate": "https://learn.microsoft.com/en-us/training/modules/manage-security-active-directory/",
        "Advanced": "https://learn.microsoft.com/en-us/training/modules/troubleshoot-active-directory/",
    },
    "Technical Documentation": {
        "Beginner": "https://developers.google.com/tech-writing",
        "Intermediate": "https://developers.google.com/tech-writing",
        "Advanced": "https://developers.google.com/tech-writing",
    },
    "Backup and Recovery": {
        "Beginner": "https://learn.microsoft.com/en-us/windows-server/administration/windows-server-backup/windows-server-backup-overview",
        "Intermediate": "https://learn.microsoft.com/en-us/windows-server/administration/windows-server-backup/windows-server-backup-overview",
        "Advanced": "https://www.coursera.org/learn/system-administration-it-infrastructure-services/",
    },
    "Mobile Device Support": {
        "Beginner": "https://learn.microsoft.com/en-us/training/paths/manage-devices-in-microsoft-intune/",
        "Intermediate": "https://learn.microsoft.com/en-us/training/paths/manage-devices-in-microsoft-intune/",
        "Advanced": "https://learn.microsoft.com/en-us/training/paths/manage-devices-in-microsoft-intune/",
    },
    "Email Administration": {
        "Beginner": "https://learn.microsoft.com/en-us/training/paths/administer-exchange-online/",
        "Intermediate": "https://learn.microsoft.com/en-us/training/paths/administer-exchange-online/",
        "Advanced": "https://learn.microsoft.com/en-us/training/paths/administer-exchange-online/",
    },
    "Remote Support Tools": {
        "Beginner": "https://learn.microsoft.com/en-us/training/modules/configure-remote-management/",
        "Intermediate": "https://learn.microsoft.com/en-us/training/modules/configure-remote-management/",
        "Advanced": "https://learn.microsoft.com/en-us/training/modules/configure-remote-management/",
    },
    "IT Asset Management": {
        "Beginner": "https://www.itassetmanagement.net/itam-basics/",
        "Intermediate": "https://learn.microsoft.com/en-us/training/paths/manage-devices-in-microsoft-intune/",
        "Advanced": "https://learn.microsoft.com/en-us/training/paths/manage-devices-in-microsoft-intune/",
    },
}


class Command(BaseCommand):
    help = "Seeds internally maintained roles, skills, requirements, and learning resources."

    def handle(self, *args, **options):
        for role_name, role_data in ROLE_DATA.items():
            role, _ = JobRole.objects.update_or_create(
                name=role_name, defaults={"description": role_data["description"]}
            )
            for skill_name, required_level in role_data["skills"].items():
                skill, _ = Skill.objects.update_or_create(
                    name=skill_name,
                    defaults={"description": DESCRIPTIONS.get(skill_name, skill_name)},
                )
                RoleSkillRequirement.objects.update_or_create(
                    role=role,
                    skill=skill,
                    defaults={"required_level": required_level},
                )
                for difficulty in [
                    LearningResource.BEGINNER,
                    LearningResource.INTERMEDIATE,
                    LearningResource.ADVANCED,
                ]:
                    real_url = LEARNING_RESOURCES.get(skill_name, {}).get(difficulty)
                    fallback_url = f"https://example.com/learn/{skill_name.lower().replace(' ', '-')}/{difficulty.lower()}"
                    LearningResource.objects.update_or_create(
                        skill=skill,
                        title=f"{skill_name} {difficulty} Guide",
                        defaults={
                            "url": real_url or fallback_url,
                            "difficulty": difficulty,
                            "description": f"A curated {difficulty.lower()} resource for improving {skill_name}.",
                        },
                    )
        self.stdout.write(self.style.SUCCESS("Demo data seeded."))