CREATE TABLE IF NOT EXISTS Users (
user_id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
mail text NOT NULL,
password text NOT NULL
);

CREATE TABLE IF NOT EXISTS Items (
item_id integer PRIMARY KEY AUTOINCREMENT,
category text NOT NULL,
name text NOT NULL,
price integer NOT NULL,
main_color text not NULL,
sizes text NOT NULL,
main_photo_src text  NOT NULL
);

CREATE TABLE IF NOT EXISTS Cart (
user_id integer NOT NULL,
item_id integer NOT NULL,
add_time text NOT NULL,
FOREIGN KEY (user_id) REFERENCES Users (user_id),
FOREIGN KEY (item_id) REFERENCES Items (item_id)
);

CREATE TABLE IF NOT EXISTS Photos (
item_id integer NOT NULL,
photo_src text NOT NULL,
FOREIGN KEY (item_id) REFERENCES Items (item_id)
);