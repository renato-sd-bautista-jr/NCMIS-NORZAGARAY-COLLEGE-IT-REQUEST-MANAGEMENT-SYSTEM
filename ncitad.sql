-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 24, 2025 at 01:59 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ncitad`
--

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
  `device_name` varchar(100) NOT NULL,
  `department_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `devices`
--

INSERT INTO `devices` (`device_id`, `device_name`, `department_id`) VALUES
(1, 'PC1', 1),
(3, 'PC2', 1);

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
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

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
  MODIFY `device_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

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
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
