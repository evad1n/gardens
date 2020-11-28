CREATE TABLE IF NOT EXISTS users (
id SERIAL PRIMARY KEY,
first_name TEXT NOT NULL,
last_name TEXT NOT NULL,
email TEXT NOT NULL,
password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS gardens (
id SERIAL PRIMARY KEY,
name TEXT NOT NULL,
author TEXT NOT NULL,
author_id INTEGER NOT NULL,
CONSTRAINT fk_gardens_users
    FOREIGN KEY (author_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS flowers (
id SERIAL PRIMARY KEY,
color TEXT NOT NULL,
x REAL NOT NULL,
y REAL NOT NULL,
garden_id INTEGER NOT NULL,
CONSTRAINT fk_flowers_gardens
    FOREIGN KEY (garden_id)
    REFERENCES gardens(id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comments (
id SERIAL PRIMARY KEY,
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
