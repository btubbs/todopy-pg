BEGIN;
CREATE TABLE todos (
	id SERIAL PRIMARY KEY,
	created_time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	description TEXT NOT NULL,
	completed BOOLEAN NOT NULL DEFAULT false
);

-- On any insert/update/delete of a todo, send a JSON-formatted notification to
-- a 'todos_update' channel.
CREATE OR REPLACE FUNCTION todos_notify_func() RETURNS trigger as $$
DECLARE
  payload text;
BEGIN
	IF TG_OP = 'DELETE' THEN
    payload := row_to_json(tmp)::text FROM (
			SELECT
				OLD.id as id,
				TG_OP as _op,
				TG_TABLE_NAME as _tablename
		) tmp;
	ELSE
		payload := row_to_json(tmp)::text FROM (
			SELECT 
				NEW.*,
				TG_TABLE_NAME as _tablename,
				TG_OP as _op
		) tmp;
		IF octet_length( payload ) > 8000 THEN
			-- payload is too big for a pg_notify. 
			payload := row_to_json(tmp)::text FROM (
				SELECT
					NEW.id as id,
					'payload length > 8000 bytes' as error,
					TG_TABLE_NAME as _tablename,
					TG_OP as _op
			) tmp;
		END IF;
	END IF;
  PERFORM pg_notify('todos_updates'::text, payload);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER todos_notify_trig AFTER INSERT OR UPDATE OR DELETE ON todos 
   FOR EACH ROW EXECUTE PROCEDURE todos_notify_func();

INSERT INTO migration_history (name) VALUES ('0002-add-todos-table');
COMMIT;
