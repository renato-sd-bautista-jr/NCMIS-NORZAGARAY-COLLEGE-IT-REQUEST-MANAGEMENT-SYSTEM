-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 23, 2025 at 10:18 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ncmis`
--

-- --------------------------------------------------------

--
-- Table structure for table `borrow_requests`
--

CREATE TABLE `borrow_requests` (
  `borrow_id` int(11) NOT NULL,
  `student_id` varchar(20) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `middle_initial` varchar(5) DEFAULT NULL,
  `device_id` int(11) NOT NULL,
  `borrow_date` date NOT NULL,
  `return_date` date DEFAULT NULL,
  `reason` text NOT NULL,
  `status` enum('Pending','Approved','Returned') DEFAULT 'Pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `borrow_requests`
--

INSERT INTO `borrow_requests` (`borrow_id`, `student_id`, `last_name`, `first_name`, `middle_initial`, `device_id`, `borrow_date`, `return_date`, `reason`, `status`) VALUES
(8, '2021-0442', 'Bautista', 'Renato', 'SD', 4, '2025-09-29', '2025-09-29', 're', 'Returned'),
(9, '2021-0442', 'Bautista', 'Renato', 'SD', 1, '2025-09-29', NULL, '33', 'Pending');

-- --------------------------------------------------------

--
-- Table structure for table `concerns`
--

CREATE TABLE `concerns` (
  `concern_id` int(11) NOT NULL,
  `description` text NOT NULL,
  `status` enum('Pending','Ongoing','Resolved') DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `resolution_feedback` text DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `concerns`
--

INSERT INTO `concerns` (`concern_id`, `description`, `status`, `created_at`, `updated_at`, `resolution_feedback`, `user_id`) VALUES
(13, 'sadadadwa', 'Pending', '2025-03-24 09:26:15', '2025-03-24 09:26:15', NULL, 10),
(17, 'sdadawdadwad', 'Pending', '2025-03-24 10:16:17', '2025-03-24 10:16:17', NULL, 9);

-- --------------------------------------------------------

--
-- Table structure for table `concern_devices`
--

CREATE TABLE `concern_devices` (
  `concern_id` int(11) NOT NULL,
  `device_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `concern_devices`
--

INSERT INTO `concern_devices` (`concern_id`, `device_id`) VALUES
(13, 1),
(17, 1);

-- --------------------------------------------------------

--
-- Table structure for table `concern_history`
--

CREATE TABLE `concern_history` (
  `id` int(11) NOT NULL,
  `concern_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `description` text NOT NULL,
  `status` enum('Pending','Ongoing','Resolved') NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `resolution_feedback` text NOT NULL,
  `faculty_name` varchar(255) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `devices` text DEFAULT NULL,
  `archived_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `concern_history`
--

INSERT INTO `concern_history` (`id`, `concern_id`, `user_id`, `description`, `status`, `created_at`, `updated_at`, `resolution_feedback`, `faculty_name`, `email`, `devices`, `archived_at`) VALUES
(6, 9, 0, 'adadawdawd', 'Resolved', '2025-03-24 17:10:54', '2025-03-24 17:11:04', 'dadawdadawdad', 'auro', 'matthewjohnsantos2004@gmail.com', '[{\"device_name\":\"PC2\",\"department_name\":\"Dean\'s Office\"}]', '2025-03-24 09:11:11'),
(7, 14, 9, 'adadadwa', 'Resolved', '2025-03-24 17:26:20', '2025-03-24 17:26:48', 'adadwadad', 'me', 'matthewjohnsantos143@gmail.com', '[{\"device_name\":\"PC1\",\"department_name\":\"Dean\'s Office\"}]', '2025-03-24 09:27:10'),
(8, 11, 0, 'fasfadfwa', 'Resolved', '2025-03-24 17:25:27', '2025-03-24 18:06:46', 'sdadwadadw', 'auro', 'matthewjohnsantos2004@gmail.com', '[{\"device_name\":\"PC1\",\"department_name\":\"Dean\'s Office\"}]', '2025-03-24 10:06:49'),
(9, 12, 9, 'adadadad', 'Resolved', '2025-03-24 17:25:32', '2025-03-24 18:15:28', 'adadawdad', 'auro', 'matthewjohnsantos2004@gmail.com', '[{\"device_name\":\"PC1\",\"department_name\":\"Dean\'s Office\"}]', '2025-03-24 10:15:31'),
(10, 16, 9, 'dadawdawdawdaw', 'Resolved', '2025-03-24 18:16:12', '2025-03-24 18:16:30', 'adadwadaw', 'auro', 'matthewjohnsantos2004@gmail.com', '[{\"device_name\":\"PC1\",\"department_name\":\"Dean\'s Office\"}]', '2025-03-24 10:16:33'),
(11, 15, 10, 'asdadawdadadw', 'Resolved', '2025-03-24 17:26:27', '2025-03-24 18:19:37', 'adadawd', 'me', 'matthewjohnsantos143@gmail.com', '[{\"device_name\":\"PC1\",\"department_name\":\"Dean\'s Office\"},{\"device_name\":\"PC2\",\"department_name\":\"Dean\'s Office\"}]', '2025-03-24 10:19:41'),
(12, 18, 9, 'adadawdawda', 'Resolved', '2025-03-24 18:16:21', '2025-03-24 18:19:58', 'tite', 'auro', 'matthewjohnsantos2004@gmail.com', '[{\"device_name\":\"PC1\",\"department_name\":\"Dean\'s Office\"}]', '2025-03-24 10:20:04'),
(13, 19, 9, 'dadadwadaw', 'Resolved', '2025-03-24 20:42:28', '2025-03-24 20:42:42', 'dadwdadw', 'auro', 'matthewjohnsantos2004@gmail.com', '[{\"device_name\":\"PC1\",\"department_name\":\"Dean\'s Office\"}]', '2025-03-24 12:48:26');

-- --------------------------------------------------------

--
-- Table structure for table `departments`
--

CREATE TABLE `departments` (
  `department_id` int(11) NOT NULL,
  `department_name` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `departments`
--

INSERT INTO `departments` (`department_id`, `department_name`) VALUES
(1, 'Dean\'s Office');

-- --------------------------------------------------------

--
-- Table structure for table `devices`
--

CREATE TABLE `devices` (
  `device_id` int(11) NOT NULL,
  `item_name` varchar(150) NOT NULL,
  `brand_model` varchar(100) DEFAULT NULL,
  `department_id` int(11) NOT NULL,
  `serial_number` varchar(100) DEFAULT NULL,
  `quantity` int(11) DEFAULT 0,
  `device_type` varchar(50) DEFAULT NULL,
  `status` enum('Available','Borrowed','Damaged','Disposed') DEFAULT 'Available'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `devices`
--

INSERT INTO `devices` (`device_id`, `item_name`, `brand_model`, `department_id`, `serial_number`, `quantity`, `device_type`, `status`) VALUES
(1, 'PC1', NULL, 1, NULL, 0, NULL, 'Available'),
(3, 'PC2', NULL, 1, NULL, 0, NULL, 'Available'),
(4, 'Projector', 'Epson EB-X07', 1, 'PRJ-001', 5, 'Electronics', 'Available'),
(5, 'Mouse', 'a4tech', 1, 'm2025', 29, 'Computer accessory', 'Available'),
(6, 'a4Tech Mouse', 'a4Tech', 1, NULL, 1, 'Mouse', 'Available'),
(7, 'inplay keyboard 2', 'inplay', 1, NULL, 1, 'keyboard', 'Available');

-- --------------------------------------------------------

--
-- Table structure for table `devices_full`
--

CREATE TABLE `devices_full` (
  `accession_id` int(11) NOT NULL,
  `device_id` int(11) DEFAULT NULL,
  `item_name` varchar(255) NOT NULL,
  `brand_model` varchar(255) DEFAULT NULL,
  `serial_number` varchar(255) DEFAULT NULL,
  `quantity` int(11) DEFAULT 1,
  `device_type` varchar(255) DEFAULT NULL,
  `department_id` int(11) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'Available',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `devices_full`
--

INSERT INTO `devices_full` (`accession_id`, `device_id`, `item_name`, `brand_model`, `serial_number`, `quantity`, `device_type`, `department_id`, `status`, `created_at`) VALUES
(2, NULL, '3', '1', '1', 1, '1', 1, 'Available', '2025-10-14 17:00:09'),
(3, NULL, 'inplay keyboard 1', 'inplay', '9', 1, 'keyboard', 1, 'Available', '2025-10-14 19:26:41'),
(4, NULL, 'w', 'w', 'w', 1, 'w', 1, 'Available', '2025-10-14 19:32:43'),
(5, NULL, '5', '3', '3', 1, '3', 1, 'Available', '2025-10-14 19:40:21'),
(6, NULL, '4', '54', '5', 1, '5', 1, 'Available', '2025-10-14 19:48:47'),
(7, NULL, 'e', 'Epson EB-X0778e', 'e', 1, 'e', 1, 'Available', '2025-10-14 19:50:30'),
(9, NULL, '55', '333', '66', 1, '22', 1, 'Available', '2025-10-14 19:51:48'),
(10, NULL, '4542', '25235', '23423', 1, '234234', 1, 'Available', '2025-10-14 19:53:10'),
(11, NULL, 'a4Tech Mouse', 'a4Tech', 'm2025', 1, 'Mouse', 1, 'Available', '2025-10-21 17:07:19');

-- --------------------------------------------------------

--
-- Table structure for table `devices_units`
--

CREATE TABLE `devices_units` (
  `accession_id` int(11) NOT NULL,
  `device_id` int(11) NOT NULL,
  `serial_number` varchar(100) DEFAULT NULL,
  `status` enum('Available','Borrowed','Damaged','Disposed') DEFAULT 'Available'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `devices_units`
--

INSERT INTO `devices_units` (`accession_id`, `device_id`, `serial_number`, `status`) VALUES
(1, 4, 'PRJ-001', 'Borrowed'),
(2, 4, 'PRJ-002', 'Available'),
(3, 4, 'PRJ-003', 'Available'),
(4, 4, 'PRJ-004', 'Borrowed'),
(5, 4, 'PRJ-005', 'Available'),
(6, 5, 'm2025', 'Available'),
(7, 5, NULL, 'Available'),
(8, 5, NULL, 'Available'),
(9, 5, NULL, 'Available'),
(10, 5, NULL, 'Available'),
(11, 5, NULL, 'Available'),
(12, 5, NULL, 'Available'),
(13, 5, NULL, 'Available'),
(14, 5, NULL, 'Available'),
(15, 5, NULL, 'Available'),
(16, 5, NULL, 'Available'),
(17, 5, NULL, 'Available'),
(18, 5, NULL, 'Available'),
(19, 5, NULL, 'Available'),
(20, 5, NULL, 'Available'),
(21, 5, NULL, 'Available'),
(22, 5, NULL, 'Available'),
(23, 5, NULL, 'Available'),
(24, 5, NULL, 'Available'),
(25, 5, NULL, 'Available'),
(26, 5, NULL, 'Available'),
(27, 5, NULL, 'Available'),
(28, 5, NULL, 'Available'),
(29, 5, NULL, 'Available'),
(30, 5, NULL, 'Available'),
(31, 5, NULL, 'Available'),
(32, 5, NULL, 'Available'),
(33, 5, NULL, 'Available'),
(34, 5, NULL, 'Available'),
(35, 6, 'M03', 'Available');

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `action` varchar(255) NOT NULL,
  `target_type` varchar(50) DEFAULT NULL,
  `target_id` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `action`, `target_type`, `target_id`, `created_at`) VALUES
(1, 9, 'Added new PC: PC1333 (Serial: SN-0000051)', 'PC', 0, '2025-10-21 19:21:18'),
(2, 9, 'Added new PC: pc418pm (Serial: SN-000001f24)', 'PC', 0, '2025-10-23 08:18:17');

-- --------------------------------------------------------

--
-- Table structure for table `pcinfofull`
--

CREATE TABLE `pcinfofull` (
  `pcid` int(11) NOT NULL,
  `pcname` varchar(255) NOT NULL,
  `department_id` int(11) NOT NULL,
  `location` varchar(255) DEFAULT NULL,
  `quantity` int(11) NOT NULL DEFAULT 1,
  `acquisition_cost` decimal(12,2) DEFAULT NULL,
  `date_acquired` date DEFAULT NULL,
  `accountable` varchar(255) DEFAULT NULL,
  `serial_no` varchar(255) NOT NULL,
  `municipal_serial_no` varchar(255) DEFAULT NULL,
  `status` varchar(100) DEFAULT NULL,
  `note` text DEFAULT NULL,
  `monitor` varchar(255) DEFAULT NULL,
  `motherboard` varchar(255) DEFAULT NULL,
  `ram` varchar(255) DEFAULT NULL,
  `storage` varchar(255) DEFAULT NULL,
  `gpu` varchar(255) DEFAULT NULL,
  `psu` varchar(255) DEFAULT NULL,
  `casing` varchar(255) DEFAULT NULL,
  `other_parts` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pcinfofull`
--

INSERT INTO `pcinfofull` (`pcid`, `pcname`, `department_id`, `location`, `quantity`, `acquisition_cost`, `date_acquired`, `accountable`, `serial_no`, `municipal_serial_no`, `status`, `note`, `monitor`, `motherboard`, `ram`, `storage`, `gpu`, `psu`, `casing`, `other_parts`, `created_at`, `updated_at`) VALUES
(1, 'PC-LAB-01', 1, 'Computer Lab A', 1, 45000.00, '2025-10-20', 'John Doe', 'SN-000001f', 'MUN-000123', 'Active', 'For student usedsss', 'AOC 24-inch', 'ASUS PRIME B450', '16GB DDR4', '512GB SSD', 'GTX 1050 Ti', 'Corsair 500W', 'CoolerMaster', 'WiFi Card', '2025-10-20 07:43:02', '2025-10-20 08:25:02'),
(2, 'PC-LAB-02', 1, 'Computer Lab A', 1, 45000.00, '2025-10-13', 'John Doe', 'SN-000002', 'MUN-000124', 'Active', 'number 2', 'AOC 24-inch', 'ASUS PRIME B450', '16GB DDR4', '512GB SSD', 'GTX 1050 Ti', 'Corsair 500W', 'CoolerMaster', 'yes', '2025-10-20 08:29:07', '2025-10-20 08:29:07'),
(3, 'PC3', 1, 'Computer Lab A', 1, 40000.00, '2025-10-22', 'John Doe', 'SN-000003', 'MUN-000125', 'Active', '3', 'nvision 24\"', 'gigabyte a320m', 'ramsta 8gb', 'ramsta 500gb', 'GTX 1050 Ti', '500wats', 'CoolerMaster', '22', '2025-10-21 17:09:37', '2025-10-21 17:09:37'),
(4, 'PC4', 1, 'Computer Lab A', 1, 50000.00, '2025-10-23', 'John Doe', 'SN-000004', 'MUN-000126', 'Active', '333', 'nvision 24\"', 'gigabyte a320m', 'ramsta 8gb', 'ramsta 500gb', 'GTX 1050 Ti', 'Corsair 500W', 'CoolerMaster', '22', '2025-10-21 17:17:39', '2025-10-21 17:17:39'),
(7, 'PC5', 1, 'Computer Lab A', 1, 30000.00, '2025-10-22', 'John Doe', 'SN-000005', 'MUN-0050126', 'Active', '3', '3', '3', '3', '3', '3', '3', '3', '3', '2025-10-21 17:22:08', '2025-10-21 17:22:08'),
(8, 'PC7', 1, 'Computer Lab A', 1, 50000.00, '2025-10-22', 'John Doe', 'SN-000006', 'MUN-00501263', 'Active', '3333', '4', '4', '4', '4', '2', '3', '1', '2', '2025-10-21 17:24:47', '2025-10-21 17:24:47'),
(9, 'pc8', 1, 'Computer Lab A', 1, 80000.00, '2025-10-22', 'John Doe', 'SN-0000063', 'MUN-005012633', 'Active', '33', 'AOC 24-inch', 'gigabyte a320m', '22', 'ramsta 500gb', 'GTX 1050 Ti', 'Corsair 500W', 'CoolerMaster', 'yes', '2025-10-21 17:27:50', '2025-10-21 17:27:50'),
(10, 'pc9', 1, 'Computer Lab A', 1, 50000.00, '2025-10-22', 'John Doe', 'SN-00000633', 'MUN-0050126331', 'Active', '33', '3', '1', '2', '1', '1', '1', '1', '1', '2025-10-21 17:32:32', '2025-10-21 17:32:32'),
(11, 'pc10', 1, 'it', 1, 3.00, '2025-10-23', '3', 'SN-0000043', 'MUN-0050126321', 'Active', '3', '3', '2', '3', '2', '1', '2', '2', '2', '2025-10-21 17:35:37', '2025-10-21 17:35:37'),
(12, 'PC11', 1, 'Computer Lab A', 1, 333333.00, '0000-00-00', 'John Doe', 'SN-0000021', 'MUN-0001243', 'Active', '3', '3', '4', '3', '4', '3', '1', '2', '2', '2025-10-21 17:37:17', '2025-10-21 17:37:17'),
(13, 'pc12', 1, 'Computer Lab A', 1, 33333.00, '2025-10-22', 'John Doe', 'SN-000001f3', 'MUN-0001254', 'Active', '4', '1', '3', '1', '3', '1', '3', '2', '3', '2025-10-21 17:57:15', '2025-10-21 17:57:15'),
(14, 'PC133', 1, 'Computer Lab A', 1, 33333.00, '2025-10-22', '', 'SN-000001f31', 'MUN-0001252', 'Active', '3', 'yh', 'w', 't', 'w', 't', 'e', 't', 'r', '2025-10-21 17:58:41', '2025-10-21 17:58:41'),
(16, 'PC53', 1, 'Computer Lab A', 1, 333333.00, '2025-10-22', 'John Doe', 'SN-000001f23', 'MUN-00012523', 'Active', '3', 'nvision 24\"', 'gigabyte a320m', 'ramsta 8gb', '4', 'GTX 1050 Ti', 'Corsair 500W', 'CoolerMaster', 'yes', '2025-10-21 18:02:30', '2025-10-21 18:02:30'),
(17, 'PC532', 1, 'Computer Lab A', 1, 333333.00, '2025-10-22', 'John Doe', 'SN-0000052', 'MUN-0001251', 'Active', '32', 's', 's', 's', 's', 's', 's', 's', 's', '2025-10-21 18:09:37', '2025-10-21 18:09:37'),
(20, 'PC1335', 1, 'Computer Lab A', 1, 333.00, '2025-10-22', 'John Doe', 'SN-003', 'MUN-000125221', 'Active', '46', 'qetr', 'qwe', 't', 'wqe', 'wq', 'wqe', 're', 'q', '2025-10-21 19:16:24', '2025-10-21 19:16:24'),
(21, 'PC1333', 1, 'Computer Lab A', 1, 3333333.00, '2025-10-22', 'John Doe', 'SN-0000051', 'MUN-00012524', 'Active', '4', '2', '23', '213', '23', '213', '23', '213', '23', '2025-10-21 19:21:18', '2025-10-21 19:21:18'),
(22, 'pc418pm', 1, 'it', 1, 43333.00, '2025-10-23', 'John Doe', 'SN-000001f24', 'MUN-0001252244', 'Active', '2', 'qetr', 'qwe', 't', 'ramsta 500gb', 'wq', 'Corsair 500W', 'CoolerMaster', '2', '2025-10-23 08:18:17', '2025-10-23 08:18:17');

--
-- Triggers `pcinfofull`
--
DELIMITER $$
CREATE TRIGGER `before_insert_pcinfofull` BEFORE INSERT ON `pcinfofull` FOR EACH ROW BEGIN
  DECLARE next_id INT;
  IF NEW.serial_no IS NULL OR NEW.serial_no = '' THEN
    SELECT IFNULL(MAX(pcid), 0) + 1 INTO next_id FROM pcinfofull;
    SET NEW.serial_no = CONCAT('SN-', LPAD(next_id, 6, '0'));
  END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `pcparts`
--

CREATE TABLE `pcparts` (
  `part_id` int(11) NOT NULL,
  `pcid` varchar(50) NOT NULL,
  `monitor` varchar(100) DEFAULT NULL,
  `motherboard` varchar(100) DEFAULT NULL,
  `ram` varchar(100) DEFAULT NULL,
  `storage` varchar(100) DEFAULT NULL,
  `gpu` varchar(100) DEFAULT NULL,
  `psu` varchar(100) DEFAULT NULL,
  `casing` varchar(100) DEFAULT NULL,
  `other_parts` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pcparts`
--

INSERT INTO `pcparts` (`part_id`, `pcid`, `monitor`, `motherboard`, `ram`, `storage`, `gpu`, `psu`, `casing`, `other_parts`) VALUES
(4, '1', '33', '222', '22', '22', '22', '22', '22', '22'),
(7, 'PC-953FF49C', '1', '1', '1', '1', '1', '1', '1', '1'),
(8, 'PC-30143C90', '7', '7', '66', '5', '4', '4', '3', 'e');

-- --------------------------------------------------------

--
-- Table structure for table `pcs`
--

CREATE TABLE `pcs` (
  `pcid` varchar(50) NOT NULL,
  `pcname` varchar(100) NOT NULL,
  `department_id` int(11) NOT NULL,
  `status` enum('Active','In Repair','Decommissioned') DEFAULT 'Active',
  `note` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pcs`
--

INSERT INTO `pcs` (`pcid`, `pcname`, `department_id`, `status`, `note`) VALUES
('1', 'PC1', 1, 'Active', '3'),
('PC-30143C90', '66', 1, 'Active', '88'),
('PC-953FF49C', '2', 1, 'Active', '1');

-- --------------------------------------------------------

--
-- Table structure for table `students`
--

CREATE TABLE `students` (
  `student_id` varchar(20) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `middle_initial` varchar(5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`student_id`, `last_name`, `first_name`, `middle_initial`) VALUES
('2021-0442', 'Bautista', 'Renato', 'SD');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(10) UNSIGNED NOT NULL,
  `username` varchar(50) NOT NULL,
  `faculty_name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `is_admin` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `faculty_name`, `email`, `password`, `is_admin`, `created_at`, `updated_at`) VALUES
(9, 'admin', 'auro', 'matthewjohnsantos2004@gmail.com', '$2y$10$nvmP/E2tXSJ3zYIOp2Z.iu29/gNxPA/pmF/iZOiJoijB.k48zCj22', 1, '2025-03-24 02:34:16', '2025-03-24 02:49:06'),
(10, 'user', 'me', 'matthewjohnsantos143@gmail.com', '$2y$10$3HWZONw6vWb8WNkqsDA3ReMbUiyuvdqP.MSWD2CuFdrN4UDfVtNSG', 0, '2025-03-24 09:25:58', '2025-03-24 09:25:58');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `borrow_requests`
--
ALTER TABLE `borrow_requests`
  ADD PRIMARY KEY (`borrow_id`),
  ADD KEY `fk_borrow_device` (`device_id`);

--
-- Indexes for table `concerns`
--
ALTER TABLE `concerns`
  ADD PRIMARY KEY (`concern_id`);

--
-- Indexes for table `concern_devices`
--
ALTER TABLE `concern_devices`
  ADD PRIMARY KEY (`concern_id`,`device_id`),
  ADD KEY `device_id` (`device_id`);

--
-- Indexes for table `concern_history`
--
ALTER TABLE `concern_history`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `departments`
--
ALTER TABLE `departments`
  ADD PRIMARY KEY (`department_id`);

--
-- Indexes for table `devices`
--
ALTER TABLE `devices`
  ADD PRIMARY KEY (`device_id`),
  ADD KEY `department_id` (`department_id`);

--
-- Indexes for table `devices_full`
--
ALTER TABLE `devices_full`
  ADD PRIMARY KEY (`accession_id`),
  ADD UNIQUE KEY `serial_number` (`serial_number`),
  ADD KEY `fk_department` (`department_id`);

--
-- Indexes for table `devices_units`
--
ALTER TABLE `devices_units`
  ADD PRIMARY KEY (`accession_id`),
  ADD KEY `device_id` (`device_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `pcinfofull`
--
ALTER TABLE `pcinfofull`
  ADD PRIMARY KEY (`pcid`),
  ADD UNIQUE KEY `pcname` (`pcname`),
  ADD UNIQUE KEY `serial_no` (`serial_no`),
  ADD UNIQUE KEY `municipal_serial_no` (`municipal_serial_no`),
  ADD KEY `department_id` (`department_id`);

--
-- Indexes for table `pcparts`
--
ALTER TABLE `pcparts`
  ADD PRIMARY KEY (`part_id`),
  ADD KEY `pcid` (`pcid`);

--
-- Indexes for table `pcs`
--
ALTER TABLE `pcs`
  ADD PRIMARY KEY (`pcid`),
  ADD KEY `department_id` (`department_id`);

--
-- Indexes for table `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`student_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `borrow_requests`
--
ALTER TABLE `borrow_requests`
  MODIFY `borrow_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `concerns`
--
ALTER TABLE `concerns`
  MODIFY `concern_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT for table `concern_history`
--
ALTER TABLE `concern_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `departments`
--
ALTER TABLE `departments`
  MODIFY `department_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `devices`
--
ALTER TABLE `devices`
  MODIFY `device_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `devices_full`
--
ALTER TABLE `devices_full`
  MODIFY `accession_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `devices_units`
--
ALTER TABLE `devices_units`
  MODIFY `accession_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `pcinfofull`
--
ALTER TABLE `pcinfofull`
  MODIFY `pcid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `pcparts`
--
ALTER TABLE `pcparts`
  MODIFY `part_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `borrow_requests`
--
ALTER TABLE `borrow_requests`
  ADD CONSTRAINT `fk_borrow_device` FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `concern_devices`
--
ALTER TABLE `concern_devices`
  ADD CONSTRAINT `concern_devices_ibfk_1` FOREIGN KEY (`concern_id`) REFERENCES `concerns` (`concern_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `concern_devices_ibfk_2` FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`);

--
-- Constraints for table `devices`
--
ALTER TABLE `devices`
  ADD CONSTRAINT `devices_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`);

--
-- Constraints for table `devices_full`
--
ALTER TABLE `devices_full`
  ADD CONSTRAINT `fk_department` FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`) ON DELETE SET NULL;

--
-- Constraints for table `devices_units`
--
ALTER TABLE `devices_units`
  ADD CONSTRAINT `devices_units_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`);

--
-- Constraints for table `pcinfofull`
--
ALTER TABLE `pcinfofull`
  ADD CONSTRAINT `pcinfofull_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`);

--
-- Constraints for table `pcparts`
--
ALTER TABLE `pcparts`
  ADD CONSTRAINT `pcparts_ibfk_1` FOREIGN KEY (`pcid`) REFERENCES `pcs` (`pcid`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `pcs`
--
ALTER TABLE `pcs`
  ADD CONSTRAINT `pcs_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
