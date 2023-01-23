CREATE TABLE IF NOT EXISTS User_Info (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
mail text NOT NULL,
password text NOT NULL,
shoplist integer[30]
);

CREATE TABLE IF NOT EXISTS Items (
id integer PRIMARY KEY AUTOINCREMENT,
category text NOT NULL,
name text NOT NULL,
price float,
sizes float[10],
photos text[10]
);