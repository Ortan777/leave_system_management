-- Create the database
CREATE DATABASE IF NOT EXISTS leave;
USE leave;

-- Users table (for login)
CREATE TABLE users (
    username VARCHAR(20) PRIMARY KEY,
    password VARCHAR(100) NOT NULL
);

-- Permission table (leave requests)
CREATE TABLE permission (
    USN VARCHAR(20),
    NAME VARCHAR(100),
    `LEAVE` VARCHAR(10),
    `FROM` DATE,
    `TO` DATE,
    STATUS VARCHAR(20),
    REASON TEXT,
    NOTIFIED BOOLEAN DEFAULT FALSE
);

-- Subject leave tracking
CREATE TABLE subject_leaves (
    USN VARCHAR(20),
    subject VARCHAR(50),
    date DATE,
    period INT
);
