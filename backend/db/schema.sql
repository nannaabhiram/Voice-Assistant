-- Database Schema for Offline AI Assistant

-- Table: tasks
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    status ENUM('pending','done') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date DATETIME NULL
);

-- Table: reminders
DROP TABLE IF EXISTS reminders;
CREATE TABLE reminders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    remind_time DATETIME NOT NULL,
    notified TINYINT DEFAULT 0,
    text VARCHAR(255) NOT NULL
);

-- Table: conversations
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_input TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: system_logs
CREATE TABLE IF NOT EXISTS system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(255) NOT NULL,
    status ENUM('success','fail') DEFAULT 'success',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert, select, and update operations for reminders
INSERT INTO reminders (text, remind_time) VALUES ('Meeting with team', '2023-10-10 10:00:00');
SELECT id, text, remind_time FROM reminders WHERE remind_time <= NOW() AND notified = 0;
UPDATE reminders SET notified = 1 WHERE id = 1;



