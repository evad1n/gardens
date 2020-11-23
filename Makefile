all: run

run: 
	./reload.py

db:
	sqlite3 gardens.db

db-reset: 
	echo .read schema.sql | sqlite3 gardens.db
