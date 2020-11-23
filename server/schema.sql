DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS gardens;
DROP TABLE IF EXISTS flowers;
DROP TABLE IF EXISTS comments;

CREATE TABLE users (
id INTEGER PRIMARY KEY,
first_name TEXT NOT NULL,
last_name TEXT NOT NULL,
email TEXT NOT NULL,
password TEXT NOT NULL
);

CREATE TABLE gardens (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL,
author TEXT NOT NULL,
author_id INTEGER NOT NULL,
CONSTRAINT fk_gardens_users
    FOREIGN KEY (author_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

CREATE TABLE flowers (
id INTEGER PRIMARY KEY,
color TEXT NOT NULL,
x REAL NOT NULL,
y REAL NOT NULL,
garden_id INTEGER NOT NULL,
CONSTRAINT fk_flowers_gardens
    FOREIGN KEY (garden_id)
    REFERENCES gardens(id)
    ON DELETE CASCADE
);

CREATE TABLE comments (
id INTEGER PRIMARY KEY,
content TEXT NOT NULL,
garden_id INTEGER NOT NULL,
author_id INTEGER NOT NULL,
CONSTRAINT fk_comments_gardens
    FOREIGN KEY (garden_id)
    REFERENCES gardens(id)
    ON DELETE CASCADE,
CONSTRAINT fk_comments_users
    FOREIGN KEY (author_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);
