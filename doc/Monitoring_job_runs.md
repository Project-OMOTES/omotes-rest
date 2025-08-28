## Introduction

To monitor OMOTES job runs in a single table. The script below can be applied manually in OMOTES REST PostgreSQL database.

```sql
CREATE TABLE job_logs (
    LIKE job_rest INCLUDING DEFAULTS,
    deleted_at TIMESTAMP DEFAULT NULL
);

CREATE OR REPLACE FUNCTION backup_job_to_logs()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    -- On DELETE: remove existing log row (if any), then insert with deleted_at
    DELETE FROM job_logs WHERE job_id = OLD.job_id;

    INSERT INTO job_logs
    SELECT OLD.*, now();

    RETURN OLD;

  ELSE
    -- On INSERT or UPDATE: remove existing log row (if any), then insert new
    DELETE FROM job_logs WHERE job_id = NEW.job_id;

    INSERT INTO job_logs
    SELECT NEW.*, NULL;

    RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_backup_all
AFTER INSERT OR UPDATE OR DELETE ON job_rest
FOR EACH ROW
EXECUTE FUNCTION backup_job_to_logs();
```