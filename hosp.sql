-- Create Database if it doesn't exist
CREATE DATABASE IF NOT EXISTS HospitalDB;
USE HospitalDB;

-- User Creation with Varied Privileges
DROP USER IF EXISTS 'admin_user'@'localhost';
DROP USER IF EXISTS 'staff_user'@'localhost';
DROP USER IF EXISTS 'read_only_user'@'localhost';

CREATE USER 'admin_user'@'localhost' IDENTIFIED BY 'admin_pass';
GRANT ALL PRIVILEGES ON HospitalDB.* TO 'admin_user'@'localhost';

CREATE USER 'staff_user'@'localhost' IDENTIFIED BY 'staff_pass';
GRANT SELECT, INSERT, UPDATE ON HospitalDB.* TO 'staff_user'@'localhost';

CREATE USER 'read_only_user'@'localhost' IDENTIFIED BY 'readonly_pass';
GRANT SELECT ON HospitalDB.* TO 'read_only_user'@'localhost';

-- Administrator Table
CREATE TABLE IF NOT EXISTS Administrator (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL
);

-- Initial Data for Administrator
INSERT INTO Administrator (username, password)
VALUES ('meg', 'meg')
ON DUPLICATE KEY UPDATE password = 'meg';

-- Groups Table
CREATE TABLE IF NOT EXISTS `groups` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_name VARCHAR(255) NOT NULL,
    description TEXT
);

-- Patient Table (Auto Increment P_ID)
CREATE TABLE IF NOT EXISTS Patient (
  P_ID INT AUTO_INCREMENT PRIMARY KEY,  -- Auto increment P_ID
  name VARCHAR(50) NOT NULL,
  gender VARCHAR(10),
  DOB DATE,
  Age INT,
  symptoms TEXT,  -- Symptoms column added
  address VARCHAR(128),
  phone_no VARCHAR(15),
  blood_group VARCHAR(5),
  insurance VARCHAR(50),
  email VARCHAR(255),
  password VARCHAR(255)
);


-- Doctors Table with AUTO_INCREMENT for D_ID
CREATE TABLE IF NOT EXISTS doctors (
  D_ID INT AUTO_INCREMENT PRIMARY KEY,  -- Ensure D_ID is AUTO_INCREMENT
  name VARCHAR(50) NOT NULL,
  phone_no VARCHAR(15),
  email VARCHAR(255),
  job_title VARCHAR(100),
  degree VARCHAR(100),
  year INT,
  employer VARCHAR(255),
  password VARCHAR(255),
  specialty VARCHAR(50),
  DOB DATE,
  Age INT,
  salary DECIMAL(10, 2)
);


-- Appointment Table
CREATE TABLE IF NOT EXISTS Appointment (
    A_ID INT AUTO_INCREMENT PRIMARY KEY,  -- Auto-increment integer ID
    time DATETIME NOT NULL,               -- Date and Time of Appointment
    notes TEXT,                           -- Additional Notes for Appointment
    status ENUM('Scheduled', 'Concluded', 'Completed', 'Cancelled') DEFAULT 'Scheduled', -- Appointment Status
    P_ID INT NOT NULL,                    -- Patient ID
    D_ID INT NOT NULL,                    -- Doctor ID
    FOREIGN KEY (P_ID) REFERENCES Patient(P_ID) ON DELETE CASCADE, -- Ensure relational integrity
    FOREIGN KEY (D_ID) REFERENCES doctors(D_ID) ON DELETE CASCADE  -- Ensure relational integrity
);



-- Prescription Table
CREATE TABLE IF NOT EXISTS Prescription (
  Pr_ID VARCHAR(20) PRIMARY KEY,
  name VARCHAR(50),
  dosage VARCHAR(50),
  instructions TEXT,
  duration INT
);

-- Bill Table
CREATE TABLE IF NOT EXISTS Bill (
  B_ID VARCHAR(20) PRIMARY KEY,
  date DATE,
  amount DECIMAL(10, 2),
  payment_status ENUM('Completed', 'Yet-to-be-done')
);

-- Relationship Tables

-- Associates doctors (D_ID) with patients (P_ID) to represent the patients who need care from specific doctors.
CREATE TABLE IF NOT EXISTS Needs (
  D_ID INT,
  P_ID INT,  -- P_ID references INT for Patient
  PRIMARY KEY (D_ID, P_ID),
  FOREIGN KEY (D_ID) REFERENCES doctors(D_ID),
  FOREIGN KEY (P_ID) REFERENCES Patient(P_ID)
);

-- Triggers for Patient Table: Before Insert to Update Age Based on DOB
DROP TRIGGER IF EXISTS before_insert_patient;
DELIMITER //
CREATE TRIGGER before_insert_patient
BEFORE INSERT ON Patient
FOR EACH ROW
BEGIN
  IF NEW.DOB IS NOT NULL THEN
    SET NEW.Age = TIMESTAMPDIFF(YEAR, NEW.DOB, CURDATE());
  END IF;
END;
//
DELIMITER ;


-- Trigger to ensure that an appointment cannot have conflicting statuses or be scheduled in the past.
DELIMITER //
CREATE TRIGGER before_insert_appointment
BEFORE INSERT ON Appointment
FOR EACH ROW
BEGIN
    -- Ensure the appointment date is in the future
    IF NEW.time <= NOW() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Appointment cannot be scheduled in the past.';
    END IF;
END;
//
DELIMITER ;

-- Procedure to fetch all appointments for a specific doctor, including details about the patient.
DELIMITER //
CREATE PROCEDURE GetAppointmentsByDoctor (IN doctor_id INT)
BEGIN
    SELECT 
        a.A_ID AS Appointment_ID,
        a.time AS Appointment_Time,
        a.status AS Appointment_Status,
        p.name AS Patient_Name,
        p.phone_no AS Patient_Phone,
        p.email AS Patient_Email,
        a.notes AS Appointment_Notes
    FROM 
        Appointment a
    INNER JOIN 
        Patient p ON a.P_ID = p.P_ID
    WHERE 
        a.D_ID = doctor_id
    ORDER BY 
        a.time ASC;
END;
//
DELIMITER ;



-- Procedure retrieves the list of patients assigned to a specific doctor, including their details.
DELIMITER //
CREATE PROCEDURE GetPatientsByDoctor(IN doctor_id INT)
BEGIN
    SELECT 
        p.P_ID AS Patient_ID,
        p.name AS Patient_Name,
        p.gender AS Gender,
        p.DOB AS Date_of_Birth,
        p.phone_no AS Phone,
        p.email AS Email,
        a.time AS Appointment_Time,
        a.status AS Appointment_Status
    FROM Patient p
    JOIN Appointment a ON p.P_ID = a.P_ID
    WHERE a.D_ID = doctor_id
    ORDER BY a.time DESC;
END //
DELIMITER ;




-- Sample Data Inserts
INSERT INTO doctors (name, phone_no, email, job_title, degree, year, employer, password, specialty, DOB, Age, salary)
VALUES ('Dr. John Doe', '1234567890', 'john.doe@example.com', 'Cardiologist', 'MD', 2000, 'City Hospital', 'hashed_password', 'Cardiology', '1975-01-01', 46, 200000.00)
ON DUPLICATE KEY UPDATE name = VALUES(name);


-- Insert Data into Patient Table
INSERT INTO Patient (name, gender, DOB, symptoms, address, phone_no, blood_group, insurance, email, password)
VALUES ('John Smith', 'Male', '1990-05-15', 'Fever, Cough', '123 Main St', '5551234567', 'O+', 'Aetna', 'johnsmith@example.com', 'hashed_password')
ON DUPLICATE KEY UPDATE name = VALUES(name);
