SET foreign_key_checks = 0;
DROP TABLE IF EXISTS SessionSquads;
DROP TABLE IF EXISTS MatchSession;
DROP TABLE IF EXISTS PlayerPositions;
DROP TABLE IF EXISTS PlayerTeams;
DROP TABLE IF EXISTS Team;
DROP TABLE IF EXISTS TvChannel;
DROP TABLE IF EXISTS Stadium;
DROP TABLE IF EXISTS Positions;
DROP TABLE IF EXISTS Jury;
DROP TABLE IF EXISTS Coach;
DROP TABLE IF EXISTS Player;
DROP TABLE IF EXISTS DatabaseManager;
SET foreign_key_checks = 1;

CREATE TABLE IF NOT EXISTS DatabaseManager (
    username VARCHAR(256) PRIMARY KEY,
    password LONGTEXT
);

CREATE TABLE IF NOT EXISTS Player (
    username	VARCHAR(256) PRIMARY KEY,
    password	VARCHAR(256),
    name	VARCHAR(256),
    surname	VARCHAR(256),
    date_of_birth VARCHAR(256), 
    height REAL,
    weight REAL
);

CREATE TABLE IF NOT EXISTS Coach (
	username	VARCHAR(256) PRIMARY KEY,
    password	VARCHAR(256),
    name	VARCHAR(256),
    surname	VARCHAR(256),
    nationality VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS Jury (
	username	VARCHAR(256) PRIMARY KEY,
    password	VARCHAR(256),
    name	VARCHAR(256),
    surname	VARCHAR(256),
    nationality VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS Positions (
    position_ID INTEGER PRIMARY KEY,
    position_name VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS Stadium (
    stadium_ID INTEGER PRIMARY KEY,
    stadium_name VARCHAR(256) UNIQUE,
    country VARCHAR(256),
    UNIQUE (stadium_ID, stadium_name, country)
);

CREATE TABLE IF NOT EXISTS TvChannel (
	channel_ID INTEGER PRIMARY KEY,
    channel_name VARCHAR(256),
    UNIQUE (channel_ID, channel_name)
);

CREATE TABLE IF NOT EXISTS Team 
(
    team_ID	INT PRIMARY KEY,
    team_name	VARCHAR(256),
    coach_username	VARCHAR(256) NOT NULL,
    contract_start	VARCHAR(256),
    contract_finish	VARCHAR(256),
    channel_ID	INT,
    channel_name	VARCHAR(256),
    FOREIGN KEY (channel_ID, channel_name) REFERENCES TvChannel(channel_ID, channel_name),
    FOREIGN KEY (coach_username) REFERENCES Coach(username)
); 

CREATE TABLE IF NOT EXISTS PlayerTeams (
    player_teams_ID INTEGER PRIMARY KEY,
	username VARCHAR(256),
    team INTEGER,
    FOREIGN KEY (username) REFERENCES Player(username),
    FOREIGN KEY (team) REFERENCES Team(team_ID)
);


CREATE TABLE IF NOT EXISTS PlayerPositions (
    player_positions_ID INTEGER PRIMARY KEY,
    username VARCHAR(256),
    position INTEGER,
    FOREIGN KEY (username) REFERENCES Player(username),
    FOREIGN KEY (position) REFERENCES Positions(position_ID)
);

CREATE TABLE IF NOT EXISTS MatchSession (
    session_ID INTEGER PRIMARY KEY,
    team_ID INTEGER,
    stadium_id INTEGER,
    stadium_name VARCHAR(256),
    stadium_country VARCHAR(256),
    time_slot VARCHAR(256),
    date VARCHAR(256),
    assigned_jury_username VARCHAR(256) NOT NULL,
    rating REAL,
    FOREIGN KEY (team_ID) REFERENCES Team(team_ID),
    FOREIGN KEY (stadium_id, stadium_name, stadium_country) REFERENCES Stadium(stadium_ID, stadium_name, country) ON UPDATE CASCADE,
    FOREIGN KEY (assigned_jury_username) REFERENCES Jury(username)
);

CREATE TABLE IF NOT EXISTS SessionSquads (
    squad_ID INTEGER PRIMARY KEY,
    session_ID INTEGER,
    played_player_username VARCHAR(256),
    position_ID INTEGER,
    FOREIGN KEY (played_player_username) REFERENCES Player(username),
    FOREIGN KEY (position_ID) REFERENCES Positions(position_ID),
    FOREIGN KEY (session_ID) REFERENCES MatchSession(session_ID) ON DELETE CASCADE
);

