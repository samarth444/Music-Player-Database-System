CREATE DATABASE musicdb;
USE musicdb;

-- Creating the 'User' table
CREATE TABLE User (
    user_id INT PRIMARY KEY,
    username VARCHAR(50),
    phone_number VARCHAR(15) UNIQUE,
    date_of_birth DATE,
    country VARCHAR(50),
    email_id VARCHAR(100),
    password VARCHAR(64),
    is_admin BOOLEAN DEFAULT FALSE,
    login_status ENUM('success', 'failure') DEFAULT 'failure';
);

-- Creating the 'Artist' table
CREATE TABLE Artist (
    artist_id INT PRIMARY KEY,
    name VARCHAR(100),
    style VARCHAR(50));

-- Creating the 'Album' table with ON DELETE CASCADE for artist_id
CREATE TABLE Album (
    album_id INT PRIMARY KEY,
    name VARCHAR(100),
    genre VARCHAR(50),
    year INT,
    artist_id INT,
    FOREIGN KEY (artist_id) REFERENCES Artist(artist_id) ON DELETE CASCADE
);

-- Creating the 'Song' table with ON DELETE CASCADE for album_id
CREATE TABLE Song (
    song_id INT PRIMARY KEY,
    name VARCHAR(100),
    ratings DECIMAL(3, 2),
    year_of_release INT,
    album_id INT,
    tags TEXT,
    FOREIGN KEY (album_id) REFERENCES Album(album_id) ON DELETE CASCADE
);

-- Creating the 'Playlist' table with ON DELETE CASCADE for both user_id and artist_id
CREATE TABLE Playlist (
    playlist_id INT PRIMARY KEY,
    name VARCHAR(100),
    tags TEXT,
    user_id INT,
    artist_id INT,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (artist_id) REFERENCES Artist(artist_id) ON DELETE CASCADE
);

-- Creating the 'Playlist_Song' table for many-to-many relationship between Playlist and Song
CREATE TABLE Playlist_Song (
    playlist_id INT,
    song_id INT,
    PRIMARY KEY (playlist_id, song_id),
    FOREIGN KEY (playlist_id) REFERENCES Playlist(playlist_id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES Song(song_id) ON DELETE CASCADE
);

-- Creating indexes to allow searching by album name, artist name, or playlist name
CREATE INDEX idx_album_name ON Album(name);
CREATE INDEX idx_artist_name ON Artist(name);
CREATE INDEX idx_playlist_name ON Playlist(name);

-- Optional: If you need to modify existing foreign key constraints (if any)
-- In case you previously had foreign key constraints without ON DELETE CASCADE, you can drop and recreate them:

-- Drop existing foreign key constraints (if applicable)
-- ALTER TABLE Album
-- DROP FOREIGN KEY album_artist_fk; -- Replace album_artist_fk with the actual foreign key name if different.

-- ALTER TABLE Song
-- DROP FOREIGN KEY song_album_fk; -- Replace song_album_fk with the actual foreign key name if different.

-- Recreate the foreign key constraints with ON DELETE CASCADE
-- ALTER TABLE Album
-- ADD CONSTRAINT album_artist_fk FOREIGN KEY (artist_id) REFERENCES Artist(artist_id) ON DELETE CASCADE;

-- ALTER TABLE Song
-- ADD CONSTRAINT song_album_fk FOREIGN KEY (album_id) REFERENCES Album(album_id) ON DELETE CASCADE;

-- If necessary, you can modify Playlist foreign keys similarly:
-- ALTER TABLE Playlist
-- DROP FOREIGN KEY playlist_artist_fk; -- Replace with actual foreign key name.
-- ALTER TABLE Playlist
-- ADD CONSTRAINT playlist_artist_fk FOREIGN KEY (artist_id) REFERENCES Artist(artist_id) ON DELETE CASCADE;

--procedure
DELIMITER $$

CREATE PROCEDURE GetMostPopularSong()
BEGIN
    SELECT s.song_id, s.name AS song_name, AVG(s.ratings) AS avg_rating
    FROM Song s
    GROUP BY s.song_id
    ORDER BY avg_rating DESC
    LIMIT 1;
END $$

DELIMITER ;

--table for user logs usings succes and failure triggers 
CREATE TABLE login_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    login_type ENUM('user', 'admin'),
    login_result ENUM('success', 'failure'),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


DELIMITER $$

CREATE TRIGGER log_successful_login
AFTER UPDATE ON User
FOR EACH ROW
BEGIN
    -- Check if the login_status was updated to 'success'
    IF NEW.login_status = 'success' AND OLD.login_status != 'success' THEN
        -- Log the successful login into the login_logs table
        INSERT INTO login_logs (username, login_type, login_result)
        VALUES (NEW.username, 
                IF(NEW.is_admin, 'admin', 'user'), 
                'success');
    END IF;
END $$

DELIMITER ;


DELIMITER $$

CREATE TRIGGER log_failed_login
AFTER UPDATE ON User
FOR EACH ROW
BEGIN
    -- Check if the login_status was updated to 'failure'
    IF NEW.login_status = 'failure' AND OLD.login_status != 'failure' THEN
        -- Log the failed login into the login_logs table
        INSERT INTO login_logs (username, login_type, login_result)
        VALUES (NEW.username, 
                IF(NEW.is_admin, 'admin', 'user'), 
                'failure');
    END IF;
END $$

DELIMITER ;

