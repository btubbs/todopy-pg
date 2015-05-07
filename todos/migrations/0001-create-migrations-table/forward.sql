BEGIN;
CREATE TABLE migration_history (
	name TEXT NOT NULL, 
	time TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	who TEXT DEFAULT CURRENT_USER NOT NULL, 
	PRIMARY KEY (name)
);

INSERT INTO migration_history (name) VALUES ('0001-create-migrations-table');
COMMIT;
