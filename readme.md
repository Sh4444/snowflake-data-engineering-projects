# 🌍 Passport Ranking Data Engineering Project

A modern **Snowflake Data Engineering project** that processes passport ranking data over multiple years using an automated data pipeline, **SCD Type 2**, Snowpipe, Snowflake Tasks, and GitHub-based CI/CD.

The project is designed to demonstrate an end-to-end data engineering workflow from raw CSV ingestion to a production-ready target table and dashboard.

---

## 📌 Project Overview

The Passport Ranking pipeline loads yearly passport ranking data into Snowflake and maintains historical changes using **Slowly Changing Dimension (SCD) Type 2**.

The pipeline supports:

* Automated CSV ingestion
* Raw data landing
* Data validation
* Staging transformation
* SCD Type 2 historical tracking
* Snowpipe auto-ingestion
* Snowflake Tasks for orchestration
* Production target tables
* GitHub source control
* DEV → PROD CI/CD
* Dashboard-ready data

---

## 🏗️ Architecture

```text
                    CSV Files
                       │
                       ▼
                ┌─────────────┐
                │   Snowpipe  │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │     RD      │
                │ Raw Data    │
                └──────┬──────┘
                       │
                  Validation
                       │
                       ▼
                ┌─────────────┐
                │     STG     │
                │  Staging    │
                └──────┬──────┘
                       │
                 SCD Type 2
                       │
                       ▼
                ┌─────────────┐
                │     TRG     │
                │   Target    │
                └──────┬──────┘
                       │
                       ▼
                 Dashboard
```

---

## 🔄 Data Flow

```text
CSV
 │
 ▼
Snowflake Stage
 │
 ▼
Snowpipe
 │
 ▼
RANK_PASSPORT_RD
 │
 ▼
Validation
 │
 ▼
RANK_PASSPORT_STG
 │
 ▼
SCD Type 2 Processing
 │
 ▼
RANK_PASSPORT_TRG
 │
 ▼
Dashboard
```

---

## 🗄️ Snowflake Data Layers

### RD — Raw Data

`RANK_PASSPORT_RD`

Contains the data exactly as received from the source CSV files.

Purpose:

* Raw data landing
* Source data preservation
* Initial validation

---

### STG — Staging

`RANK_PASSPORT_STG`

Used to prepare and validate data before loading into the target.

Typical validations include:

* Country name validation
* Duplicate checking
* Required-field validation
* Data type validation
* Ranking validation

---

### TRG — Target

`RANK_PASSPORT_TRG`

Contains the final historical passport ranking data.

The target table maintains historical records using SCD Type 2.

Example:

```text
COUNTRY_NAME | RANK | STRT_DT   | END_DT
-------------|------|-----------|-----------
Country A    | 10   | 2024-01-01| 2024-12-31
Country A    | 8    | 2025-01-01| 9999-12-31
```

This allows historical changes to be preserved instead of overwriting previous records.

---

# 🔁 SCD Type 2

The project uses **Slowly Changing Dimension Type 2** to maintain historical ranking changes.

When an existing country's ranking changes:

1. Existing active record is end-dated.
2. New ranking record is inserted.
3. New record becomes the active record.

Conceptually:

```text
Existing Record
      │
      ▼
End Date Old Record
      │
      ▼
Insert New Record
      │
      ▼
New Active Record
```

Active records use an open-ended `END_DT`.

---

# 🚀 Snowpipe

Snowpipe is used for automated ingestion of new CSV files.

```text
New CSV
   │
   ▼
Cloud Storage / Stage
   │
   ▼
Snowpipe
   │
   ▼
Raw Table
```

This eliminates the need for manually running `COPY INTO` whenever a new file arrives.

---

# ⏱️ Snowflake Tasks

Snowflake Tasks are used to orchestrate the pipeline.

Example:

```text
Snowpipe
   │
   ▼
Validation
   │
   ▼
STG Load
   │
   ▼
SCD Type 2
   │
   ▼
Target
```

Tasks can be scheduled or triggered based on pipeline requirements.

---

# 📂 Repository Structure

```text
passport-ranking/
│
├── .github/
│   └── workflows/
│       └── snowflake-cicd.yml
│
├── sql/
│   ├── 01_database_schema.sql
│   ├── 02_tables.sql
│   ├── 03_file_formats_stages.sql
│   ├── 04_pipes.sql
│   ├── 05_procedures.sql
│   ├── 06_tasks.sql
│   └── 07_views.sql
│
├── dashboard/
│
└── README.md
```

### SQL Deployment Order

The SQL files are executed in the following order:

```text
01_database_schema.sql
        ↓
02_tables.sql
        ↓
03_file_formats_stages.sql
        ↓
04_pipes.sql
        ↓
05_procedures.sql
        ↓
06_tasks.sql
        ↓
07_views.sql
```

All table definitions are maintained together in:

```text
sql/02_tables.sql
```

---

# 🔀 Git Branching Strategy

The project uses two main branches:

```text
feature/*
     │
     ▼
    dev
     │
     │ Pull Request
     ▼
   main
```

### DEV

The `dev` branch is used for development and testing.

Changes pushed to `dev` are deployed to the Snowflake DEV environment.

### MAIN

The `main` branch represents production-ready code.

Changes are promoted from:

```text
dev → main
```

through a Pull Request.

Changes merged into `main` are deployed to Snowflake PROD.

---

# ⚙️ CI/CD Pipeline

GitHub Actions is used to automate deployment.

```text
Developer
    │
    ▼
feature/*
    │
    ▼
   dev
    │
    ▼
GitHub Actions
    │
    ▼
Snowflake DEV
    │
    │ Testing
    ▼
Pull Request
    │
    ▼
   main
    │
    ▼
GitHub Actions
    │
    ▼
Snowflake PROD
```

The CI/CD pipeline performs:

* SQL validation
* Credential checks
* Snowflake connection validation
* SQL deployment
* DEV deployment
* PROD deployment

---

# 🔐 Security

Credentials are not stored in the repository.

GitHub Actions uses:

### GitHub Secrets

```text
SNOWFLAKE_ACCOUNT
SNOWFLAKE_USER
SNOWFLAKE_PAT
```

### GitHub Variables

```text
SNOWFLAKE_ROLE
SNOWFLAKE_WAREHOUSE
```

Sensitive credentials should never be committed to GitHub.

---

# 🧪 Data Validation

The pipeline validates incoming data before processing.

Examples:

```text
✓ Country name cannot be NULL
✓ Duplicate countries are rejected
✓ Required fields must be populated
✓ Ranking values must be valid
✓ Data types must match the target structure
```

Invalid records can be rejected before entering the target table.

---

# 📊 Dashboard

The final target data can be consumed by a dashboard for analysis such as:

* Passport ranking by year
* Country ranking changes
* Historical ranking trends
* Country-level comparisons
* Top-ranked passports
* Ranking movement over time

---

# 🛠️ Technology Stack

| Technology      | Purpose                  |
| --------------- | ------------------------ |
| Snowflake       | Cloud Data Warehouse     |
| Snowpipe        | Automated ingestion      |
| Snowflake Tasks | Pipeline orchestration   |
| Snowflake SQL   | Transformation           |
| SCD Type 2      | Historical data tracking |
| GitHub          | Source control           |
| GitHub Actions  | CI/CD                    |
| CSV             | Source data              |
| Dashboard       | Data visualization       |

---

# 🎯 Key Features

* End-to-end Snowflake data pipeline
* Automated file ingestion
* Raw → Staging → Target architecture
* SCD Type 2 implementation
* Historical passport ranking tracking
* Data quality validation
* Snowpipe automation
* Snowflake Task orchestration
* Git-based development
* DEV and PROD environments
* Automated CI/CD deployment

---

# 🚀 Future Enhancements

Potential future improvements include:

* Automated data-quality testing
* Key-pair or OIDC authentication
* CI/CD deployment rollback
* Dynamic SQL deployment framework
* Monitoring and alerting
* Pipeline execution logging
* Additional dashboard analytics
* Infrastructure-as-code
* Automated documentation generation

---

## 👨‍💻 Project

**Passport Ranking Data Engineering Project**

Built using Snowflake, SQL, Snowpipe, Snowflake Tasks, SCD Type 2, GitHub, and GitHub Actions.
