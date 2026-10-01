--Database

CREATE DATABASE IF NOT EXISTS SHPROD;

--Target table


CREATE OR REPLACE TABLE SHPROD.PUBLIC.RANK_PASSPORT(
    pr_id int identity(1,1) PRIMARY KEY,
    country_name VARCHAR not null,
    rnk int not null,
   yrs VARCHAR not null,
   run_id INT not null,
   strt_dt date,
   end_dt date,
   access_no_country int,
   not_access_no_country int
);


--RD Table

CREATE OR REPLACE TABLE SHPROD.PUBLIC.RANK_PASSPORT_RD (
    rid int,
    cntry VARCHAR PRIMARY KEY,
    rnk VARCHAR,
    access_no_country VARCHAR,
    yr VARCHAR
);


--STG Table

CREATE OR REPLACE TABLE SHPROD.PUBLIC.RANK_PASSPORT_STG (
    sid int ,
    cntry VARCHAR PRIMARY KEY,
    rnk VARCHAR,
    access_no_country VARCHAR,
    yr VARCHAR
);


--ERROR Table

CREATE OR REPLACE TABLE SHPROD.PUBLIC.RANK_PASSPORT_ERR (
    cntry VARCHAR,
    rnk VARCHAR,
    access_no_country VARCHAR,
    yr VARCHAR,
    error_reason VARCHAR,
    run_id INT
);


--Audit Table

CREATE TABLE IF NOT EXISTS SHPROD.PUBLIC.EXECUTION_LOGS (
    log_id INT IDENTITY(1,1) PRIMARY KEY,
    run_id INT,                  -- Link to your batch/run_id
    procedure_name VARCHAR(100),
    step_description VARCHAR(255),
    status VARCHAR(20),          -- 'STARTED', 'SUCCESS', 'FAILED'
    rows_affected INT,
    start_ts TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    end_ts TIMESTAMP_NTZ,
    error_code VARCHAR(10),
    error_message VARCHAR(16777216)
);


--Runlog Table

CREATE OR REPLACE TABLE SHPROD.PUBLIC.runlog (
    run_id INT IDENTITY(1,1) PRIMARY KEY,
    start_ts TIMESTAMP_NTZ,
    end_ts TIMESTAMP_NTZ,
    yrs VARCHAR,
    STATUS VARCHAR


);





--SELECT * FROM SHPROD.INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'RANK_PASSPORT';

--desc table RANK_PASSPORT;
