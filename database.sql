-- Drop existing Database if it exists
DROP DATABASE IF EXISTS landscaping_platform;

-- Create the database
CREATE DATABASE landscaping_platform;

-- Use the newly created database
USE landscaping_platform;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS Payments;
DROP TABLE IF EXISTS Invoices;
DROP TABLE IF EXISTS Schedules;
DROP TABLE IF EXISTS Materials;
DROP TABLE IF EXISTS Services;
DROP TABLE IF EXISTS Projects;
DROP TABLE IF EXISTS landscaperstable;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS Administrator;
DROP TABLE IF EXISTS LandscaperMaterials;

-- Create materials table
CREATE TABLE Materials (
    MaterialID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100),
    Quantity INT,
    Price DECIMAL(10, 2)
);

-- Create customers table
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    zipcode VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create landscapers table
CREATE TABLE landscaperstable (
    id INT AUTO_INCREMENT PRIMARY KEY,
    business_name VARCHAR(255),
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    services_offered TEXT,
    address TEXT NOT NULL,
    zipcode VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Administrator table
CREATE TABLE Administrator (
    AdminID INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(20) NOT NULL,
    position VARCHAR(100) NOT NULL
);

-- Insert only one admin in Administrator table
INSERT INTO Administrator (full_name, email, phone_number, position) VALUES
('Ashfaq Ahmed', 'ashfaqahmed011@gmail.com', '+1 (516) 805-5283', 'Admin');

-- Create Services table and link to Landscapers
CREATE TABLE services (
    ServiceID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100),
    Description TEXT,
    Price DECIMAL(10, 2),
    LandscaperID INT,
    FOREIGN KEY (LandscaperID) REFERENCES landscaperstable(id) ON DELETE CASCADE
);

-- Create Projects table
CREATE TABLE projects (
    ProjectID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT,
    zipcode VARCHAR(10) NOT NULL,
    AdminID INT,
    StartDate DATE,
    EndDate DATE,
    Status VARCHAR(50),
    FOREIGN KEY (CustomerID) REFERENCES customers(id),
    FOREIGN KEY (AdminID) REFERENCES Administrator(AdminID)
);

-- Create Invoices table
CREATE TABLE invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    landscaper_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status ENUM('Pending', 'Paid') DEFAULT 'Pending',
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (landscaper_id) REFERENCES landscaperstable(id)
);

CREATE TABLE invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    landscaper_id INT NOT NULL,
    customer_id INT NOT NULL,
    work_description TEXT NOT NULL,
    logo VARCHAR(255),
    attachment VARCHAR(255),
    total_amount DECIMAL(10, 2) NOT NULL,
    status ENUM('Pending', 'Rejected', 'Approved', 'Paid') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (landscaper_id) REFERENCES landscaperstable(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Create Payments table
CREATE TABLE Payments (
    PaymentID INT PRIMARY KEY AUTO_INCREMENT,
    InvoiceID INT,
    DateReceived DATE,
    Amount DECIMAL(10, 2),
    FOREIGN KEY (InvoiceID) REFERENCES Invoices(InvoiceID) ON DELETE CASCADE
);

-- Create Schedules table
CREATE TABLE Schedules (
    ScheduleID INT PRIMARY KEY AUTO_INCREMENT,
    LandscaperID INT,
    ProjectID INT,
    Date DATE,
    Task VARCHAR(255),
    FOREIGN KEY (LandscaperID) REFERENCES landscaperstable(id) ON DELETE CASCADE,
    FOREIGN KEY (ProjectID) REFERENCES projects(ProjectID) ON DELETE CASCADE
);

-- Create LandscaperMaterials table to link materials and landscapers
CREATE TABLE LandscaperMaterials (
    LandscaperID INT,
    MaterialID INT,
    PRIMARY KEY (LandscaperID, MaterialID),
    FOREIGN KEY (LandscaperID) REFERENCES landscaperstable(id) ON DELETE CASCADE,
    FOREIGN KEY (MaterialID) REFERENCES Materials(MaterialID) ON DELETE CASCADE
);

CREATE TABLE requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    landscaper_id INT,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    landscaper_id INT NOT NULL,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (landscaper_id) REFERENCES landscaperstable(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES landscaperstable(id) ON DELETE CASCADE
);


-- Insert sample data into customers table
INSERT INTO customers (full_name, email, phone_number, password, address, zipcode) VALUES
('Ahmed', 'ahmed12@gmail.com', '+914565676739', 'password123', '123 Main St', '11203'),
('Test User1', 'user1@gmail.com', '+1(123)456-9090', 'password123', '456 Second St', '11580'),
('Test User2', 'user2@gmail.com', '+1(198)567-8900', 'password123', '789 Third St', '11590');

-- Insert sample data into landscapers table
INSERT INTO landscaperstable (business_name, email, phone_number, password, services_offered, address, zipcode) VALUES
('Green Lawn Services', 'shujath@gmail.com', '+911234567890', 'password123', 'Lawn Mowing, Garden Cleanup','124 Shatter St', '11203'),
('Rahman Landscaping', 'abdulgmail.com', '1(123)4567890', 'password123', 'Landscape Design', '457 Hyde way St', '11580'),
('Khubaib’s Garden Services', 'khubaib@gmail.com', '1(234)5678910', 'password123', 'Garden Cleanup, Lawn Mowing', '792 Eve Pl', '11590'),
('Ahmed’s Landscaping', 'ahmed1@gmail.com', '1(123)4560011', 'password123', 'Lawn Mowing, Landscape Design', '10 New Ave', '11590');

-- Insert sample data into Services table with link to landscapers
INSERT INTO services (Name, Description, Price, LandscaperID) VALUES
('Lawn Mowing', 'Mowing the lawn and trimming the edges', 50.00, 1),
('Garden Cleanup', 'Removing weeds and dead plants, pruning', 75.00, 2),
('Landscape Design', 'Designing a new landscape layout', 200.00, 3);

-- Insert sample data into Materials table
INSERT INTO Materials (Name, Quantity, Price) VALUES
('Grass Seed', 10, 15.00),
('Mulch', 5, 20.00),
('Fertilizer', 8, 10.00);

-- Insert sample data into LandscaperMaterials table
INSERT INTO LandscaperMaterials (LandscaperID, MaterialID) VALUES
(1, 1),  -- Landscaper 1 (Green Lawn Services) uses Material 1 (Grass Seed)
(2, 2),  -- Landscaper 2 (Rahman Landscaping) uses Material 2 (Mulch)
(3, 3);  -- Landscaper 3 (Khubaib’s Garden Services) uses Material 3 (Fertilizer)

-- Insert sample data into Projects table
INSERT INTO projects (CustomerID, zipcode, AdminID, StartDate, EndDate, Status) VALUES
(1, 11203, 1, '2024-07-01', '2024-07-15', 'Pending'),
(2, 11203, 1, '2024-07-05', '2024-07-20', 'In Progress'),
(3, 11203, 1, '2024-07-10', '2024-07-25', 'Completed');

-- Insert sample data into Invoices table
INSERT INTO Invoices (ProjectID, DateIssued, TotalAmount) VALUES
(1, '2024-07-15', 150.00),
(2, '2024-07-20', 300.00),
(3, '2024-07-25', 250.00);

-- Insert sample data into Payments table
INSERT INTO Payments (InvoiceID, DateReceived, Amount) VALUES
(1, '2024-07-16', 150.00),
(2, '2024-07-21', 300.00),
(3, '2024-07-26', 250.00);

-- Insert sample data into Schedules table
INSERT INTO Schedules (LandscaperID, ProjectID, Date, Task) VALUES
(1, 1, '2024-07-01', 'Lawn Mowing'),
(2, 2, '2024-07-05', 'Garden Cleanup'),
(3, 3, '2024-07-10', 'Landscape Design');

-- Display the contents of each table
SELECT * FROM customers;
SELECT * FROM projects;
SELECT * FROM services;
SELECT * FROM landscaperstable;
SELECT * FROM Administrator;
SELECT * FROM Invoices;
SELECT * FROM Payments;
SELECT * FROM Materials;
SELECT * FROM Schedules;
SELECT * FROM LandscaperMaterials;
SELECT * FROM requests;
SELECT * FROM chat;

/*SELECT * FROM customers;

select *from chat;

desc chat;
drop table invoices;
desc invoices;

select *from invoices;

alter table invoices drop foreign key ProjectID;


Truncate table chat;
Truncate table requests;
Truncate table invoices;

delete from invoices where customer_id='5' ; */
