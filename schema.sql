CREATE DATABASE IF NOT EXISTS itms_db;
USE itms_db;

CREATE TABLE Department (
    DepartmentID INT AUTO_INCREMENT PRIMARY KEY,
    DepartmentName VARCHAR(50) NOT NULL
);

CREATE TABLE Faculty (
    FacultyID INT AUTO_INCREMENT PRIMARY KEY,
    FacultyName VARCHAR(50) NOT NULL,
    FacultyEmail VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Student (
    StudentID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Phone VARCHAR(15),
    DepartmentID INT,
    FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID) ON DELETE SET NULL
);

CREATE TABLE Company (
    CompanyID INT AUTO_INCREMENT PRIMARY KEY,
    CompanyName VARCHAR(50) NOT NULL,
    ContactEmail VARCHAR(100) NOT NULL,
    Location VARCHAR(100)
);

CREATE TABLE Internship (
    InternshipID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(100) NOT NULL,
    Duration VARCHAR(50),
    Stipend DECIMAL(10,2),
    CompanyID INT,
    FacultyID INT,
    FOREIGN KEY (CompanyID) REFERENCES Company(CompanyID) ON DELETE CASCADE,
    FOREIGN KEY (FacultyID) REFERENCES Faculty(FacultyID) ON DELETE SET NULL
);

CREATE TABLE Application (
    ApplicationID INT AUTO_INCREMENT PRIMARY KEY,
    DateApplied DATE NOT NULL,
    Status ENUM('Pending', 'Accepted', 'Rejected') DEFAULT 'Pending',
    StudentID INT,
    InternshipID INT,
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID) ON DELETE CASCADE,
    FOREIGN KEY (InternshipID) REFERENCES Internship(InternshipID) ON DELETE CASCADE
);

CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    Role ENUM('student', 'faculty', 'admin') NOT NULL,
    RefID INT
);

-- Insert Sample Data
INSERT INTO Department (DepartmentName) VALUES ('Computer Science'), ('Electrical Engineering');

INSERT INTO Faculty (FacultyName, FacultyEmail) VALUES 
('Dr. Alan Turing', 'alan@college.edu'), 
('Dr. Ada Lovelace', 'ada@college.edu');

INSERT INTO Student (Name, Email, Phone, DepartmentID) VALUES 
('Alice Smith', 'alice@student.edu', '1234567890', 1),
('Bob Johnson', 'bob@student.edu', '0987654321', 1),
('Charlie Brown', 'charlie@student.edu', '1122334455', 2);

INSERT INTO Company (CompanyName, ContactEmail, Location) VALUES 
('TechCorp', 'hr@techcorp.com', 'New York'),
('Innovate Inc', 'careers@innovate.com', 'San Francisco');

INSERT INTO Internship (Title, Duration, Stipend, CompanyID, FacultyID) VALUES 
('Software Engineering Intern', '3 Months', 1500.00, 1, 1),
('Data Science Intern', '6 Months', 2000.00, 1, 2),
('Hardware Engineering Intern', '3 Months', 1200.00, 2, 2);

INSERT INTO Application (DateApplied, Status, StudentID, InternshipID) VALUES 
('2024-03-01', 'Pending', 1, 1),
('2024-03-02', 'Accepted', 2, 2),
('2024-03-05', 'Rejected', 3, 3),
('2024-03-10', 'Pending', 1, 2);

INSERT INTO Users (Username, Password, Role, RefID) VALUES
('admin1', 'password', 'admin', NULL),
('alice_s', 'password', 'student', 1),
('bob_j', 'password', 'student', 2),
('alan_t', 'password', 'faculty', 1),
('ada_l', 'password', 'faculty', 2);
