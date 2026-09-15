CREATE DATABASE BosowaBerlianMotor;
USE BosowaBerlianMotor;

-- Tabel Pelanggan
CREATE TABLE Customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    date_registered DATE
);

-- Tabel Kendaraan
CREATE TABLE Vehicles (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    brand VARCHAR(50),
    model VARCHAR(50),
    year INT,
    price DECIMAL(12,2),
    stock_quantity INT
);

-- Tabel Dealer (Cabang Bosowa Berlian Motor)
CREATE TABLE Dealers (
    dealer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    location TEXT,
    phone VARCHAR(20)
);

-- Tabel Karyawan
CREATE TABLE Employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    position VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    dealer_id INT,
    FOREIGN KEY (dealer_id) REFERENCES Dealers(dealer_id) ON DELETE SET NULL
);

-- Tabel Penjualan Mobil
CREATE TABLE Sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    vehicle_id INT,
    dealer_id INT,
    employee_id INT,
    sale_date DATE,
    quantity INT,
    total_price DECIMAL(12,2),
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicles(vehicle_id) ON DELETE CASCADE,
    FOREIGN KEY (dealer_id) REFERENCES Dealers(dealer_id) ON DELETE SET NULL,
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id) ON DELETE SET NULL
);

-- Tabel Servis Kendaraan
CREATE TABLE ServiceRecords (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    vehicle_id INT,
    service_date DATE,
    service_type VARCHAR(100),
    cost DECIMAL(12,2),
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicles(vehicle_id) ON DELETE CASCADE
);
