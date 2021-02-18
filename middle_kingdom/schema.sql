DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS words;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT
);

CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simplified TEXT NOT NULL,
    traditional TEXT NOT NULL,
    hsk_level INT NOT NULL,
    pinyin_number TEXT NOT NULL,
    pinyin_accent TEXT NOT NULL,
    meaning TEXT NOT NULL,
    overall_freq INT NOT NULL,
    wubi TEXT NOT NULL
);
