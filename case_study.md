# Case Study: RevOps Pipeline Intelligence Platform

## Summary

A Python and SQL workflow that cleans messy CRM lead data, scores opportunities, prioritizes follow-ups, and produces a sales pipeline dashboard for weekly business review.

## Background

I hold a B.Tech in Information Technology from Chandigarh Group of Colleges, Landran, and have worked as a Business Development Executive (BDE). In that role, lead follow-up discipline and clean CRM data directly affected conversions. This project applies that sales experience together with technical skills in Python, SQL, and data reporting.

## Business Problem

B2B sales teams often track leads across CRM exports and spreadsheets. Typical issues:

- Duplicate lead records
- Inconsistent lead sources and sales stages
- Missing or overdue follow-up dates
- Incomplete or invalid deal values
- No visibility into pipeline risk
- No clear next-action list for sales reps

Impact: leads go cold, managers overvalue raw lead count, and high-value opportunities are contacted late.

## Solution

1. **Data generation:** a seeded, reproducible raw CRM dataset with realistic quality issues.
2. **Data cleansing (Python):** standardized sources, industries, regions, stages, email statuses, dates, deal values, and flags.
3. **Deduplication:** one record per lead, keeping the most advanced stage and latest contact.
4. **Lead scoring:** a 0 to 100 score from stage, source, email engagement, meetings, deal value, follow-up status, and contact recency.
5. **Follow-up logic:** Overdue, Due Today, Due This Week, Missing Follow-Up, Scheduled, or Closed.
6. **SQLite database:** cleaned data loaded for repeatable SQL analysis.
7. **SQL analysis:** KPI summary, follow-up queue, rep performance, source performance, stage analysis, and industry pipeline.
8. **Dashboard and summary:** an HTML dashboard and an executive summary for business users.

## Business Questions Answered

- How much active and probability-weighted pipeline does the team hold?
- Which leads need follow-up first?
- Which sales reps carry the most pipeline and overdue follow-ups?
- Which lead sources and industries produce the strongest opportunities?
- Which stages hold the most pipeline value?
- Where is revenue at risk because follow-ups are missing or overdue?

## Tools

Python, SQL, SQLite, CSV, HTML/CSS.

## Possible Next Steps

- Power BI or Excel version of the dashboard
- Scheduled weekly refresh
- Win-probability model trained on historical stage data

