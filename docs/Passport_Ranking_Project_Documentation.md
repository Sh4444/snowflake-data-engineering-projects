# Passport Ranking — Snowflake Data Engineering Project

## Technical Documentation

## 1. Project Overview

The Passport Ranking project is an end-to-end Snowflake data engineering solution for processing yearly passport ranking data, validating source records, maintaining historical changes using SCD Type 2, and presenting the processed data through a Streamlit dashboard.

### Objectives

- Load passport ranking CSV data into Snowflake.
- Process the source using a scheduled batch pipeline.
- Maintain Raw Data (RD), Staging (STG), and Target (TRG) layers.
- Perform data-quality validation before target processing.
- Maintain ranking history using SCD Type 2.
- Provide reporting views and a Streamlit dashboard.
- Manage code through GitHub with DEV and PROD environments.
- Automate deployment through GitHub Actions.

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Snowflake | Cloud data warehouse and processing platform |
| Snowflake SQL | Data transformation and database objects |
| Snowflake Tasks | Scheduled batch orchestration |
| Snowflake Stage | Source CSV landing |
| SCD Type 2 | Historical change tracking |
| GitHub | Source control |
| GitHub Actions | CI/CD automation |
| Streamlit | Interactive dashboard |
| CSV | Source data format |

## 3. Architecture

```text
CSV File
   |
   v
Snowflake Stage
   |
   v
Scheduled Snowflake Task
   |
   +--> TRUNCATE RD
   |
   +--> COPY INTO RD
             |
             v
          RD Layer
             |
             v
        Validation
             |
             v
          STG Layer
             |
             v
        SCD Type 2
             |
             v
          TRG Layer
             |
             v
           Views
             |
             v
      Streamlit Dashboard
```

## 4. Data Flow

1. A passport ranking CSV is placed in the Snowflake stage.
2. The scheduled Snowflake Task starts the batch.
3. The RD table is truncated when a full batch refresh is required.
4. `COPY INTO` loads the staged CSV into RD.
5. Source data is validated and transformed.
6. Valid records are prepared in STG.
7. SCD Type 2 compares incoming records with active target records.
8. Changed records are end-dated and new versions are inserted.
9. Views expose reporting-ready data.
10. The Streamlit dashboard consumes the reporting layer.

## 5. Data Model

### RANK_PASSPORT_RD

Raw batch table containing the current source load.

### RANK_PASSPORT_STG

Staging layer used for validation and transformation.

### RANK_PASSPORT_TRG

Historical target table containing final passport ranking data.

### Typical RD Columns

| Column | Description |
|---|---|
| RID | Batch-generated row identifier |
| CNTRY | Country name |
| RNK | Passport ranking |
| ACCESS_NO_COUNTRY | Number of countries accessible |
| YR | Ranking year |

## 6. Batch Processing

The Passport Ranking implementation is batch based rather than continuous file ingestion. A scheduled Snowflake Task runs the batch at the configured time.

### Example Task

```sql
CREATE OR REPLACE TASK SHPROD.PUBLIC.LOAD_PASSPORT_JOB
    WAREHOUSE = 'COMPUTE_WH'
    SCHEDULE = 'USING CRON 59 0 * * * Asia/Kolkata'
AS
BEGIN
    TRUNCATE TABLE SHPROD.PUBLIC.RANK_PASSPORT_RD;

    COPY INTO SHPROD.PUBLIC.RANK_PASSPORT_RD
        (rid, cntry, rnk, access_no_country, yr)
    FROM (
        SELECT
            ROW_NUMBER() OVER (ORDER BY s.$1),
            s.$1, s.$2, s.$3, s.$4
        FROM @SHPROD.PUBLIC.LOADDATA/henleypassportindex.csv
             (FILE_FORMAT => 'SHPROD.PUBLIC.CSV_FORMAT') s
    )
    FORCE = TRUE;
END;
```

### FORCE Consideration

`FORCE = TRUE` is used when the same source filename must intentionally be reloaded. Because it bypasses Snowflake's already-loaded-file protection, it should only be used as part of an intentional full-refresh batch design.

## 7. SCD Type 2

SCD Type 2 preserves historical versions of passport ranking records instead of overwriting the previous state.

```text
Existing active record
        |
        v
End-date old record
        |
        v
Insert new ranking
        |
        v
New active record
```

### Example

```text
COUNTRY | RANK | START_DT   | END_DT
India   | 80   | 2024-01-01 | 2024-12-31
India   | 85   | 2025-01-01 | 9999-12-31
```

## 8. Data Validation

The pipeline validates source data before it reaches the final historical target.

### Validation Rules

- Country name must not be NULL.
- Ranking must not be NULL.
- Year must not be NULL.
- Duplicate country/year records should be identified.
- Ranking values should be checked against expected business rules.
- New countries should be validated before SCD Type 2 processing.

### Duplicate Check

```sql
SELECT cntry, yr, COUNT(*)
FROM SHPROD.PUBLIC.RANK_PASSPORT_RD
GROUP BY cntry, yr
HAVING COUNT(*) > 1;
```

## 9. Snowflake Objects

- **Tables** — RD, STG, and TRG data layers.
- **Stage** — source CSV landing location.
- **File Format** — CSV parsing configuration.
- **Tasks** — scheduled batch orchestration.
- **Procedures** — reusable transformation/business logic.
- **Views** — reporting and dashboard consumption.

## 10. GitHub Repository Structure

```text
snowflake-data-engineering-projects/
|
+-- .github/
|   +-- workflows/
|
+-- docs/
|
+-- tables/
+-- scripts/
+-- procedures/
+-- tasks/
+-- views/
|
+-- streamlit/
|   +-- passport_ranking/
|
+-- README.md
```

## 11. Git Branching and CI/CD

### Branch Strategy

```text
feature/*
    |
    v
  dev
    |
    | Pull Request
    v
  main
```

The `dev` branch is used for development and testing against Snowflake DEV. After validation, changes are promoted through a Pull Request to `main`. The `main` branch represents production-ready code and is deployed to Snowflake PROD.

### Deployment Flow

```text
Developer
    |
    v
feature/*
    |
    v
dev
    |
    v
GitHub Actions
    |
    v
Snowflake DEV
    |
    | Testing / Approval
    v
main
    |
    v
GitHub Actions
    |
    v
Snowflake PROD
```

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

Credentials must never be committed directly into SQL, YAML, or application source files.

## 12. Deployment Guide

1. Create the required Snowflake database, schema, warehouse, and roles.
2. Create the file format and stage.
3. Create RD, STG, and TRG tables.
4. Deploy procedures and transformation logic.
5. Create and configure tasks.
6. Create reporting views.
7. Configure GitHub Actions secrets and variables.
8. Deploy and validate the DEV environment.
9. Promote approved changes from `dev` to `main`.
10. Deploy the production version to Snowflake PROD.

### Recommended Object Order

```text
Database / Schema
      ↓
File Format / Stage
      ↓
Tables
      ↓
Procedures
      ↓
Tasks
      ↓
Views
      ↓
Streamlit
```

## 13. Streamlit Dashboard

The Streamlit application is maintained under:

```text
streamlit/passport_ranking/
```

It provides interactive views of passport ranking data, historical trends, country comparisons, and passport access information.

### Recommended Data Flow

```text
TRG
 |
 v
Reporting View
 |
 v
Streamlit
```

## 14. Troubleshooting

### COPY INTO Does Not Load a File

A file can be visible in the stage but skipped because Snowflake has already recorded it as loaded. For an intentional full batch reload, `FORCE = TRUE` can be used.

```sql
SELECT
    s.$1,
    s.$2,
    s.$3,
    s.$4
FROM @SHPROD.PUBLIC.LOADDATA/henleypassportindex.csv
     (FILE_FORMAT => 'SHPROD.PUBLIC.CSV_FORMAT') s
LIMIT 10;
```

### Check File Format

```sql
DESC FILE FORMAT SHPROD.PUBLIC.CSV_FORMAT;
```

### Check Task Status

```sql
SHOW TASKS LIKE 'LOAD_PASSPORT_JOB';
```

Resume a suspended task:

```sql
ALTER TASK SHPROD.PUBLIC.LOAD_PASSPORT_JOB RESUME;
```

## 15. Future Enhancements

- Automated data-quality test framework.
- Batch execution audit and logging.
- Pipeline monitoring and failure notifications.
- CI/CD automated SQL validation.
- Deployment rollback.
- Snowflake key-pair or OIDC authentication.
- Infrastructure as Code.
- Data lineage.
- Performance optimization.
- Expanded dashboard analytics.

## 16. Conclusion

This project demonstrates a complete Snowflake data engineering workflow covering batch ingestion, layered data processing, data validation, SCD Type 2 historical tracking, scheduled orchestration, reporting, visualization, Git-based development, and DEV-to-PROD CI/CD.
