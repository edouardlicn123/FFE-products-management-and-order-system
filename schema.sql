-- 用户表
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- 产品表
CREATE TABLE IF NOT EXISTS product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL DEFAULT '其他',
    description TEXT,
    length INTEGER,
    width INTEGER,
    height INTEGER,
    seat_height INTEGER,
    images TEXT
);