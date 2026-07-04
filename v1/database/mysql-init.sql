-- Create Database
CREATE DATABASE IF NOT EXISTS `gps_tracker` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `gps_tracker`;

-- 1. Countries Table
CREATE TABLE IF NOT EXISTS `countries` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `country_code` VARCHAR(10) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. States Table
CREATE TABLE IF NOT EXISTS `states` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `state_code` VARCHAR(10) NOT NULL,
    `country_id` INT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_states_country_id` (`country_id`)
) ENGINE=InnoDB;

-- 3. Cities Table
CREATE TABLE IF NOT EXISTS `cities` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `state_id` INT NOT NULL,
    `country_id` INT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_cities_state_id` (`state_id`),
    INDEX `idx_cities_country_id` (`country_id`)
) ENGINE=InnoDB;

-- 4. organizations Table
CREATE TABLE IF NOT EXISTS `organizations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(150) NOT NULL,
    `status` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '0: Inactive, 1: Active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 4. Branches Table
CREATE TABLE IF NOT EXISTS `branches` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `org_id` INT NOT NULL,
    `name` VARCHAR(150) NOT NULL,
    `address_line_1` VARCHAR(255) NOT NULL,
    `address_line_2` VARCHAR(255) DEFAULT NULL,
    `pincode` VARCHAR(20) NOT NULL,
    `country_id` INT NOT NULL,
    `state_id` INT NOT NULL,
    `city_id` INT DEFAULT NULL,
    `is_head_office` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '0: No, 1: Yes',
    `mobile` VARCHAR(20) NOT NULL,
    `phone` VARCHAR(20) DEFAULT NULL,
    `status` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '0: Inactive, 1: Active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_branches_org_id` (`org_id`),
    INDEX `idx_branches_country_id` (`country_id`),
    INDEX `idx_branches_state_id` (`state_id`),
    INDEX `idx_branches_city_id` (`city_id`)
) ENGINE=InnoDB;

-- 5. Roles Table
CREATE TABLE IF NOT EXISTS `roles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL UNIQUE,
    `status` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '0: Inactive, 1: Active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 6. Users Table
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(150) NOT NULL UNIQUE,
    `mobile` VARCHAR(20) NOT NULL,
    `branch_id` INT NOT NULL,
    `role_id` INT NOT NULL,
    `address_line_1` VARCHAR(255) DEFAULT NULL,
    `address_line_2` VARCHAR(255) DEFAULT NULL,
    `pincode` VARCHAR(20) DEFAULT NULL,
    `country_id` INT NOT NULL,
    `state_id` INT NOT NULL,
    `city_id` INT DEFAULT NULL,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL, -- Length 255 to support secure hashing (e.g. bcrypt)
    `status` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '0: Inactive, 1: Active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_users_branch_id` (`branch_id`),
    INDEX `idx_users_role_id` (`role_id`),
    INDEX `idx_users_country_id` (`country_id`),
    INDEX `idx_users_state_id` (`state_id`),
    INDEX `idx_users_city_id` (`city_id`)
) ENGINE=InnoDB;

-- 7. Permissions Table
CREATE TABLE IF NOT EXISTS `permissions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `permission_key` VARCHAR(100) NOT NULL UNIQUE,
    `description` TEXT DEFAULT NULL,
    `status` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '0: Inactive, 1: Active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 8. Role Permissions Table (Composite Primary Key Setup)
CREATE TABLE IF NOT EXISTS `role_permissions` (
    `role_id` INT NOT NULL,
    `permission_id` INT NOT NULL,
    PRIMARY KEY (`role_id`, `permission_id`),
    INDEX `idx_rp_role_id` (`role_id`),
    INDEX `idx_rp_permission_id` (`permission_id`)
) ENGINE=InnoDB;

-- 9. Cards Table (GPS Tracking Devices)
CREATE TABLE IF NOT EXISTS `cards` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `imei_number` VARCHAR(50) NOT NULL UNIQUE,
    `sim_mobile` VARCHAR(20) NOT NULL,
    `company` VARCHAR(100) DEFAULT NULL,
    `model` VARCHAR(100) DEFAULT NULL,
    `status` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '0: Inactive, 1: Active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 10. Card Members Table
CREATE TABLE IF NOT EXISTS `card_members` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(150) DEFAULT NULL,
    `mobile` VARCHAR(20) NOT NULL,
    `branch_id` INT NOT NULL,
    `address_line_1` VARCHAR(255) DEFAULT NULL,
    `address_line_2` VARCHAR(255) DEFAULT NULL,
    `pincode` VARCHAR(20) DEFAULT NULL,
    `country_id` INT NOT NULL,
    `state_id` INT NOT NULL,
    `city_id` INT DEFAULT NULL,
    `card_id` INT DEFAULT NULL UNIQUE, -- Unique because one card belongs to one member at a time
    `emergency_contact_1` VARCHAR(20) NOT NULL,
    `emergency_contact_2` VARCHAR(20) DEFAULT NULL,
    `emergency_contact_3` VARCHAR(20) DEFAULT NULL,
    `status` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '0: Inactive, 1: Active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_members_branch_id` (`branch_id`),
    INDEX `idx_members_country_id` (`country_id`),
    INDEX `idx_members_state_id` (`state_id`),
    INDEX `idx_members_city_id` (`city_id`),
    INDEX `idx_members_card_id` (`card_id`)
) ENGINE=InnoDB;

-- 11. Locations Table
CREATE TABLE IF NOT EXISTS `locations` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `card_id` INT NOT NULL,
    `lat` DECIMAL(10, 8) NOT NULL COMMENT 'Latitude coordinate',
    `lng` DECIMAL(11, 8) NOT NULL COMMENT 'Longitude coordinate',
    `speed` DECIMAL(5, 2) DEFAULT 0.00 COMMENT 'Speed in km/h or mph',
    `battery` TINYINT DEFAULT NULL COMMENT 'Battery percentage remaining',
    `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `sos_button_pressed` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '0: No, 1: Yes',
    INDEX `idx_locations_card_id` (`card_id`)
) ENGINE=InnoDB;

-- Create Index on location timestamps for optimized querying
CREATE INDEX `idx_locations_card_timestamp` ON `locations` (`card_id`, `timestamp` DESC);


-- ========================================================
-- Seed Initial Required Data
-- ========================================================

INSERT INTO `roles` (`name`, `status`) VALUES
('Super User', 1),
('Org Admin', 1),
('Branch Admin', 1),
('End User', 1);

-- Seed Countries
INSERT INTO `countries` (`id`, `name`, `country_code`) VALUES
(1, 'India', 'IN');

-- Seed States (Indian States & Union Territories)
INSERT INTO `states` (`id`, `name`, `state_code`, `country_id`) VALUES
(1, 'Andhra Pradesh', 'AP', 1),
(2, 'Arunachal Pradesh', 'AR', 1),
(3, 'Assam', 'AS', 1),
(4, 'Bihar', 'BR', 1),
(5, 'Chhattisgarh', 'CG', 1),
(6, 'Goa', 'GA', 1),
(7, 'Gujarat', 'GJ', 1),
(8, 'Haryana', 'HR', 1),
(9, 'Himachal Pradesh', 'HP', 1),
(10, 'Jharkhand', 'JH', 1),
(11, 'Karnataka', 'KA', 1),
(12, 'Kerala', 'KL', 1),
(13, 'Madhya Pradesh', 'MP', 1),
(14, 'Maharashtra', 'MH', 1),
(15, 'Manipur', 'MN', 1),
(16, 'Meghalaya', 'ML', 1),
(17, 'Mizoram', 'MZ', 1),
(18, 'Nagaland', 'NL', 1),
(19, 'Odisha', 'OD', 1),
(20, 'Punjab', 'PB', 1),
(21, 'Rajasthan', 'RJ', 1),
(22, 'Sikkim', 'SK', 1),
(23, 'Tamil Nadu', 'TN', 1),
(24, 'Telangana', 'TG', 1),
(25, 'Tripura', 'TR', 1),
(26, 'Uttar Pradesh', 'UP', 1),
(27, 'Uttarakhand', 'UK', 1),
(28, 'West Bengal', 'WB', 1),
(29, 'Andaman and Nicobar Islands', 'AN', 1),
(30, 'Chandigarh', 'CH', 1),
(31, 'Dadra and Nagar Haveli and Daman and Diu', 'DD', 1),
(32, 'Delhi', 'DL', 1),
(33, 'Jammu and Kashmir', 'JK', 1),
(34, 'Ladakh', 'LA', 1),
(35, 'Lakshadweep', 'LD', 1),
(36, 'Puducherry', 'PY', 1);

-- Seed Cities (Major Indian Cities)
-- State IDs reference: 1=AP, 2=AR, 3=AS, 4=BR, 5=CG, 6=GA, 7=GJ, 8=HR, 9=HP, 10=JH,
-- 11=KA, 12=KL, 13=MP, 14=MH, 15=MN, 16=ML, 17=MZ, 18=NL, 19=OD, 20=PB,
-- 21=RJ, 22=SK, 23=TN, 24=TG, 25=TR, 26=UP, 27=UK, 28=WB, 29=AN, 30=CH,
-- 31=DD, 32=DL, 33=JK, 34=LA, 35=LD, 36=PY
INSERT INTO `cities` (`id`, `name`, `state_id`, `country_id`) VALUES
-- Andhra Pradesh (1)
(1, 'Visakhapatnam', 1, 1),
(2, 'Vijayawada', 1, 1),
(3, 'Guntur', 1, 1),
(4, 'Tirupati', 1, 1),
-- Assam (3)
(5, 'Guwahati', 3, 1),
-- Bihar (4)
(6, 'Patna', 4, 1),
(7, 'Gaya', 4, 1),
-- Chhattisgarh (5)
(8, 'Raipur', 5, 1),
(9, 'Bhilai', 5, 1),
-- Goa (6)
(10, 'Panaji', 6, 1),
(11, 'Margao', 6, 1),
-- Gujarat (7)
(12, 'Ahmedabad', 7, 1),
(13, 'Surat', 7, 1),
(14, 'Vadodara', 7, 1),
(15, 'Rajkot', 7, 1),
(16, 'Gandhinagar', 7, 1),
-- Haryana (8)
(17, 'Gurugram', 8, 1),
(18, 'Faridabad', 8, 1),
(19, 'Karnal', 8, 1),
-- Himachal Pradesh (9)
(20, 'Shimla', 9, 1),
(21, 'Manali', 9, 1),
-- Jharkhand (10)
(22, 'Ranchi', 10, 1),
(23, 'Jamshedpur', 10, 1),
-- Karnataka (11)
(24, 'Bengaluru', 11, 1),
(25, 'Mysuru', 11, 1),
(26, 'Mangaluru', 11, 1),
(27, 'Hubli', 11, 1),
-- Kerala (12)
(28, 'Thiruvananthapuram', 12, 1),
(29, 'Kochi', 12, 1),
(30, 'Kozhikode', 12, 1),
-- Madhya Pradesh (13)
(31, 'Bhopal', 13, 1),
(32, 'Indore', 13, 1),
(33, 'Jabalpur', 13, 1),
(34, 'Gwalior', 13, 1),
-- Maharashtra (14)
(35, 'Mumbai', 14, 1),
(36, 'Pune', 14, 1),
(37, 'Nagpur', 14, 1),
(38, 'Nashik', 14, 1),
(39, 'Aurangabad', 14, 1),
(40, 'Thane', 14, 1),
(41, 'Navi Mumbai', 14, 1),
-- Odisha (19)
(42, 'Bhubaneswar', 19, 1),
(43, 'Cuttack', 19, 1),
-- Punjab (20)
(44, 'Ludhiana', 20, 1),
(45, 'Amritsar', 20, 1),
(46, 'Jalandhar', 20, 1),
-- Rajasthan (21)
(47, 'Jaipur', 21, 1),
(48, 'Jodhpur', 21, 1),
(49, 'Udaipur', 21, 1),
(50, 'Kota', 21, 1),
-- Tamil Nadu (23)
(51, 'Chennai', 23, 1),
(52, 'Coimbatore', 23, 1),
(53, 'Madurai', 23, 1),
(54, 'Salem', 23, 1),
-- Telangana (24)
(55, 'Hyderabad', 24, 1),
(56, 'Warangal', 24, 1),
(57, 'Secunderabad', 24, 1),
-- Uttar Pradesh (26)
(58, 'Lucknow', 26, 1),
(59, 'Noida', 26, 1),
(60, 'Agra', 26, 1),
(61, 'Varanasi', 26, 1),
(62, 'Kanpur', 26, 1),
(63, 'Prayagraj', 26, 1),
(64, 'Ghaziabad', 26, 1),
-- Uttarakhand (27)
(65, 'Dehradun', 27, 1),
(66, 'Haridwar', 27, 1),
-- West Bengal (28)
(67, 'Kolkata', 28, 1),
(68, 'Howrah', 28, 1),
(69, 'Durgapur', 28, 1),
-- Chandigarh (30)
(70, 'Chandigarh', 30, 1),
-- Delhi (32)
(71, 'New Delhi', 32, 1),
-- Jammu and Kashmir (33)
(72, 'Srinagar', 33, 1),
(73, 'Jammu', 33, 1),
-- Ladakh (34)
(74, 'Leh', 34, 1),
-- Puducherry (36)
(75, 'Puducherry', 36, 1);

INSERT INTO `users` (`id`, `name`, `email`, `mobile`, `branch_id`, `role_id`, `address_line_1`, `address_line_2`, `pincode`, `country_id`, `state_id`, `city_id`, `username`, `password`, `status`, `created_at`, `updated_at`) VALUES
(1, 'admin', 'admin@email.com', '4565768798', 0, 1, 'string', 'string', '412308', 1, 14, 36, 'admin', '$2b$13$336oUAFra1cg8hzxsSf.6eY9lr6uBGRvCwIXe5wFA/OX2Jhub2n4y', 1, '2026-05-29 18:01:20', '2026-05-29 18:01:20');
