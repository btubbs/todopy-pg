BEGIN;

-- It turns out that the frontend todomvc code was using uuids.  Let's show off
-- Postgres a little by switching to use uuids for our primary key too.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

ALTER TABLE todos ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();
ALTER TABLE todos DROP CONSTRAINT todos_pkey;
ALTER TABLE todos DROP COLUMN id;
ALTER TABLE todos RENAME COLUMN new_id TO id;
ALTER TABLE todos ADD PRIMARY KEY (id);

ALTER TABLE todos RENAME COLUMN description TO title;

-- add a new column
INSERT INTO migration_history (name) VALUES ('0003-uuids-title');
COMMIT;
