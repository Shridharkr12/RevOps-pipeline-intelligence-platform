# Executive Summary

## Project
RevOps Pipeline Intelligence Platform

Author: Shridhar Sharma

## Business Scenario
A B2B sales team managed leads across CRM exports and spreadsheets with duplicate records, inconsistent lead sources and sales stages, missing follow-up dates, and invalid deal values. Leadership lacked reliable visibility into pipeline value, lead source quality, sales rep workload, and overdue follow-ups.

## Solution
- Built a Python ETL workflow for CRM data cleansing, standardization, and deduplication.
- Designed a lead scoring model using stage, lead source, email engagement, meeting count, deal value, and contact recency.
- Loaded the cleaned dataset into SQLite and wrote SQL queries for pipeline KPIs, rep performance, source performance, stage conversion, and industry analysis.
- Created a priority follow-up queue covering overdue, due-this-week, and missing follow-up leads.
- Delivered dashboard-ready CSV exports and a static HTML sales pipeline dashboard.

## Key Findings
- Total leads cleaned: 760
- Active pipeline value: ₹13,46,23,283
- Expected pipeline value: ₹4,48,81,027
- Won revenue: ₹1,75,79,108
- Overdue follow-ups: 442
- High-priority active leads: 194
- Highest expected pipeline source: Website at ₹1,02,98,410
- Top rep by expected pipeline: Simran Kaur at ₹1,08,14,596
- Highest expected pipeline industry: SaaS at ₹1,20,93,699

## Recommendation
Use the follow-up queue as a weekly sales operations workflow. Protect the existing pipeline by fixing missing follow-up dates, prioritizing high-score leads, and reviewing lead sources by expected value instead of raw lead volume.

## Skills Demonstrated
Python, SQL, SQLite, ETL, Data Cleaning, Data Standardization, Deduplication, Lead Scoring, Sales Pipeline Analysis, KPI Reporting, CRM Analytics, Dashboard Development (HTML/CSS), Revenue Operations, Business Development.
