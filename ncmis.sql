-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 15, 2026 at 07:45 PM
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
-- Table structure for table `pc_part_replacements`
--

CREATE TABLE `pc_part_replacements` (
  `replacement_id` int(11) NOT NULL,
  `pcid` int(11) NOT NULL,
  `part_name` varchar(50) NOT NULL,
  `replaced_at` datetime DEFAULT current_timestamp(),
  `replaced_by` int(11) DEFAULT NULL,
  `old_accession_id` int(11) DEFAULT NULL,
  `new_accession_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pc_part_replacements`
--

INSERT INTO `pc_part_replacements` (`replacement_id`, `pcid`, `part_name`, `replaced_at`, `replaced_by`, `old_accession_id`, `new_accession_id`) VALUES
(1, 67, 'motherboard', '2026-04-16 00:11:42', 9, NULL, NULL),
(2, 112, 'motherboard', '2026-04-16 01:24:50', 9, NULL, 122),
(3, 111, 'motherboard', '2026-04-16 01:26:07', 9, NULL, 120),
(4, 112, 'motherboard', '2026-04-16 01:31:36', 9, 122, 121);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `pc_part_replacements`
--
ALTER TABLE `pc_part_replacements`
  ADD PRIMARY KEY (`replacement_id`),
  ADD KEY `pcid` (`pcid`),
  ADD KEY `fk_old_part` (`old_accession_id`),
  ADD KEY `fk_new_part` (`new_accession_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `pc_part_replacements`
--
ALTER TABLE `pc_part_replacements`
  MODIFY `replacement_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `pc_part_replacements`
--
ALTER TABLE `pc_part_replacements`
  ADD CONSTRAINT `fk_new_part` FOREIGN KEY (`new_accession_id`) REFERENCES `devices_full` (`accession_id`),
  ADD CONSTRAINT `fk_old_part` FOREIGN KEY (`old_accession_id`) REFERENCES `devices_full` (`accession_id`),
  ADD CONSTRAINT `pc_part_replacements_ibfk_1` FOREIGN KEY (`pcid`) REFERENCES `pcinfofull` (`pcid`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
