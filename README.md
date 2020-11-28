# Gardens Server

https://gardens-server.herokuapp.com/

## Resources

**Users**
* first_name (string)
* last_name (string)
* email (string)
* password (encrypted string)

**Gardens**
* name (string)
* author (string)
* flowers (list)
* comments (list)
* ***Foreign Key*** Owner (User)

**Flowers**
* color (string)
* x (float)
* y (float)
* ***Foreign Key*** Garden

**Comments**
* content (string)
* ***Foreign Key*** Garden
* ***Foreign Key*** Author (User)


## Schema

```sql
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
userid INTEGER NOT NULL,
CONSTRAINT fk_gardens_users
    FOREIGN KEY (userid)
    REFERENCES users(id)
    ON DELETE CASCADE
);

CREATE TABLE flowers (
id INTEGER PRIMARY KEY,
color TEXT NOT NULL,
x REAL NOT NULL,
y REAL NOT NULL,
gardenid INTEGER NOT NULL,
CONSTRAINT fk_flowers_gardens
    FOREIGN KEY (gardenid)
    REFERENCES gardens(id)
    ON DELETE CASCADE
);

CREATE TABLE comments (
id INTEGER PRIMARY KEY,
content TEXT NOT NULL,
gardenid INTEGER NOT NULL,
userid INTEGER NOT NULL,
CONSTRAINT fk_comments_gardens
    FOREIGN KEY (gardenid)
    REFERENCES gardens(id)
    ON DELETE CASCADE,
CONSTRAINT fk_comments_users
    FOREIGN KEY (userid)
    REFERENCES users(id)
    ON DELETE CASCADE
);

```

## REST Endpoints

### **Gardens**

Name                           | Method | Path
-------------------------------|--------|------------------
Retrieve garden collection     | GET    | /gardens
Retrieve garden member         | GET    | /gardens/*\<id\>*
Create garden member           | POST   | /gardens
Update garden member           | PUT    | /gardens/*\<id\>*
Delete garden member           | DELETE | /gardens/*\<id\>*

### **Flowers**

Name                           | Method | Path
-------------------------------|--------|------------------
Retrieve layout collection     | GET    | /flowers
Create layout member           | POST   | /flowers
Delete layout member           | DELETE | /flowers/*\<id\>*

### **Comments**

Name                           | Method | Path
-------------------------------|--------|------------------
Retrieve comment collection    | GET    | /comments
Create comment member          | POST   | /comments
Delete comment member          | DELETE | /comments/*\<id\>*

### **Users**

Name                           | Method | Path
-------------------------------|--------|------------------
Register a new user            | POST   | /users

### **Sessions**

Name                           | Method | Path
-------------------------------|--------|------------------
Current user info              | GET    | /me
Login                          | POST   | /sessions
Logout                         | DELETE | /sessions



## Password Hashing

```python
hashed = bcrypt.hash(password)
DB.create_user(first_name, last_name, email, hashed)
```
