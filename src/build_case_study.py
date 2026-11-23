from __future__ import annotations

import csv
import random
import sqlite3
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "crm_leads_raw.csv"
CLEAN_PATH = ROOT / "data" / "processed" / "clean_crm_leads.csv"
DB_PATH = ROOT / "data" / "processed" / "sales_pipeline.sqlite"
REPORT_DIR = ROOT / "reports"
SQL_PATH = ROOT / "sql" / "analysis_queries.sql"
REPORT_DATE = date(2026, 5, 9)
PROJECT_TITLE = "RevOps Pipeline Intelligence Platform"
AUTHOR = "Shridhar Sharma"


LEAD_SOURCES = ["Website", "Referral", "LinkedIn", "Webinar", "Cold Email", "Event", "Partner", "Paid Search"]
INDUSTRIES = ["Healthcare", "IT Services", "Manufacturing", "Education", "Real Estate", "Retail", "Financial Services", "SaaS"]
REGIONS = ["Chandigarh", "Mohali", "Delhi NCR", "Pune", "Bengaluru", "Hyderabad", "Mumbai", "Remote"]
COMPANY_SIZES = ["1-10", "11-50", "51-200", "201-500", "500+"]
SALES_REPS = ["Aarav Mehta", "Ananya Iyer", "Rohan Kapoor", "Simran Kaur", "Vikram Malhotra"]
STAGES = ["New", "Contacted", "Qualified", "Demo Scheduled", "Proposal", "Negotiation", "Won", "Lost", "Nurture"]
EMAIL_STATUSES = ["No Response", "Opened", "Replied", "Bounced", "Unsubscribed"]
LOST_REASONS = ["No Budget", "No Decision", "Bad Fit", "Chose Competitor", "Timing", ""]

STAGE_PROBABILITY = {
    "New": 0.08,
    "Contacted": 0.15,
    "Qualified": 0.32,
    "Demo Scheduled": 0.48,
    "Proposal": 0.64,
    "Negotiation": 0.78,
    "Won": 1.0,
    "Lost": 0.0,
    "Nurture": 0.18,
}

STAGE_RANK = {
    "New": 1,
    "Contacted": 2,
    "Nurture": 3,
    "Qualified": 4,
    "Demo Scheduled": 5,
    "Proposal": 6,
    "Negotiation": 7,
    "Lost": 8,
    "Won": 9,
}

TEXT_VARIANTS = {
    "Website": ["Website", "web site", "WEB", "Inbound Web"],
    "Referral": ["Referral", "referral", "Referred"],
    "LinkedIn": ["LinkedIn", "linkedin", "Linked In"],
    "Webinar": ["Webinar", "webinar", "Online Event"],
    "Cold Email": ["Cold Email", "cold email", "Outbound Email"],
    "Paid Search": ["Paid Search", "paid search", "Google Ads"],
    "IT Services": ["IT Services", "it services", "IT Svcs"],
    "SaaS": ["SaaS", "saas", "Software"],
    "New": ["New", "new", "Fresh Lead"],
    "Contacted": ["Contacted", "contacted", "Reached Out"],
    "Qualified": ["Qualified", "qualified", "Good Fit"],
    "Demo Scheduled": ["Demo Scheduled", "demo scheduled", "Demo Booked"],
    "Proposal": ["Proposal", "proposal", "Proposal Sent"],
    "Negotiation": ["Negotiation", "negotiation", "Decision Stage"],
    "Won": ["Won", "won", "Closed Won"],
    "Lost": ["Lost", "lost", "Closed Lost"],
    "Nurture": ["Nurture", "nurture", "Long Term"],
    "No Response": ["No Response", "no response", "No Reply"],
    "Opened": ["Opened", "opened", "Email Opened"],
    "Replied": ["Replied", "replied", "Response"],
    "Bounced": ["Bounced", "bounced", "Invalid Email"],
}


def ensure_dirs() -> None:
    for path in [RAW_PATH.parent, CLEAN_PATH.parent, DB_PATH.parent, REPORT_DIR, SQL_PATH.parent]:
        path.mkdir(parents=True, exist_ok=True)


def messy_text(value: str, chance: float = 0.16) -> str:
    if random.random() < 0.025:
        return ""
    if random.random() < chance and value in TEXT_VARIANTS:
        return random.choice(TEXT_VARIANTS[value])
    return value


def messy_date(value: date | None) -> str:
    if value is None:
        return ""
    if random.random() < 0.025:
        return ""
    return value.strftime(random.choice(["%Y-%m-%d", "%d/%m/%Y", "%d %b %Y"]))


def messy_money(value: float) -> str:
    if random.random() < 0.035:
        return ""
    if random.random() < 0.02:
        return f"-{value:.2f}"
    if random.random() < 0.12:
        return f"₹ {value:,.2f}"
    return f"{value:.2f}"


def messy_int(value: int) -> str:
    if random.random() < 0.03:
        return ""
    if random.random() < 0.02:
        return str(value * -1)
    return str(value)


def messy_bool(value: bool) -> str:
    if value:
        return random.choice(["yes", "Y", "true", "1", "Booked"])
    return random.choice(["no", "N", "false", "0", ""])


def base_deal_value(company_size: str, industry: str) -> float:
    size_multiplier = {
        "1-10": 0.65,
        "11-50": 1.0,
        "51-200": 1.55,
        "201-500": 2.2,
        "500+": 3.1,
    }[company_size]
    industry_multiplier = {
        "Healthcare": 1.35,
        "IT Services": 1.15,
        "Manufacturing": 1.25,
        "Education": 0.9,
        "Real Estate": 1.1,
        "Retail": 0.8,
        "Financial Services": 1.4,
        "SaaS": 1.7,
    }[industry]
    return random.uniform(40000, 200000) * size_multiplier * industry_multiplier


def generate_raw_dataset(record_count: int = 760) -> list[dict[str, str]]:
    random.seed(41)
    rows: list[dict[str, str]] = []
    first_names = ["Rahul", "Neha", "Amit", "Pooja", "Karan", "Ishita", "Arjun", "Meera", "Sanjay", "Priya"]
    last_names = ["Gupta", "Verma", "Singh", "Reddy", "Nair", "Joshi", "Bansal", "Chopra", "Khanna", "Bhatia"]
    company_words = ["Trident", "Himalaya", "Veda", "Apex", "Nexora", "Orbit", "Sapphire", "Kestrel"]
    company_types = ["Technologies", "Solutions", "Systems", "Labs", "Consulting", "Industries", "Enterprises", "Services"]
    start_date = date(2026, 1, 2)

    for index in range(record_count):
        source = random.choices(LEAD_SOURCES, weights=[21, 17, 16, 13, 11, 8, 7, 7], k=1)[0]
        industry = random.choices(INDUSTRIES, weights=[14, 18, 9, 10, 14, 12, 7, 16], k=1)[0]
        region = random.choice(REGIONS)
        company_size = random.choices(COMPANY_SIZES, weights=[20, 32, 25, 14, 9], k=1)[0]
        stage = random.choices(STAGES, weights=[12, 17, 19, 12, 11, 7, 9, 7, 6], k=1)[0]
        rep = random.choice(SALES_REPS)
        created_date = start_date + timedelta(days=random.randint(0, 118))

        stage_rank = STAGE_RANK[stage]
        last_contact_date = None if stage == "New" and random.random() < 0.5 else created_date + timedelta(days=random.randint(0, 38))
        if last_contact_date and last_contact_date > REPORT_DATE:
            last_contact_date = REPORT_DATE - timedelta(days=random.randint(0, 4))

        next_followup_date = None
        if stage not in {"Won", "Lost"}:
            if random.random() < 0.14:
                next_followup_date = None
            else:
                anchor = last_contact_date or created_date
                next_followup_date = anchor + timedelta(days=random.randint(2, 21))
                if random.random() < 0.32:
                    next_followup_date = REPORT_DATE - timedelta(days=random.randint(1, 18))

        deal_value = base_deal_value(company_size, industry) * random.uniform(0.78, 1.35)
        probability = STAGE_PROBABILITY[stage] + random.uniform(-0.04, 0.04)
        probability = min(1.0, max(0.0, probability))
        meeting_count = max(0, stage_rank - 2 + random.randint(-1, 2))
        if stage in {"New", "Contacted"}:
            meeting_count = random.choice([0, 0, 1])
        demo_booked = stage_rank >= STAGE_RANK["Demo Scheduled"] and stage not in {"Lost"}
        proposal_sent = stage_rank >= STAGE_RANK["Proposal"] and stage not in {"Lost"}
        email_status = random.choices(EMAIL_STATUSES, weights=[38, 26, 24, 7, 5], k=1)[0]
        lost_reason = random.choice(LOST_REASONS[:-1]) if stage == "Lost" else ""
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        company = f"{random.choice(company_words)} {random.choice(company_types)}"

        rows.append(
            {
                "lead_id": f"LD-{10000 + index}",
                "created_date": messy_date(created_date),
                "lead_source": messy_text(source),
                "industry": messy_text(industry, 0.1),
                "region": messy_text(region, 0.06),
                "company_size": company_size if random.random() > 0.03 else "",
                "company_name": company,
                "contact_name": name,
                "sales_rep": rep if random.random() > 0.03 else "",
                "stage": messy_text(stage),
                "deal_value": messy_money(deal_value),
                "probability": f"{probability:.2f}" if random.random() > 0.04 else "",
                "last_contact_date": messy_date(last_contact_date),
                "next_followup_date": messy_date(next_followup_date),
                "email_status": messy_text(email_status),
                "demo_booked": messy_bool(demo_booked),
                "proposal_sent": messy_bool(proposal_sent),
                "meeting_count": messy_int(meeting_count),
                "lost_reason": messy_text(lost_reason, 0.08),
            }
        )

    for row in random.sample(rows, 24):
        duplicate = row.copy()
        duplicate["stage"] = messy_text(random.choice(["Qualified", "Proposal", "Negotiation", "Won"]))
        duplicate["last_contact_date"] = messy_date(REPORT_DATE - timedelta(days=random.randint(0, 15)))
        duplicate["next_followup_date"] = messy_date(REPORT_DATE + timedelta(days=random.randint(1, 8)))
        rows.append(duplicate)

    random.shuffle(rows)
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value: str, default: str = "Unknown") -> str:
    cleaned = " ".join((value or "").strip().replace("-", " ").split()).title()
    if not cleaned:
        return default
    aliases = {
        "Web Site": "Website",
        "Web": "Website",
        "Inbound Web": "Website",
        "Referred": "Referral",
        "Linkedin": "LinkedIn",
        "Linked In": "LinkedIn",
        "Online Event": "Webinar",
        "Outbound Email": "Cold Email",
        "Google Ads": "Paid Search",
        "It Services": "IT Services",
        "It Svcs": "IT Services",
        "Delhi Ncr": "Delhi NCR",
        "Software": "SaaS",
        "Saas": "SaaS",
        "Fresh Lead": "New",
        "Reached Out": "Contacted",
        "Good Fit": "Qualified",
        "Demo Booked": "Demo Scheduled",
        "Proposal Sent": "Proposal",
        "Decision Stage": "Negotiation",
        "Closed Won": "Won",
        "Closed Lost": "Lost",
        "Long Term": "Nurture",
        "No Reply": "No Response",
        "Email Opened": "Opened",
        "Response": "Replied",
        "Invalid Email": "Bounced",
    }
    return aliases.get(cleaned, cleaned)


def parse_date(value: str) -> date | None:
    value = (value or "").strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d %b %Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def parse_float(value: str) -> float | None:
    try:
        parsed = float((value or "").strip().replace("₹", "").replace(",", ""))
    except ValueError:
        return None
    return parsed if parsed >= 0 else None


def parse_int(value: str) -> int:
    try:
        parsed = int(float((value or "").strip()))
    except ValueError:
        return 0
    return parsed if parsed >= 0 else 0


def parse_bool(value: str) -> bool:
    return (value or "").strip().lower() in {"yes", "y", "true", "1", "booked"}


def score_lead(row: dict) -> int:
    stage = row["stage"]
    stage_score = {
        "New": 12,
        "Contacted": 22,
        "Qualified": 45,
        "Demo Scheduled": 61,
        "Proposal": 73,
        "Negotiation": 86,
        "Won": 100,
        "Lost": 0,
        "Nurture": 28,
    }.get(stage, 10)
    source_bonus = {"Referral": 9, "LinkedIn": 6, "Webinar": 5, "Website": 4, "Partner": 4}.get(row["lead_source"], 0)
    email_bonus = {"Replied": 8, "Opened": 4, "No Response": 0, "Bounced": -8, "Unsubscribed": -10}.get(row["email_status"], 0)
    meeting_bonus = min(10, row["meeting_count"] * 2)
    value_bonus = 10 if row["deal_value"] >= 300000 else 6 if row["deal_value"] >= 150000 else 2
    recency_bonus = 0
    if isinstance(row["days_since_contact"], int):
        if row["days_since_contact"] <= 7:
            recency_bonus = 7
        elif row["days_since_contact"] <= 14:
            recency_bonus = 3
        elif row["days_since_contact"] > 30:
            recency_bonus = -8
    score = stage_score + source_bonus + email_bonus + meeting_bonus + value_bonus + recency_bonus
    if row["followup_status"] == "Overdue":
        score += 5
    return max(0, min(100, round(score)))


def recommended_action(row: dict) -> str:
    stage = row["stage"]
    status = row["followup_status"]
    if stage in {"Won", "Lost"}:
        return "Closed - review for learning"
    if status == "Overdue":
        return "Follow up today"
    if status == "Missing Follow-Up":
        return "Set next follow-up date"
    if status == "Due Today":
        return "Call or email today"
    if stage in {"Proposal", "Negotiation"}:
        return "Confirm decision timeline"
    if stage == "New":
        return "Qualify lead"
    if stage == "Nurture":
        return "Send nurture sequence"
    return "Continue scheduled follow-up"


def clean_dataset(rows: list[dict[str, str]]) -> list[dict]:
    deduped: dict[str, dict] = {}
    for raw in rows:
        created = parse_date(raw["created_date"]) or REPORT_DATE
        last_contact = parse_date(raw["last_contact_date"])
        next_followup = parse_date(raw["next_followup_date"])
        stage = normalize_text(raw["stage"], "New")
        if stage not in STAGE_RANK:
            stage = "New"
        probability = parse_float(raw["probability"])
        if probability is None:
            probability = STAGE_PROBABILITY[stage]
        probability = max(0.0, min(1.0, probability))
        deal_value = parse_float(raw["deal_value"]) or 0.0
        days_since_contact = (REPORT_DATE - last_contact).days if last_contact else None
        days_to_followup = (next_followup - REPORT_DATE).days if next_followup else None

        if stage in {"Won", "Lost"}:
            followup_status = "Closed"
        elif next_followup is None:
            followup_status = "Missing Follow-Up"
        elif days_to_followup < 0:
            followup_status = "Overdue"
        elif days_to_followup == 0:
            followup_status = "Due Today"
        elif days_to_followup <= 7:
            followup_status = "Due This Week"
        else:
            followup_status = "Scheduled"

        clean = {
            "lead_id": raw["lead_id"].strip(),
            "created_date": created.isoformat(),
            "lead_source": normalize_text(raw["lead_source"], "Unknown"),
            "industry": normalize_text(raw["industry"], "Unknown"),
            "region": normalize_text(raw["region"], "Unknown"),
            "company_size": raw["company_size"].strip() or "Unknown",
            "company_name": raw["company_name"].strip() or "Unknown Company",
            "contact_name": raw["contact_name"].strip() or "Unknown Contact",
            "sales_rep": raw["sales_rep"].strip() or "Unassigned",
            "stage": stage,
            "deal_value": round(deal_value, 2),
            "probability": round(probability, 2),
            "expected_value": round(deal_value * probability, 2),
            "last_contact_date": last_contact.isoformat() if last_contact else "",
            "next_followup_date": next_followup.isoformat() if next_followup else "",
            "days_since_contact": days_since_contact if days_since_contact is not None else "",
            "days_to_followup": days_to_followup if days_to_followup is not None else "",
            "followup_status": followup_status,
            "email_status": normalize_text(raw["email_status"], "Unknown"),
            "demo_booked": parse_bool(raw["demo_booked"]),
            "proposal_sent": parse_bool(raw["proposal_sent"]),
            "meeting_count": parse_int(raw["meeting_count"]),
            "lost_reason": normalize_text(raw["lost_reason"], "") if stage == "Lost" else "",
        }
        clean["lead_score"] = score_lead(clean)
        clean["priority"] = (
            "Closed"
            if stage in {"Won", "Lost"}
            else "High"
            if clean["lead_score"] >= 75
            else "Medium"
            if clean["lead_score"] >= 55
            else "Low"
        )
        clean["recommended_action"] = recommended_action(clean)
        current = deduped.get(clean["lead_id"])
        if current is None:
            deduped[clean["lead_id"]] = clean
            continue
        current_rank = STAGE_RANK[current["stage"]]
        new_rank = STAGE_RANK[clean["stage"]]
        current_contact = current["last_contact_date"] or "0000-00-00"
        new_contact = clean["last_contact_date"] or "0000-00-00"
        if (new_rank, new_contact) >= (current_rank, current_contact):
            deduped[clean["lead_id"]] = clean
    return sorted(deduped.values(), key=lambda item: item["lead_id"])


def load_sqlite(rows: list[dict]) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    columns = list(rows[0])
    column_sql = ", ".join(f"{column} TEXT" for column in columns)
    connection.execute(f"CREATE TABLE crm_leads ({column_sql})")
    placeholders = ", ".join("?" for _ in columns)
    connection.executemany(
        f"INSERT INTO crm_leads ({', '.join(columns)}) VALUES ({placeholders})",
        [[str(row[column]) for column in columns] for row in rows],
    )
    connection.commit()
    connection.close()


def query_rows(sql: str) -> list[dict]:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    rows = [dict(row) for row in connection.execute(sql)]
    connection.close()
    return rows


def export_analysis_tables() -> dict[str, list[dict]]:
    def scalar(sql: str):
        return query_rows(sql)[0]["value"]

    total_leads = scalar("SELECT COUNT(*) AS value FROM crm_leads")
    active_pipeline = scalar("SELECT ROUND(SUM(CAST(deal_value AS REAL)), 2) AS value FROM crm_leads WHERE stage NOT IN ('Won','Lost')")
    expected_pipeline = scalar("SELECT ROUND(SUM(CAST(expected_value AS REAL)), 2) AS value FROM crm_leads WHERE stage NOT IN ('Won','Lost')")
    won_revenue = scalar("SELECT ROUND(SUM(CAST(deal_value AS REAL)), 2) AS value FROM crm_leads WHERE stage = 'Won'")
    overdue_followups = scalar("SELECT COUNT(*) AS value FROM crm_leads WHERE followup_status = 'Overdue'")
    high_priority_leads = scalar("SELECT COUNT(*) AS value FROM crm_leads WHERE priority = 'High' AND stage NOT IN ('Won','Lost')")

    tables = {
        "pipeline_kpi_summary": [
            {
                "metric": "Total leads cleaned",
                "value": total_leads,
            },
            {
                "metric": "Active pipeline value",
                "value": money(active_pipeline),
            },
            {
                "metric": "Expected pipeline value",
                "value": money(expected_pipeline),
            },
            {
                "metric": "Won revenue",
                "value": money(won_revenue),
            },
            {
                "metric": "Overdue follow-ups",
                "value": overdue_followups,
            },
            {
                "metric": "High-priority active leads",
                "value": high_priority_leads,
            },
        ],
        "followup_queue": query_rows(
            """
            SELECT lead_id, company_name, contact_name, sales_rep, stage, lead_source,
                   deal_value, expected_value, lead_score, priority, followup_status,
                   next_followup_date, recommended_action
            FROM crm_leads
            WHERE stage NOT IN ('Won','Lost')
              AND followup_status IN ('Overdue', 'Due Today', 'Due This Week', 'Missing Follow-Up')
            ORDER BY
              CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
              CASE followup_status WHEN 'Overdue' THEN 1 WHEN 'Due Today' THEN 2 WHEN 'Missing Follow-Up' THEN 3 ELSE 4 END,
              CAST(expected_value AS REAL) DESC
            LIMIT 80
            """
        ),
        "rep_performance": query_rows(
            """
            SELECT sales_rep,
                   COUNT(*) AS total_leads,
                   ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(deal_value AS REAL) ELSE 0 END), 2) AS active_pipeline,
                   ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(expected_value AS REAL) ELSE 0 END), 2) AS expected_pipeline,
                   ROUND(SUM(CASE WHEN stage = 'Won' THEN CAST(deal_value AS REAL) ELSE 0 END), 2) AS won_revenue,
                   SUM(CASE WHEN followup_status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_followups,
                   SUM(CASE WHEN priority = 'High' AND stage NOT IN ('Won','Lost') THEN 1 ELSE 0 END) AS high_priority_leads,
                   ROUND(AVG(CAST(lead_score AS REAL)), 1) AS avg_lead_score
            FROM crm_leads
            GROUP BY sales_rep
            ORDER BY expected_pipeline DESC
            """
        ),
        "source_performance": query_rows(
            """
            SELECT lead_source,
                   COUNT(*) AS total_leads,
                   SUM(CASE WHEN stage IN ('Qualified','Demo Scheduled','Proposal','Negotiation','Won') THEN 1 ELSE 0 END) AS qualified_or_better,
                   ROUND(100.0 * SUM(CASE WHEN stage = 'Won' THEN 1 ELSE 0 END) / COUNT(*), 1) AS win_rate_pct,
                   ROUND(AVG(CAST(deal_value AS REAL)), 2) AS avg_deal_value,
                   ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(expected_value AS REAL) ELSE 0 END), 2) AS expected_pipeline,
                   SUM(CASE WHEN followup_status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_followups
            FROM crm_leads
            GROUP BY lead_source
            ORDER BY expected_pipeline DESC
            """
        ),
        "stage_conversion": query_rows(
            """
            SELECT stage,
                   COUNT(*) AS lead_count,
                   ROUND(SUM(CAST(deal_value AS REAL)), 2) AS total_deal_value,
                   ROUND(SUM(CAST(expected_value AS REAL)), 2) AS expected_value,
                   ROUND(AVG(CAST(lead_score AS REAL)), 1) AS avg_lead_score
            FROM crm_leads
            GROUP BY stage
            ORDER BY
              CASE stage
                WHEN 'New' THEN 1
                WHEN 'Contacted' THEN 2
                WHEN 'Nurture' THEN 3
                WHEN 'Qualified' THEN 4
                WHEN 'Demo Scheduled' THEN 5
                WHEN 'Proposal' THEN 6
                WHEN 'Negotiation' THEN 7
                WHEN 'Won' THEN 8
                WHEN 'Lost' THEN 9
                ELSE 10
              END
            """
        ),
        "industry_pipeline": query_rows(
            """
            SELECT industry,
                   COUNT(*) AS total_leads,
                   ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(deal_value AS REAL) ELSE 0 END), 2) AS active_pipeline,
                   ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(expected_value AS REAL) ELSE 0 END), 2) AS expected_pipeline,
                   SUM(CASE WHEN priority = 'High' AND stage NOT IN ('Won','Lost') THEN 1 ELSE 0 END) AS high_priority_leads,
                   ROUND(AVG(CAST(deal_value AS REAL)), 2) AS avg_deal_value
            FROM crm_leads
            GROUP BY industry
            ORDER BY expected_pipeline DESC
            """
        ),
    }
    for name, rows in tables.items():
        write_csv(ROOT / "data" / "processed" / f"{name}.csv", rows)
    return tables


def write_sql_file() -> None:
    SQL_PATH.write_text(
        f"""-- {PROJECT_TITLE}
-- Author: {AUTHOR}
-- SQL queries used to analyze cleaned CRM lead data.

-- KPI summary
SELECT
  COUNT(*) AS total_leads,
  ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(deal_value AS REAL) ELSE 0 END), 2) AS active_pipeline,
  ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(expected_value AS REAL) ELSE 0 END), 2) AS expected_pipeline,
  ROUND(SUM(CASE WHEN stage = 'Won' THEN CAST(deal_value AS REAL) ELSE 0 END), 2) AS won_revenue,
  SUM(CASE WHEN followup_status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_followups,
  SUM(CASE WHEN priority = 'High' AND stage NOT IN ('Won','Lost') THEN 1 ELSE 0 END) AS high_priority_active_leads
FROM crm_leads;

-- Follow-up queue
SELECT lead_id, company_name, contact_name, sales_rep, stage, lead_source,
       deal_value, expected_value, lead_score, priority, followup_status,
       next_followup_date, recommended_action
FROM crm_leads
WHERE stage NOT IN ('Won','Lost')
  AND followup_status IN ('Overdue', 'Due Today', 'Due This Week', 'Missing Follow-Up')
ORDER BY
  CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
  CASE followup_status WHEN 'Overdue' THEN 1 WHEN 'Due Today' THEN 2 WHEN 'Missing Follow-Up' THEN 3 ELSE 4 END,
  CAST(expected_value AS REAL) DESC;

-- Sales rep performance
SELECT sales_rep,
       COUNT(*) AS total_leads,
       ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(deal_value AS REAL) ELSE 0 END), 2) AS active_pipeline,
       ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(expected_value AS REAL) ELSE 0 END), 2) AS expected_pipeline,
       ROUND(SUM(CASE WHEN stage = 'Won' THEN CAST(deal_value AS REAL) ELSE 0 END), 2) AS won_revenue,
       SUM(CASE WHEN followup_status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_followups,
       SUM(CASE WHEN priority = 'High' AND stage NOT IN ('Won','Lost') THEN 1 ELSE 0 END) AS high_priority_leads,
       ROUND(AVG(CAST(lead_score AS REAL)), 1) AS avg_lead_score
FROM crm_leads
GROUP BY sales_rep
ORDER BY expected_pipeline DESC;

-- Lead source performance
SELECT lead_source,
       COUNT(*) AS total_leads,
       SUM(CASE WHEN stage IN ('Qualified','Demo Scheduled','Proposal','Negotiation','Won') THEN 1 ELSE 0 END) AS qualified_or_better,
       ROUND(100.0 * SUM(CASE WHEN stage = 'Won' THEN 1 ELSE 0 END) / COUNT(*), 1) AS win_rate_pct,
       ROUND(AVG(CAST(deal_value AS REAL)), 2) AS avg_deal_value,
       ROUND(SUM(CASE WHEN stage NOT IN ('Won','Lost') THEN CAST(expected_value AS REAL) ELSE 0 END), 2) AS expected_pipeline,
       SUM(CASE WHEN followup_status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_followups
FROM crm_leads
GROUP BY lead_source
ORDER BY expected_pipeline DESC;
""",
        encoding="utf-8",
    )


def money(value: float | int | str | None) -> str:
    if value is None or value == "":
        return "\u20b90"
    number = float(value)
    sign = "-" if number < 0 else ""
    whole = f"{abs(number):.0f}"
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:])
            head = head[:-2]
        if head:
            groups.insert(0, head)
        whole = ",".join(groups + [tail])
    return f"{sign}\u20b9{whole}"


def money_short(value: float | int | str | None) -> str:
    number = float(value or 0)
    if abs(number) >= 1e7:
        return f"\u20b9{number / 1e7:.2f} Cr"
    if abs(number) >= 1e5:
        return f"\u20b9{number / 1e5:.2f} L"
    return money(number)


DASHBOARD_CSS = """
    :root {
      --navy: #0b1f3a;
      --navy-2: #14305a;
      --ink: #101828;
      --muted: #667085;
      --line: #e4e7ec;
      --bg: #f4f6fa;
      --panel: #ffffff;
      --blue: #1d4ed8;
      --teal: #0e7490;
      --green: #067647;
      --amber: #b54708;
      --red: #b42318;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", Inter, -apple-system, Roboto, Arial, sans-serif;
      color: var(--ink);
      background: var(--bg);
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }
    .topbar { background: linear-gradient(90deg, var(--navy), var(--navy-2)); color: #fff; position: sticky; top: 0; z-index: 10; }
    .topbar-inner { max-width: 1280px; margin: 0 auto; padding: 12px 28px; display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
    .brand { display: flex; align-items: center; gap: 12px; }
    .logo { width: 34px; height: 34px; border-radius: 8px; background: #2f6bff; display: grid; place-items: center; font-weight: 800; font-size: 13px; letter-spacing: .5px; }
    .brand-name { font-size: 15px; font-weight: 700; }
    .brand-sub { font-size: 12px; color: #a9b8d3; }
    .meta { display: flex; gap: 8px; flex-wrap: wrap; }
    .chip { font-size: 12px; padding: 4px 10px; border-radius: 999px; background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.16); color: #dbe5f7; }
    .hero, main { max-width: 1280px; margin: 0 auto; padding-left: 28px; padding-right: 28px; }
    .hero { padding-top: 28px; }
    .hero h1 { margin: 0; font-size: 26px; letter-spacing: -.01em; }
    .hero p { margin: 6px 0 0; color: var(--muted); max-width: 820px; }
    main { padding-top: 20px; padding-bottom: 40px; }
    .kpis { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 14px; }
    .kpi { background: var(--panel); border: 1px solid var(--line); border-top: 3px solid var(--blue); border-radius: 10px; padding: 16px 18px; box-shadow: 0 1px 2px rgba(16,24,40,.05); }
    .kpi.teal { border-top-color: var(--teal); }
    .kpi.green { border-top-color: var(--green); }
    .kpi.amber { border-top-color: var(--amber); }
    .kpi.red { border-top-color: var(--red); }
    .kpi-label { font-size: 11px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }
    .kpi-value { font-size: 26px; font-weight: 700; margin: 6px 0 2px; font-variant-numeric: tabular-nums; }
    .kpi-note { font-size: 12px; color: var(--muted); }
    .row { display: grid; gap: 16px; margin-top: 16px; }
    .row.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .card { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 18px 20px; min-width: 0; box-shadow: 0 1px 2px rgba(16,24,40,.05); }
    .card-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 14px; }
    .card h2 { margin: 0; font-size: 15px; font-weight: 700; }
    .card-sub { font-size: 12px; color: var(--muted); }
    .search { border: 1px solid var(--line); border-radius: 8px; padding: 7px 10px; font-size: 13px; min-width: 220px; font-family: inherit; }
    .search:focus { outline: 2px solid #bfd1ff; border-color: #93b0ff; }
    .bar-row { display: grid; grid-template-columns: 140px 1fr 120px; align-items: center; gap: 12px; padding: 6px 0; font-size: 13px; }
    .bar-label { color: #344054; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .bar-track { height: 10px; background: #eef2f6; border-radius: 999px; overflow: hidden; }
    .bar-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #4f83ff, #1d4ed8); }
    .bar-fill.won { background: linear-gradient(90deg, #34b27b, #067647); }
    .bar-fill.lost { background: linear-gradient(90deg, #f08a82, #b42318); }
    .bar-value { text-align: right; font-weight: 600; font-variant-numeric: tabular-nums; }
    .bar-value small { display: block; font-weight: 400; color: var(--muted); font-size: 11px; }
    .table-wrap { overflow: auto; }
    .table-wrap.tall { max-height: 470px; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    table.wide { min-width: 960px; }
    th, td { border-bottom: 1px solid var(--line); padding: 10px 12px; text-align: left; vertical-align: top; overflow-wrap: anywhere; }
    th { position: sticky; top: 0; background: #f9fafb; color: #475467; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .04em; white-space: nowrap; }
    td.num, th.num { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
    td.nowrap { white-space: nowrap; }
    tbody tr:hover { background: #f9fafb; }
    .badge { display: inline-block; border-radius: 999px; padding: 2px 9px; font-size: 12px; font-weight: 600; white-space: nowrap; background: #eef2f6; color: #344054; }
    .badge-high, .badge-overdue { background: #fee4e2; color: var(--red); }
    .badge-medium, .badge-due-today, .badge-missing-follow-up { background: #fef0c7; color: var(--amber); }
    .badge-low, .badge-scheduled { background: #d1fadf; color: var(--green); }
    .badge-due-this-week { background: #dbe7ff; color: var(--blue); }
    .insights { margin: 0; padding-left: 18px; color: #344054; font-size: 14px; }
    .insights li { margin-bottom: 8px; }
    .note { border-left: 4px solid var(--blue); background: #eef4ff; padding: 12px 14px; margin-top: 14px; font-size: 14px; color: #344054; border-radius: 0 8px 8px 0; }
    footer { max-width: 1280px; margin: 0 auto; padding: 0 28px 32px; color: var(--muted); font-size: 12px; }
    @media (max-width: 1100px) {
      .kpis { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    }
    @media (max-width: 900px) {
      .row.two { grid-template-columns: 1fr; }
      .hero, main, .topbar-inner, footer { padding-left: 16px; padding-right: 16px; }
      .bar-row { grid-template-columns: 96px 1fr 96px; }
      .search { min-width: 0; width: 100%; }
    }
    @media (max-width: 560px) {
      .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
"""

DASHBOARD_JS = """
    document.getElementById('queue-filter').addEventListener('input', function (event) {
      var query = event.target.value.toLowerCase();
      document.querySelectorAll('#queue-table tbody tr').forEach(function (row) {
        row.style.display = row.textContent.toLowerCase().indexOf(query) > -1 ? '' : 'none';
      });
    });
"""


def write_dashboard(tables: dict[str, list[dict]]) -> None:
    rep_rows = tables["rep_performance"]
    stage_rows = tables["stage_conversion"]
    source_rows = tables["source_performance"]
    industry_rows = tables["industry_pipeline"]
    queue_rows = tables["followup_queue"][:25]

    total_leads = sum(int(row["total_leads"]) for row in rep_rows)
    active_pipeline = sum(float(row["active_pipeline"]) for row in rep_rows)
    expected_pipeline = sum(float(row["expected_pipeline"]) for row in rep_rows)
    won_revenue = sum(float(row["won_revenue"]) for row in rep_rows)
    overdue = sum(int(row["overdue_followups"]) for row in rep_rows)
    high_priority = sum(int(row["high_priority_leads"]) for row in rep_rows)
    active_count = sum(int(row["lead_count"]) for row in stage_rows if row["stage"] not in ("Won", "Lost"))
    won_count = sum(int(row["lead_count"]) for row in stage_rows if row["stage"] == "Won")
    weighted_pct = expected_pipeline / active_pipeline * 100 if active_pipeline else 0
    overdue_pct = overdue / active_count * 100 if active_count else 0
    top_source, top_rep, top_industry = source_rows[0], rep_rows[0], industry_rows[0]

    kpi_cards = [
        ("Total Leads", f"{total_leads:,}", "Deduplicated CRM records", "teal"),
        ("Active Pipeline", money_short(active_pipeline), f"{active_count:,} open opportunities", ""),
        ("Expected Pipeline", money_short(expected_pipeline), f"Probability-weighted, {weighted_pct:.0f}% of active", ""),
        ("Won Revenue", money_short(won_revenue), f"{won_count:,} deals closed won", "green"),
        ("Overdue Follow-Ups", f"{overdue:,}", f"{overdue_pct:.0f}% of open leads", "red"),
        ("High-Priority Leads", f"{high_priority:,}", "Lead score of 75 or above", "amber"),
    ]
    kpi_html = "".join(
        f'<div class="kpi {accent}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>'
        for label, value, note, accent in kpi_cards
    )

    def bar_chart(rows: list[dict], label_key: str, value_key: str, count_key: str) -> str:
        peak = max((float(row[value_key]) for row in rows), default=0) or 1
        out = ""
        for row in rows:
            value = float(row[value_key])
            fill = str(row[label_key]).lower() if str(row[label_key]) in ("Won", "Lost") else ""
            out += (
                f'<div class="bar-row"><div class="bar-label" title="{escape(str(row[label_key]))}">{escape(str(row[label_key]))}</div>'
                f'<div class="bar-track"><div class="bar-fill {fill}" style="width:{value / peak * 100:.1f}%"></div></div>'
                f'<div class="bar-value">{money_short(value)}<small>{int(row[count_key]):,} leads</small></div></div>'
            )
        return out

    def cell(value, kind: str) -> str:
        if kind == "money":
            return f'<td class="num">{money(value)}</td>'
        if kind == "pct":
            return f'<td class="num">{float(value):.1f}%</td>'
        if kind == "num":
            number = float(value)
            text = f"{number:,.0f}" if number.is_integer() else f"{number:,.1f}"
            return f'<td class="num">{text}</td>'
        if kind == "badge":
            text = escape(str(value))
            return f'<td><span class="badge badge-{text.lower().replace(" ", "-")}">{text}</span></td>'
        if kind == "nowrap":
            return f'<td class="nowrap">{escape(str(value))}</td>'
        return f"<td>{escape(str(value))}</td>"

    def table(columns: list[tuple[str, str, str]], rows: list[dict], table_id: str = "", wide: bool = False) -> str:
        head = "".join(
            f'<th class="{"num" if kind in ("money", "pct", "num") else ""}">{label}</th>'
            for _, label, kind in columns
        )
        body = "".join(
            "<tr>" + "".join(cell(row.get(key, ""), kind) for key, _, kind in columns) + "</tr>"
            for row in rows
        )
        id_attr = f' id="{table_id}"' if table_id else ""
        wide_class = ' class="wide"' if wide else ""
        return f'<table{id_attr}{wide_class}><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'

    queue_cols = [
        ("lead_id", "Lead ID", "nowrap"),
        ("company_name", "Company", "text"),
        ("sales_rep", "Sales Rep", "text"),
        ("stage", "Stage", "text"),
        ("expected_value", "Expected Value", "money"),
        ("lead_score", "Score", "num"),
        ("priority", "Priority", "badge"),
        ("followup_status", "Follow-Up", "badge"),
        ("recommended_action", "Recommended Action", "text"),
    ]
    rep_cols = [
        ("sales_rep", "Sales Rep", "text"),
        ("total_leads", "Leads", "num"),
        ("expected_pipeline", "Expected Pipeline", "money"),
        ("won_revenue", "Won Revenue", "money"),
        ("overdue_followups", "Overdue", "num"),
        ("high_priority_leads", "High Priority", "num"),
        ("avg_lead_score", "Avg Score", "num"),
    ]

    insights = [
        f"{escape(str(top_source['lead_source']))} is the strongest lead source with {money_short(top_source['expected_pipeline'])} in expected pipeline.",
        f"{escape(str(top_rep['sales_rep']))} owns the largest expected pipeline at {money_short(top_rep['expected_pipeline'])}.",
        f"{escape(str(top_industry['industry']))} is the highest-value industry segment at {money_short(top_industry['expected_pipeline'])}.",
        f"{overdue:,} open leads ({overdue_pct:.0f}%) have an overdue follow-up and need immediate attention.",
    ]
    insights_html = "".join(f"<li>{item}</li>" for item in insights)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{PROJECT_TITLE} | Sales Pipeline Dashboard</title>
  <style>{DASHBOARD_CSS}</style>
</head>
<body>
  <div class="topbar">
    <div class="topbar-inner">
      <div class="brand">
        <div class="logo">RP</div>
        <div>
          <div class="brand-name">{PROJECT_TITLE}</div>
          <div class="brand-sub">Revenue Operations Analytics</div>
        </div>
      </div>
      <div class="meta">
        <span class="chip">Data as of {REPORT_DATE:%d %b %Y}</span>
        <span class="chip">Synthetic dataset</span>
        <span class="chip">Prepared by {AUTHOR}</span>
      </div>
    </div>
  </div>

  <div class="hero">
    <h1>Sales Pipeline &amp; Follow-Up Overview</h1>
    <p>Weekly sales operations view of pipeline value, lead quality, follow-up risk and rep workload across {total_leads:,} cleaned and deduplicated CRM leads.</p>
  </div>

  <main>
    <section class="kpis">{kpi_html}</section>

    <section class="row two">
      <div class="card">
        <div class="card-head"><h2>Deal Value by Stage</h2><span class="card-sub">Total deal value and lead count</span></div>
        {bar_chart(stage_rows, "stage", "total_deal_value", "lead_count")}
      </div>
      <div class="card">
        <div class="card-head"><h2>Expected Pipeline by Lead Source</h2><span class="card-sub">Probability-weighted, open leads</span></div>
        {bar_chart(source_rows, "lead_source", "expected_pipeline", "total_leads")}
      </div>
    </section>

    <section class="row">
      <div class="card">
        <div class="card-head">
          <div><h2>Priority Follow-Up Queue</h2><span class="card-sub">Top {len(queue_rows)} leads ranked by priority, follow-up status and expected value</span></div>
          <input id="queue-filter" class="search" type="search" placeholder="Filter by company, rep, stage..." aria-label="Filter follow-up queue">
        </div>
        <div class="table-wrap tall">{table(queue_cols, queue_rows, "queue-table", wide=True)}</div>
      </div>
    </section>

    <section class="row">
      <div class="card">
        <div class="card-head"><h2>Sales Rep Performance</h2><span class="card-sub">Ranked by expected pipeline</span></div>
        <div class="table-wrap">{table(rep_cols, rep_rows)}</div>
      </div>
    </section>

    <section class="row two">
      <div class="card">
        <div class="card-head"><h2>Expected Pipeline by Industry</h2><span class="card-sub">Probability-weighted, open leads</span></div>
        {bar_chart(industry_rows, "industry", "expected_pipeline", "total_leads")}
      </div>
      <div class="card">
        <div class="card-head"><h2>Key Insights</h2></div>
        <ul class="insights">{insights_html}</ul>
        <div class="note"><strong>Recommendation:</strong> Work overdue high-score leads first, fill missing follow-up dates, and rank lead sources by expected pipeline rather than raw lead volume.</div>
      </div>
    </section>
  </main>

  <footer>Prepared by {AUTHOR}. All records are synthetic and generated for demonstration. Amounts in INR.</footer>
  <script>{DASHBOARD_JS}</script>
</body>
</html>
"""
    (REPORT_DIR / "pipeline_intelligence_dashboard.html").write_text(html, encoding="utf-8")


def write_executive_summary(tables: dict[str, list[dict]]) -> None:
    kpis = {row["metric"]: row["value"] for row in tables["pipeline_kpi_summary"]}
    top_source = tables["source_performance"][0]
    top_rep = tables["rep_performance"][0]
    top_industry = tables["industry_pipeline"][0]
    text = f"""# Executive Summary

## Project
{PROJECT_TITLE}

Author: {AUTHOR}

## Business Scenario
A B2B sales team managed leads across CRM exports and spreadsheets with duplicate records, inconsistent lead sources and sales stages, missing follow-up dates, and invalid deal values. Leadership lacked reliable visibility into pipeline value, lead source quality, sales rep workload, and overdue follow-ups.

## Solution
- Built a Python ETL workflow for CRM data cleansing, standardization, and deduplication.
- Designed a lead scoring model using stage, lead source, email engagement, meeting count, deal value, and contact recency.
- Loaded the cleaned dataset into SQLite and wrote SQL queries for pipeline KPIs, rep performance, source performance, stage conversion, and industry analysis.
- Created a priority follow-up queue covering overdue, due-this-week, and missing follow-up leads.
- Delivered dashboard-ready CSV exports and a static HTML sales pipeline dashboard.

## Key Findings
- Total leads cleaned: {kpis["Total leads cleaned"]}
- Active pipeline value: {kpis["Active pipeline value"]}
- Expected pipeline value: {kpis["Expected pipeline value"]}
- Won revenue: {kpis["Won revenue"]}
- Overdue follow-ups: {kpis["Overdue follow-ups"]}
- High-priority active leads: {kpis["High-priority active leads"]}
- Highest expected pipeline source: {top_source["lead_source"]} at {money(top_source["expected_pipeline"])}
- Top rep by expected pipeline: {top_rep["sales_rep"]} at {money(top_rep["expected_pipeline"])}
- Highest expected pipeline industry: {top_industry["industry"]} at {money(top_industry["expected_pipeline"])}

## Recommendation
Use the follow-up queue as a weekly sales operations workflow. Protect the existing pipeline by fixing missing follow-up dates, prioritizing high-score leads, and reviewing lead sources by expected value instead of raw lead volume.

## Skills Demonstrated
Python, SQL, SQLite, ETL, Data Cleaning, Data Standardization, Deduplication, Lead Scoring, Sales Pipeline Analysis, KPI Reporting, CRM Analytics, Dashboard Development (HTML/CSS), Revenue Operations, Business Development.
"""
    (REPORT_DIR / "executive_summary.md").write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    raw_rows = generate_raw_dataset()
    write_csv(RAW_PATH, raw_rows)
    clean_rows = clean_dataset(raw_rows)
    write_csv(CLEAN_PATH, clean_rows)
    load_sqlite(clean_rows)
    write_sql_file()
    tables = export_analysis_tables()
    write_dashboard(tables)
    write_executive_summary(tables)
    print(f"Generated {len(raw_rows)} raw CRM rows")
    print(f"Cleaned to {len(clean_rows)} deduplicated leads")
    print(f"Dashboard: {REPORT_DIR / 'pipeline_intelligence_dashboard.html'}")
    print(f"Executive summary: {REPORT_DIR / 'executive_summary.md'}")


if __name__ == "__main__":
    main()
