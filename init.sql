-- Drop the existing database if it exists
DROP DATABASE IF EXISTS VCID_app;

-- Create the VCID_app database
CREATE DATABASE IF NOT EXISTS VCID_app;

-- Create the 'vcid' user with privileges on the VCID_app database
CREATE USER IF NOT EXISTS 'vcid'@'localhost' IDENTIFIED BY 'IchBinDeinSicheresPasswort69';
GRANT ALL PRIVILEGES ON VCID_app.* TO 'vcid'@'localhost';

-- Switch to the VCID_app database
USE VCID_app;

-- Create the 'users' table
CREATE TABLE users (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL
);

-- Create the 'posts' table with the 'author_username' field
CREATE TABLE posts (
    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    author_username VARCHAR(255) NOT NULL,  -- New field for author's username
    titel VARCHAR(255) NOT NULL,
    inhalt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- New field for post creation timestamp
    CONSTRAINT fk_user_id_posts FOREIGN KEY (user_id) REFERENCES users (id)
);