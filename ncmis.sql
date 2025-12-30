-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 30, 2025 at 11:25 PM
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
-- Table structure for table `asset_maintenance_logs`
--

CREATE TABLE `asset_maintenance_logs` (
  `id` int(11) NOT NULL,
  `asset_type` enum('PC','Device') DEFAULT NULL,
  `asset_id` int(11) DEFAULT NULL,
  `action` varchar(100) DEFAULT NULL,
  `previous_status` varchar(50) DEFAULT NULL,
  `new_status` varchar(50) DEFAULT NULL,
  `performed_by` varchar(255) DEFAULT NULL,
  `performed_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
  `department_name` varchar(100) NOT NULL,
  `department_code` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `departments`
--

INSERT INTO `departments` (`department_id`, `department_name`, `department_code`) VALUES
(1, 'Dean\'s Office', 'DO');

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
  `quantity` int(11) DEFAULT 1,
  `acquisition_cost` decimal(12,2) DEFAULT NULL,
  `date_acquired` date DEFAULT NULL,
  `accountable` varchar(255) DEFAULT NULL,
  `serial_no` varchar(255) NOT NULL,
  `municipal_serial_no` varchar(255) DEFAULT NULL,
  `device_type` varchar(255) DEFAULT NULL,
  `department_id` int(11) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'Available',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `last_checked` date DEFAULT NULL,
  `maintenance_interval_days` int(11) DEFAULT 30,
  `health_score` int(11) DEFAULT 100,
  `risk_level` varchar(20) DEFAULT 'Low'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `devices_full`
--

INSERT INTO `devices_full` (`accession_id`, `device_id`, `item_name`, `brand_model`, `quantity`, `acquisition_cost`, `date_acquired`, `accountable`, `serial_no`, `municipal_serial_no`, `device_type`, `department_id`, `status`, `created_at`, `updated_at`, `last_checked`, `maintenance_interval_days`, `health_score`, `risk_level`) VALUES
(14, NULL, 'Mouse', 'a4Tech', 1, 400.00, '2025-10-25', 'John Doe', 'SN-0103', 'MUN-0001241', 'Mouse', 1, 'Needs Checking', '2025-10-25 13:19:00', '2025-12-26 14:38:28', NULL, 30, 100, 'Medium'),
(15, NULL, 'inplay keyboard 1', 'inplay', 5, 1000.00, '0000-00-00', 'John Doe', 'SN-000001', 'MUN-0001252', 'keynoard', 1, 'Needs Checking', '2025-10-26 02:09:23', '2025-12-26 14:38:28', NULL, 30, 100, 'Medium'),
(16, NULL, 'Epson EB-X08', 'Epson', 1, 3000.00, '2025-10-27', 'John Doe', 'SN-003', 'MUN-000125', 'projector', 1, 'Needs Checking', '2025-10-26 17:13:39', '2025-12-26 14:38:28', NULL, 30, 100, 'Medium'),
(17, NULL, '3', '2', 1, 213321.00, '2025-10-27', '213', '123', '123', '213', 1, 'Needs Checking', '2025-10-27 02:00:09', '2025-12-26 14:38:28', NULL, 30, 100, 'Medium'),
(18, NULL, '4', '3', 1, 3.00, '0000-00-00', '3', '3', '4', '3', 1, 'Needs Checking', '2025-10-27 03:27:22', '2025-12-26 14:38:28', NULL, 30, 100, 'Medium'),
(19, NULL, 'ye', 'ye', 1, 123.00, '0000-00-00', 'ye', 'ye', 'ye', 'ye', 1, 'Needs Checking', '2025-10-27 04:52:19', '2025-12-26 14:38:28', NULL, 30, 100, 'Medium'),
(20, NULL, '123', '123', 1, 123.00, '2025-10-27', '123', 'SN68546784', 'MSN68546858', '123', 1, 'Needs Checking', '2025-10-27 05:08:05', '2025-12-26 14:38:28', NULL, 30, 100, 'Medium'),
(21, NULL, '123', '123', 1, 123.00, '2025-10-27', '123', 'SN70555644', 'MSN70555662', '23', 1, 'Needs Checking', '2025-10-27 05:08:25', '2025-12-26 14:38:28', NULL, 30, 100, 'Medium'),
(22, NULL, '123', '123', 1, 123.00, '2025-10-27', '123', 'SN70555772', 'MSN70555748', '23', 1, 'Needs Checking', '2025-10-27 05:08:25', '2025-12-26 14:38:28', NULL, 30, 100, 'Medium'),
(23, NULL, '123', '123', 1, 123.00, '2025-10-27', '123', 'SN70555841', 'MSN70555872', '23', 1, 'Needs Checking', '2025-10-27 05:08:25', '2025-12-26 14:38:28', NULL, 30, 100, 'Medium'),
(24, NULL, '444', '444', 1, 4444.00, '2025-10-27', '44', 'SN73088694', 'MSN73088666', '4', 1, 'Needs Checking', '2025-10-27 05:08:50', '2025-12-26 14:38:28', NULL, 30, 100, 'Medium'),
(25, NULL, '444', '444', 1, 4444.00, '2025-10-27', '44', 'SN73088849', 'MSN73088823', '4', 1, 'Needs Checking', '2025-10-27 05:08:50', '2025-12-26 14:38:28', NULL, 30, 100, 'Medium'),
(26, NULL, '444', '444', 1, 4444.00, '2025-10-27', '44', 'SN73088928', 'MSN73088926', '4', 1, 'Needs Checking', '2025-10-27 05:08:50', '2025-12-26 14:38:28', NULL, 30, 100, 'Medium'),
(27, NULL, 'e', 'e', 1, 4.00, '2025-10-27', 'e', 'SN73089018', 'MSN73089037', 'e', 1, 'In Used', '2025-10-27 05:08:50', '2025-12-30 22:22:08', '2025-12-30', 30, 100, 'Low');

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
-- Table structure for table `inventory_settings`
--

CREATE TABLE `inventory_settings` (
  `id` int(11) NOT NULL,
  `auto_check_days` int(11) NOT NULL DEFAULT 0,
  `enabled` tinyint(1) DEFAULT 1,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `inventory_status_logs`
--

CREATE TABLE `inventory_status_logs` (
  `id` int(11) NOT NULL,
  `item_type` enum('PC','Device') DEFAULT NULL,
  `item_id` int(11) DEFAULT NULL,
  `old_status` varchar(50) DEFAULT NULL,
  `new_status` varchar(50) DEFAULT NULL,
  `changed_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `maintenance_history`
--

CREATE TABLE `maintenance_history` (
  `id` int(11) NOT NULL,
  `pcid` int(11) DEFAULT NULL,
  `asset_type` enum('PC','Device') NOT NULL,
  `asset_id` int(11) NOT NULL,
  `action` varchar(100) NOT NULL,
  `remarks` text DEFAULT NULL,
  `performed_by` varchar(255) DEFAULT NULL,
  `old_status` varchar(100) DEFAULT NULL,
  `new_status` varchar(100) DEFAULT NULL,
  `risk_level` varchar(20) DEFAULT NULL,
  `health_score` int(11) DEFAULT NULL,
  `performed_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `maintenance_history`
--

INSERT INTO `maintenance_history` (`id`, `pcid`, `asset_type`, `asset_id`, `action`, `remarks`, `performed_by`, `old_status`, `new_status`, `risk_level`, `health_score`, `performed_at`) VALUES
(1, 79, 'PC', 79, 'Manual inspection completed', 'Marked as checked manually', 'System', 'Needs Checking', 'Available', 'Low', 100, '2025-12-27 19:58:06'),
(2, NULL, 'Device', 27, 'Manual inspection completed', 'Marked as checked manually', 'System', 'Needs Checking', 'Available', 'Low', 100, '2025-12-29 22:18:38'),
(3, 80, 'PC', 80, 'Manual inspection completed', 'Marked as checked manually', 'System', 'Needs Checking', 'Available', 'Low', 100, '2025-12-29 22:45:47'),
(4, 81, 'PC', 81, 'Bulk inspection completed', 'Bulk marked as checked', 'System', 'Available', 'Available', 'Low', 100, '2025-12-30 22:18:04'),
(5, NULL, 'Device', 27, 'Bulk status update', 'Bulk marked as Damaged', 'System', 'Available', 'Damaged', 'High', 40, '2025-12-30 22:21:37'),
(6, NULL, 'Device', 27, 'Bulk status update', 'Bulk marked as Available', 'System', 'Damaged', 'Available', 'Low', 100, '2025-12-30 22:22:02'),
(7, NULL, 'Device', 27, 'Bulk status update', 'Bulk marked as In Used', 'System', 'Available', 'In Used', 'Low', 100, '2025-12-30 22:22:08');

-- --------------------------------------------------------

--
-- Table structure for table `maintenance_logs`
--

CREATE TABLE `maintenance_logs` (
  `id` int(11) NOT NULL,
  `asset_type` enum('PC','DEVICE') NOT NULL,
  `asset_id` int(11) NOT NULL,
  `previous_status` varchar(100) DEFAULT NULL,
  `new_status` varchar(100) DEFAULT NULL,
  `previous_risk_level` varchar(20) DEFAULT NULL,
  `new_risk_level` varchar(20) DEFAULT NULL,
  `action` varchar(255) NOT NULL,
  `performed_by` varchar(255) DEFAULT NULL,
  `remarks` text DEFAULT NULL,
  `performed_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `maintenance_logs`
--

INSERT INTO `maintenance_logs` (`id`, `asset_type`, `asset_id`, `previous_status`, `new_status`, `previous_risk_level`, `new_risk_level`, `action`, `performed_by`, `remarks`, `performed_at`) VALUES
(1, 'PC', 70, 'Needs Checking', 'Available', 'Medium', 'Low', 'Manual inspection completed', NULL, NULL, '2025-12-27 10:16:56'),
(2, 'PC', 71, 'Needs Checking', 'Available', 'Medium', 'Low', 'Manual inspection completed', NULL, NULL, '2025-12-27 19:28:15'),
(3, 'PC', 72, 'Needs Checking', 'Available', 'Medium', 'Low', 'Manual inspection completed', NULL, NULL, '2025-12-27 19:30:20'),
(4, 'PC', 73, 'Needs Checking', 'Available', 'Medium', 'Low', 'Manual inspection completed', NULL, NULL, '2025-12-27 19:33:01'),
(5, 'PC', 75, 'Needs Checking', 'Available', 'Medium', 'Low', 'Manual inspection completed', NULL, NULL, '2025-12-27 19:40:41'),
(6, 'PC', 76, 'Needs Checking', 'Available', 'Medium', 'Low', 'Manual inspection completed', NULL, NULL, '2025-12-27 19:53:27'),
(7, 'PC', 77, 'Needs Checking', 'Available', 'Medium', 'Low', 'Manual inspection completed', NULL, NULL, '2025-12-27 19:55:58'),
(8, 'PC', 78, 'Needs Checking', 'Available', 'Medium', 'Low', 'Manual inspection completed', NULL, NULL, '2025-12-27 19:56:29'),
(9, 'PC', 79, 'Needs Checking', 'Available', 'Medium', 'Low', 'Manual inspection completed', NULL, NULL, '2025-12-27 19:58:06'),
(12, 'DEVICE', 27, 'Needs Checking', 'Available', 'Medium', 'Low', 'Manual inspection completed', NULL, NULL, '2025-12-29 22:18:38'),
(13, 'PC', 80, 'Needs Checking', 'Available', 'Medium', 'Low', 'Manual inspection completed', NULL, NULL, '2025-12-29 22:45:47'),
(14, 'PC', 81, 'Available', 'Available', 'Low', 'Low', 'Bulk inspection completed', NULL, NULL, '2025-12-30 22:18:04'),
(15, 'DEVICE', 27, 'Available', 'Damaged', 'Low', 'High', 'Bulk status update', NULL, NULL, '2025-12-30 22:21:37'),
(16, 'DEVICE', 27, 'Damaged', 'Available', 'High', 'Low', 'Bulk status update', NULL, NULL, '2025-12-30 22:22:02'),
(17, 'DEVICE', 27, 'Available', 'In Used', 'Low', 'Low', 'Bulk status update', NULL, NULL, '2025-12-30 22:22:08');

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
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `last_checked` date DEFAULT NULL,
  `maintenance_interval_days` int(11) DEFAULT 30,
  `health_score` int(11) DEFAULT 100,
  `risk_level` varchar(20) DEFAULT 'Low'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pcinfofull`
--

INSERT INTO `pcinfofull` (`pcid`, `pcname`, `department_id`, `location`, `quantity`, `acquisition_cost`, `date_acquired`, `accountable`, `serial_no`, `municipal_serial_no`, `status`, `note`, `monitor`, `motherboard`, `ram`, `storage`, `gpu`, `psu`, `casing`, `other_parts`, `created_at`, `updated_at`, `last_checked`, `maintenance_interval_days`, `health_score`, `risk_level`) VALUES
(69, 'pc-do-00', 1, 'Computer Lab A', 1, 30000.00, '2025-10-26', 'John Doe', 'SN-1761440668046-5045499', 'MSN-1761440668046-96785299', 'Available', '3', '3', '3', '3', '3', '3', '3', '3', '3', '2025-10-26 01:04:28', '2025-12-26 14:40:45', '2025-12-26', 30, 100, 'Low'),
(70, 'pc-do-02', 1, 'Computer Lab A', 1, 30000.00, '2025-10-26', 'John Doe', 'SN-1761440668046-169661', 'MSN-1761440668046-344605', 'Available', '3', '3', '3', '3', '3', '3', '3', '3', '3', '2025-10-26 01:04:28', '2025-12-27 10:16:56', '2025-12-27', 30, 100, 'Low'),
(71, 'pc-do-03', 1, 'Computer Lab A', 1, 30000.00, '2025-10-26', 'John Doe', 'SN-1761440668046-427934', 'MSN-1761440668046-927513', 'Available', '3', '3', '3', '3', '3', '3', '3', '3', '3', '2025-10-26 01:04:28', '2025-12-27 19:28:15', '2025-12-28', 30, 100, 'Low'),
(72, 'pc-do-04', 1, 'Computer Lab A', 1, 30000.00, '0000-00-00', '4', 'SN-1761440694335-768370', 'MSN-1761440694335-395613', 'Available', '2', '2', '2', '2', '2', '213', '2', '2', '2', '2025-10-26 01:04:54', '2025-12-27 19:30:20', '2025-12-28', 30, 100, 'Low'),
(73, 'pc-do-05', 1, 'Computer Lab A', 1, 30000.00, '0000-00-00', '4', 'SN-1761440694335-256874', 'MSN-1761440694335-926256', 'Available', '2', '2', '2', '2', '2', '213', '2', '2', '2', '2025-10-26 01:04:54', '2025-12-27 19:33:01', '2025-12-28', 30, 100, 'Low'),
(75, 'pc', 1, 'Computer Lab C', 1, 35000.00, '2025-10-27', 'John Doe', 'SN-000074', '', 'Available', '3', '5', '5', '5', '5', '5', '5', '5', '5', '2025-10-26 17:14:15', '2025-12-27 19:40:41', '2025-12-28', 30, 100, 'Low'),
(76, 'pc-do-06', 1, '3', 4, 3.00, '0000-00-00', '3', 'SN-1761583172156-922706', 'MSN-1761583172156-573704', 'Available', '123', NULL, '312', '123', '123', '123', '123', '213', '123', '2025-10-27 16:39:32', '2025-12-27 19:53:27', '2025-12-28', 30, 100, 'Low'),
(77, 'pc-do-07', 1, '3', 4, 3.00, '0000-00-00', '3', 'SN-1761583172156-891456', 'MSN-1761583172156-132853', 'Available', '123', NULL, '312', '123', '123', '123', '123', '213', '123', '2025-10-27 16:39:32', '2025-12-27 19:55:58', '2025-12-28', 30, 100, 'Low'),
(78, 'pc-do-08', 1, '3', 4, 3.00, '0000-00-00', '3', 'SN-1761583172156-769494', 'MSN-1761583172156-380486', 'Available', '123', NULL, '312', '123', '123', '123', '123', '213', '123', '2025-10-27 16:39:32', '2025-12-27 19:56:29', '2025-12-28', 30, 100, 'Low'),
(79, 'pc-do-09', 1, '3', 4, 3.00, '0000-00-00', '3', 'SN-1761583172156-139349', 'MSN-1761583172156-702518', 'Available', '123', NULL, '312', '123', '123', '123', '123', '213', '123', '2025-10-27 16:39:32', '2025-12-27 19:58:06', '2025-12-28', 30, 100, 'Low'),
(80, '213', 1, '123', 1, 123.00, '0000-00-00', '123', '213', '123', 'Available', '123', NULL, '123', '123', '213', '123', '123', '214', '214', '2025-10-27 16:41:19', '2025-12-29 22:45:47', '2025-12-30', 30, 100, 'Low'),
(81, 'pc222', 1, 'Computer Lab C', 1, 50000.00, '0000-00-00', 'John Doe', 'SN-0000053434', 'MUN-00012522213', 'Available', '', NULL, '324221', '123', '12412', '123', '2133', '123', '123', '2025-12-30 22:15:43', '2025-12-30 22:18:04', '2025-12-31', 30, 100, 'Low');

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
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `permissions` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`permissions`)),
  `first_name` varchar(50) DEFAULT NULL,
  `middle_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `faculty_name`, `email`, `password`, `is_admin`, `is_active`, `created_at`, `updated_at`, `permissions`, `first_name`, `middle_name`, `last_name`) VALUES
(9, 'admin', 'santos, matthew S.', 'matthewjohnsantos2004@gmail.com', 'scrypt:32768:8:1$ryLUIe9RsrDae4ph$d62414102427f2911938fc93a342514c4064c148112be99a3aa808a83bf62eca63b5ab43f9b0cc8341e01f21f8968882b1eb26c91b737a8872e9950ff25befd0', 1, 1, '2025-03-24 02:34:16', '2025-10-27 04:03:59', '{\"dashboard\": {\"view\": true, \"edit\": true}, \"inventory\": {\"view\": true, \"edit\": true}, \"qrlist\": {\"view\": true, \"edit\": true}, \"report\": {\"view\": true, \"edit\": true}, \"dept\": {\"view\": true, \"edit\": false}}', 'matthew', 's', 'santos'),
(10, 'user', 'me', 'matthewjohnsantos143@gmail.com', 'scrypt:32768:8:1$LQ4mixntjhzilHyY$7e9f133cb8da3b06625ac3ee3164c9d8fb97983226c64ddfecddad0fa9fd76a5821f391e3d1595c4029544ae4a3f253a0952f1496174f3b46093503766ff5fcb', 0, 1, '2025-03-24 09:25:58', '2025-10-27 14:31:08', '{\"dashboard\": {\"view\": true, \"edit\": false}, \"inventory\": {\"view\": true, \"edit\": false}, \"qrlist\": {\"view\": true, \"edit\": false}, \"report\": {\"view\": true, \"edit\": false}, \"dept\": {\"view\": true, \"edit\": false}}', 'matthew', 's', 'santos'),
(11, 'rbautista', '', 'renatobautista17@gmail.com', 'scrypt:32768:8:1$Gc5JBZzptDeAvn9b$cf555f0d8ead0898962845e3fba4f6ef99fc3ab7e7c0a4f86f09d766054ed4dcfdc99174d15db62bad4701f583feb1fea555bcd14f9593675ee30e3b7891a037', 1, 1, '2025-10-26 15:24:49', '2025-10-27 16:44:03', '{\"dashboard\": {\"view\": true, \"edit\": true}, \"inventory\": {\"view\": true, \"edit\": true}, \"qrlist\": {\"view\": true, \"edit\": true}, \"report\": {\"view\": true, \"edit\": true}, \"dept\": {\"view\": true, \"edit\": true}}', 'Renato', 'sd', 'Bautista');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `asset_maintenance_logs`
--
ALTER TABLE `asset_maintenance_logs`
  ADD PRIMARY KEY (`id`);

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
  ADD UNIQUE KEY `serial_no` (`serial_no`),
  ADD UNIQUE KEY `municipal_serial_no` (`municipal_serial_no`),
  ADD KEY `fk_department` (`department_id`);

--
-- Indexes for table `devices_units`
--
ALTER TABLE `devices_units`
  ADD PRIMARY KEY (`accession_id`),
  ADD KEY `device_id` (`device_id`);

--
-- Indexes for table `inventory_settings`
--
ALTER TABLE `inventory_settings`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `inventory_status_logs`
--
ALTER TABLE `inventory_status_logs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `maintenance_history`
--
ALTER TABLE `maintenance_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_maintenance_pc` (`pcid`);

--
-- Indexes for table `maintenance_logs`
--
ALTER TABLE `maintenance_logs`
  ADD PRIMARY KEY (`id`);

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
-- AUTO_INCREMENT for table `asset_maintenance_logs`
--
ALTER TABLE `asset_maintenance_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

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
  MODIFY `department_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `devices`
--
ALTER TABLE `devices`
  MODIFY `device_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `devices_full`
--
ALTER TABLE `devices_full`
  MODIFY `accession_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `devices_units`
--
ALTER TABLE `devices_units`
  MODIFY `accession_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `inventory_settings`
--
ALTER TABLE `inventory_settings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `inventory_status_logs`
--
ALTER TABLE `inventory_status_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `maintenance_history`
--
ALTER TABLE `maintenance_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `maintenance_logs`
--
ALTER TABLE `maintenance_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `pcinfofull`
--
ALTER TABLE `pcinfofull`
  MODIFY `pcid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=82;

--
-- AUTO_INCREMENT for table `pcparts`
--
ALTER TABLE `pcparts`
  MODIFY `part_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

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
-- Constraints for table `maintenance_history`
--
ALTER TABLE `maintenance_history`
  ADD CONSTRAINT `fk_maintenance_pc` FOREIGN KEY (`pcid`) REFERENCES `pcinfofull` (`pcid`) ON DELETE CASCADE;

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
