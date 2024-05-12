SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS DatabaseManager;
DROP TABLE IF EXISTS Player;
DROP TABLE IF EXISTS Coach;
DROP TABLE IF EXISTS Jury;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE IF NOT EXISTS DatabaseManager (
    username VARCHAR(512) PRIMARY KEY,
    password LONGTEXT
);

CREATE TABLE IF NOT EXISTS Player (
    username	VARCHAR(512) PRIMARY KEY,
    password	VARCHAR(512),
    name	VARCHAR(512),
    surname	VARCHAR(512),
    date_of_birth VARCHAR(512), 
    height REAL,
    weight REAL
);

CREATE TABLE IF NOT EXISTS Coach (
	  username	VARCHAR(512) PRIMARY KEY,
    password	VARCHAR(512),
    name	VARCHAR(512),
    surname	VARCHAR(512),
    nationality VARCHAR(512) NOT NULL
);

CREATE TABLE IF NOT EXISTS Jury (
	  username	VARCHAR(512) PRIMARY KEY,
    password	VARCHAR(512),
    name	VARCHAR(512),
    surname	VARCHAR(512),
    nationality VARCHAR(512) NOT NULL
);

