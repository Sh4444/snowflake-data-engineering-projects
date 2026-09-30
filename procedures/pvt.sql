CREATE OR REPLACE PROCEDURE SHPROD.PUBLIC.SP_VALIDATE_PASSPORT()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS OWNER
AS '
DECLARE
    v_run_id INT;
    v_err_count INT;
    v_stg_count INT;
BEGIN
    -- 1️⃣ Get the same iterative Run ID used in the batch
    v_run_id := (SELECT COALESCE(MAX(run_id), 0) FROM SHPROD.PUBLIC.RUNLOG);

    -- 2️⃣ Log Start of Validation
    INSERT INTO SHPROD.PUBLIC.EXECUTION_LOGS (run_id, procedure_name, step_description, status)
    VALUES (:v_run_id, ''sp_validate_passport'', ''Validation Started'', ''STARTED'');

    -- Clear STG
    TRUNCATE TABLE SHPROD.PUBLIC.RANK_PASSPORT_STG;
    TRUNCATE TABLE SHPROD.PUBLIC.RANK_PASSPORT_ERR;

    -- 3️⃣ Reject NULL records
    INSERT INTO SHPROD.PUBLIC.RANK_PASSPORT_ERR (cntry, rnk, access_no_country, yr, error_reason, run_id)
    SELECT cntry, rnk, access_no_country, yr, ''NULL VALUE'', ''1''
    FROM SHPROD.PUBLIC.RANK_PASSPORT_RD
    WHERE cntry IS NULL 
       OR yr IS NULL 
       OR rnk IS NULL 
       OR access_no_country IS NULL;

    -- 4️⃣ Reject duplicates
    INSERT INTO SHPROD.PUBLIC.RANK_PASSPORT_ERR (cntry, rnk, access_no_country, yr, error_reason, run_id)
    SELECT cntry, rnk, access_no_country, yr, ''DUPLICATE RECORD'', :v_run_id
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (
                 PARTITION BY cntry, yr 
                 ORDER BY rid
               ) AS rn
        FROM SHPROD.PUBLIC.RANK_PASSPORT_RD
    )
    WHERE rn > 1;

    v_err_count := SQLROWCOUNT; -- Tracks how many errors were logged in this run

    -- 5️⃣ Load clean data
    INSERT INTO SHPROD.PUBLIC.RANK_PASSPORT_STG (sid,cntry, rnk, access_no_country, yr)
    SELECT ROW_NUMBER() OVER (ORDER BY rnk ASC, cntry ASC) AS sid,
    cntry, rnk, access_no_country, yr
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (
                 PARTITION BY cntry, yr 
                 ORDER BY rid
               ) AS rn
        FROM SHPROD.PUBLIC.RANK_PASSPORT_RD
        WHERE cntry IS NOT NULL
          AND yr IS NOT NULL
          AND rnk IS NOT NULL
          AND access_no_country IS NOT NULL
    )
    WHERE rn = 1;

    v_stg_count := SQLROWCOUNT; -- Tracks how many clean records moved forward

    -- 6️⃣ Log Success with Audit Counts
    UPDATE SHPROD.PUBLIC.EXECUTION_LOGS
    SET status = ''SUCCESS'',
        end_ts = CURRENT_TIMESTAMP(),
        rows_affected = :v_stg_count,
        step_description = ''Validation Completed: '' || :v_stg_count || '' clean, '' || :v_err_count || '' errors.''
    WHERE run_id = :v_run_id AND procedure_name = ''sp_validate_passport'';

    RETURN ''Validation Completed. Run ID: '' || :v_run_id;

EXCEPTION
    WHEN OTHER THEN
        -- Log Failure
        UPDATE SHPROD.PUBLIC.EXECUTION_LOGS
    SET status = ''FAILED'',
        end_ts = CURRENT_TIMESTAMP(),
        rows_affected = :v_stg_count,
        step_description = ''Validation FAILED: '' || :v_stg_count || '' stg_count, '' || :v_err_count || '' errors.'',
        error_code = :SQLCODE,
        error_message = :SQLERRM
    WHERE run_id = :v_run_id AND procedure_name = ''sp_validate_passport'';

        RAISE; 
END;
';