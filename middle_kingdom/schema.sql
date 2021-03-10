DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS words;
DROP TABLE IF EXISTS seen;
DROP TABLE IF EXISTS results;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT,
    creation_time TIMESTAMP NOT NULL
);

CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simplified TEXT NOT NULL,
    traditional TEXT NOT NULL,
    hsk_level INTEGER NOT NULL,
    pinyin_number TEXT NOT NULL,
    pinyin_accent TEXT NOT NULL,
    meaning TEXT NOT NULL,
    overall_freq INTEGER NOT NULL,
    wubi TEXT NOT NULL
);

CREATE TABLE seen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    appearance_time TIMESTAMP NOT NULL,
    question_type TEXT NOT NULL,
    answer_type TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(word_id) REFERENCES words(id)
);

CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seen_id INTEGER NOT NULL,
    is_correct INTEGER NOT NULL,
    question_time TIMESTAMP NOT NULL,
    answer_time TIMESTAMP NOT NULL,
    FOREIGN KEY(seen_id) REFERENCES seen(id)
);
