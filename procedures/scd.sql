CREATE OR REPLACE PROCEDURE SHPROD.PUBLIC.SP_PASSPORT_SCD()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS OWNER
AS '
DECLARE
    v_run_id INT ;
    v_rows INT DEFAULT 0;
    v_rowsd INT DEFAULT 0;
    v_rowsi INT DEFAULT 0;
    v_total_cnt INT;
BEGIN
    -- 1️⃣ Get Iterative Run ID
    v_run_id := (SELECT COALESCE(MAX(run_id), 0) FROM SHPROD.PUBLIC.RUNLOG);
    v_total_cnt := (SELECT COALESCE(MAX(access_no_country::INT),0) FROM SHPROD.PUBLIC.RANK_PASSPORT_RD);

    -- 2️⃣ Log Start
    INSERT INTO SHPROD.PUBLIC.EXECUTION_LOGS (run_id, procedure_name, step_description, status)
    VALUES (:v_run_id, ''sp_passport_scd'', ''SCD Type 2 Process Started'', ''STARTED'');

    -- 3️⃣ Expire Records
    UPDATE SHPROD.PUBLIC.RANK_PASSPORT t
    SET end_dt = CURRENT_DATE - 1
    FROM SHPROD.PUBLIC.RANK_PASSPORT_STG s
    WHERE t.country_name = s.cntry AND t.end_dt = ''9999-12-31'' AND s.yr > t.yrs;
    
    v_rowsd := SQLROWCOUNT; -- Capture rows updated

    -- 4️⃣ Insert Records
     INSERT INTO SHPROD.PUBLIC.RANK_PASSPORT (
        country_name,
        rnk,
        yrs,
        run_id,
        strt_dt,
        end_dt,
        access_no_country,
        not_access_no_country
    )
    SELECT 
        s.cntry,
        s.rnk,
        s.yr,
        :v_run_id,  -- This remains fixed for every row in this specific batch
        CURRENT_DATE,
        ''9999-12-31'',
         s.access_no_country,
         :v_total_cnt-s.access_no_country

    FROM SHPROD.PUBLIC.RANK_PASSPORT_STG s
    WHERE NOT EXISTS (
        SELECT 1 
        FROM SHPROD.PUBLIC.RANK_PASSPORT t 
        WHERE t.country_name = s.cntry 
          AND t.yrs = s.yr
          AND t.end_dt = ''9999-12-31''
    );

    v_rowsi := SQLROWCOUNT; -- Add rows inserted
    v_rows := v_rowsd + v_rowsi; -- Total rows affected


    -- 5️⃣ Log Success
    UPDATE SHPROD.PUBLIC.EXECUTION_LOGS
    SET status = ''SUCCESS'',
        end_ts = CURRENT_TIMESTAMP(),
        rows_affected = :v_rows,
        step_description = ''SCD Type 2 Process Completed: '' || :v_rowsd || '' EndDRecords, '' || :v_rowsi || '' NewRecords.''
    WHERE run_id = :v_run_id AND procedure_name = ''sp_passport_scd'';

    RETURN ''Success'';

EXCEPTION
    WHEN OTHER THEN
        -- 6️⃣ Log Failure

        UPDATE SHPROD.PUBLIC.EXECUTION_LOGS
        SET status = ''FAILED'',
        end_ts = CURRENT_TIMESTAMP(),
        rows_affected = :v_rows,
        step_description = ''SCD Type 2 Process Failed: '' || :v_rowsd || '' EndDRecords, '' || :v_rowsi || '' NewRecords.'',
        error_code= :SQLCODE,
        error_message = :SQLERRM
        WHERE run_id = :v_run_id AND procedure_name = ''sp_passport_scd'';
 
        RAISE; -- Re-throw the error so the Snowflake Task also knows it failed
END;
';