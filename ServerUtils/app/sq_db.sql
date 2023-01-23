CREATE TABLE IF NOT EXISTS Users (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
mail text NOT NULL,
password text NOT NULL
);

CREATE TABLE IF NOT EXISTS Items (
id integer PRIMARY KEY AUTOINCREMENT,
category text NOT NULL,
name text NOT NULL,
price integer,
sizes float[10],
photos text[10]
);