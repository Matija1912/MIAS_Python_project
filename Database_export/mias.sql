-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 18, 2024 at 11:41 AM
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
-- Database: `mias`
--

DELIMITER $$
--
-- Procedures
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `RemoveInvoiceAndUpdateCounter` (IN `in_invoice_id` INT, IN `in_company_id` INT)   BEGIN
DECLARE _invoice_year INT;
DECLARE max_invoice_number INT;

	SELECT invoices.invoice_year
    INTO _invoice_year
    FROM invoices
    WHERE id = in_invoice_id AND company_id = in_company_id;

    UPDATE invoices
    SET invoices.company_id = NULL
    WHERE invoices.id = in_invoice_id AND invoices.company_id = in_company_id;

	SELECT COALESCE(MAX(invoices.invoice_number), 0)
    INTO max_invoice_number
    FROM invoices
    WHERE invoices.company_id = in_company_id AND invoices.invoice_year = _invoice_year;

    UPDATE invoice_counter
    SET invoice_counter.next_invoice_number = max_invoice_number
    WHERE invoice_counter.year = _invoice_year
    AND invoice_counter.company_id = in_company_id;

END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `UpdateInvoiceCounter` (IN `_company_id` INT, IN `_year` INT, IN `_invoice_number` INT)   BEGIN
    DECLARE current_invoice_number INT;

    SELECT ic.next_invoice_number INTO current_invoice_number
    FROM invoice_counter ic
    WHERE ic.year = _year AND ic.company_id = _company_id;

    IF current_invoice_number IS NULL THEN
    	 INSERT INTO invoice_counter (year, company_id, next_invoice_number)
         VALUES (_year, _company_id, 0);
         SET current_invoice_number= 0;
	END IF;

    IF _invoice_number > current_invoice_number THEN
        UPDATE invoice_counter
        SET next_invoice_number = _invoice_number
        WHERE year = _year AND company_id = _company_id;
    END IF;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `UpdateInvoiceCounterAutoGen` (IN `_company_id` INT, IN `_year` INT)   BEGIN

    UPDATE invoice_counter ic
    SET ic.next_invoice_number = ic.next_invoice_number + 1
    WHERE ic.year = _year AND ic.company_id = _company_id;

    IF ROW_COUNT() = 0 THEN

        INSERT INTO invoice_counter (invoice_counter.year, invoice_counter.company_id, invoice_counter.next_invoice_number)
        VALUES (_year, _company_id, 1);
    END IF;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `companies`
--

CREATE TABLE `companies` (
  `id` int(11) NOT NULL,
  `company_name` varchar(255) NOT NULL,
  `street` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `post_number` varchar(255) DEFAULT NULL,
  `vat_id` varchar(255) DEFAULT NULL,
  `iban` varchar(34) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `companies`
--

INSERT INTO `companies` (`id`, `company_name`, `street`, `city`, `post_number`, `vat_id`, `iban`) VALUES
(1, 'Motorsport innovations and solutions d.o.o.', 'Glavna cesta 84', 'Đurđekovec', '10362', 'HR92531046076', 'HR0924840081135381404'),
(2, 'MOTORSPORT INNOVATIONS AND SOLUTIONS d.o.o.', 'Glavna cesta 84', 'Durdekovec', '10362', 'HR92531046076', 'HR0924840081135381404');

-- --------------------------------------------------------

--
-- Table structure for table `customers`
--

CREATE TABLE `customers` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `street` varchar(255) NOT NULL,
  `post_number` varchar(20) NOT NULL,
  `city` varchar(100) NOT NULL,
  `country` varchar(100) NOT NULL,
  `vat_id` varchar(20) NOT NULL,
  `registration_number` varchar(50) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `fax` varchar(50) DEFAULT NULL,
  `company_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customers`
--

INSERT INTO `customers` (`id`, `name`, `email`, `street`, `post_number`, `city`, `country`, `vat_id`, `registration_number`, `phone`, `fax`, `company_id`) VALUES
(1, 'AUTO CENTAR IVKOVIĆ d.o.o.', 'autocentarivkovic1@gmail.com', 'Čepljani, Piceti 52 B', '52470', 'Umag', 'Hrvatska', '07518901102', NULL, NULL, NULL, 1),
(2, 'AGRO MAK d.o.o.', 'info.agromak@gmail.com', 'Ulica 30. svibnja 50', '33000', 'Milanovac', 'Hrvatska', '42835023837', NULL, NULL, NULL, 1),
(6, 'ENDURO MOTO SPORT D.O.O.', 'enduromotosport113@gmail.com', 'Tugonica 128A', '49246', 'Marija Bistrica', 'Hrvatska', '36910638020', NULL, NULL, NULL, 1),
(7, 'Customer1', 'customer1@email.com', 'customer 1a', '1000', 'City', 'Country', '71363415', NULL, NULL, NULL, 2);

-- --------------------------------------------------------

--
-- Table structure for table `invoices`
--

CREATE TABLE `invoices` (
  `id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `invoice_with_vat` tinyint(1) NOT NULL,
  `status` varchar(20) DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `invoice_number` int(10) NOT NULL,
  `invoice_year` int(11) GENERATED ALWAYS AS (year(`created_at`)) STORED,
  `company_id` int(11) DEFAULT NULL,
  `invoice_office_number` int(5) DEFAULT 1,
  `invoice_device_number` int(5) DEFAULT 1,
  `note` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `invoices`
--

INSERT INTO `invoices` (`id`, `customer_id`, `invoice_with_vat`, `status`, `created_at`, `invoice_number`, `company_id`, `invoice_office_number`, `invoice_device_number`, `note`) VALUES
(57, 1, 1, 'Pending', '2024-12-14 14:19:00', 1, 1, 1, 1, '1. Dokument izradio: Karlo Kovacic\n2. Ovaj dokument je izdan u elektronskom obliku te je valjan bez potpisa i pečata.\n                    \n                    \n                    '),
(58, 6, 1, 'Pending', '2024-12-14 14:23:00', 2, 1, 1, 1, '1. Dokument izradio: Karlo Kovacic\n2. Ovaj dokument je izdan u elektronskom obliku te je valjan bez potpisa i pečata.\n                    '),
(59, 6, 1, 'Pending', '2024-12-14 14:28:00', 3, NULL, 1, 1, '1. Dokument izradio: Karlo Kovacic\n2. Ovaj dokument je izdan u elektronskom obliku te je valjan bez potpisa i pečata.\n                    '),
(60, 1, 1, 'Pending', '2024-12-14 16:30:00', 3, 1, 1, 1, '1. Dokument izradio: Karlo Kovacic\n2. Ovaj dokument je izdan u elektronskom obliku te je valjan bez potpisa i pečata.\n                    '),
(61, 2, 1, 'Pending', '2024-12-14 18:22:00', 4, 1, 1, 1, '1. Dokument izradio: Karlo Kovacic\n2. Ovaj dokument je izdan u elektronskom obliku te je valjan bez potpisa i pečata.\n                    \n                    ');

-- --------------------------------------------------------

--
-- Table structure for table `invoice_counter`
--

CREATE TABLE `invoice_counter` (
  `year` int(4) NOT NULL,
  `next_invoice_number` int(11) NOT NULL DEFAULT 0,
  `company_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `invoice_counter`
--

INSERT INTO `invoice_counter` (`year`, `next_invoice_number`, `company_id`) VALUES
(2024, 4, 1);

-- --------------------------------------------------------

--
-- Table structure for table `invoice_items`
--

CREATE TABLE `invoice_items` (
  `id` int(11) NOT NULL,
  `invoice_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `discount` decimal(10,2) DEFAULT 0.00,
  `product_price_no_vat` decimal(10,2) DEFAULT NULL,
  `product_description` text DEFAULT NULL,
  `vat_percentage` decimal(5,2) DEFAULT 0.00,
  `product_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `invoice_items`
--

INSERT INTO `invoice_items` (`id`, `invoice_id`, `product_id`, `quantity`, `discount`, `product_price_no_vat`, `product_description`, `vat_percentage`, `product_name`) VALUES
(197, 57, 7, 1, 0.00, 1200.00, 'Kayo TT140 pit bike.\nVIN: ', 25.00, 'KAYO TT140'),
(198, 58, 9, 1, 20.00, 1840.00, 'Kayo K2 Enduro motocikl.\nVIN: ADGQEQE762', 25.00, 'KAYO K2 ENDURO'),
(199, 58, 5, 1, 20.00, 1000.00, 'Kayo TS90 pit bike.\nVIN: ASFQGHQ123T', 25.00, 'KAYO TS90'),
(200, 58, 7, 1, 20.00, 1200.00, 'Kayo TT140 pit bike.\nVIN: QWF12RFWQ', 25.00, 'KAYO TT140'),
(201, 59, 5, 1, 20.00, 800.00, 'Kayo TS90 pit bike.\nVIN:SDASDDAS121', 25.00, 'KAYO TS90'),
(202, 59, 7, 1, 20.00, 1200.00, 'Kayo TT140 pit bike.\nVIN: Sdasdas12312', 25.00, 'KAYO TT140'),
(203, 60, 9, 1, 0.00, 1840.00, 'Kayo K2 Enduro motocikl.\nVIN: ', 25.00, 'KAYO K2 ENDURO'),
(205, 61, 5, 1, 0.00, 1000.00, 'Kayo TS90 pit bike.\nVIN:', 25.00, 'KAYO TS90');

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `vat_percentage` decimal(5,2) DEFAULT 0.00,
  `stock` int(11) DEFAULT 0,
  `company_id` int(11) DEFAULT NULL,
  `vat_status` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`id`, `name`, `description`, `price`, `vat_percentage`, `stock`, `company_id`, `vat_status`) VALUES
(5, 'KAYO TS90', 'Kayo TS90 pit bike.\r\nVIN:', 1000.00, 25.00, 3, 1, 0),
(7, 'KAYO TT140', 'Kayo TT140 pit bike.\r\nVIN: ', 1200.00, 25.00, 4, 1, 0),
(9, 'KAYO K2 ENDURO', 'Kayo K2 Enduro motocikl.\r\nVIN: ', 1840.00, 25.00, 1, 1, 0),
(12, 'Product1', 'Product1 description', 1195.95, 25.00, 0, 2, 0),
(13, 'KAYO K6', 'Kayo K6 motocikl.\r\nVIN: ', 4600.00, 25.00, 5, 1, 0),
(14, 'Dostava', 'Usluga dostave', 100.00, 25.00, 0, 1, 1),
(15, 'KAYO A150', 'Kayo A150\r\nVIN: ', 2000.00, 25.00, 10, 1, 0);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `company_id` int(11) DEFAULT NULL,
  `role` varchar(50) DEFAULT 'admin'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `email`, `password_hash`, `first_name`, `last_name`, `company_id`, `role`) VALUES
(1, 'matija@kayomotorcycles.eu', 'pbkdf2:sha256:1000000$olBwmlC8CeX3AvMk$dd167c1c27c0c1a2d2a8b0c1f1d41b44f756c936b90876eb403915975a7d87ed', 'Matija', 'Kovacic', 2, 'admin'),
(3, 'marko@kayomotorcycles.eu', 'pbkdf2:sha256:1000000$V0b17bqLz401Xk7h$b5f1fee3091bda9b93d3b86c5a5e4159def2c28dd727b1064edd2b93cacd85b4', 'Marko', 'Šimunec', 1, 'admin'),
(4, 'karlo@kayomotorcycles.eu', 'pbkdf2:sha256:1000000$RqyhWGWd7MCfvDqQ$210472a061f6952e48b3e4c40b2b5f37a504ef0584c2e46d1b77de81824fde3d', 'Karlo', 'Kovacic', 1, 'admin'),
(5, 'domagoj@mias.eu', 'pbkdf2:sha256:1000000$RerZ2Mc6KqczDkcV$bfb6986d9d260f9714abb87d75a4fddff6c3e59a1478d0738aff6f76ff52578a', 'Domagoj', 'Lepen', 2, 'admin'),
(6, 'roman@mias.eu', 'pbkdf2:sha256:1000000$YMurxZfR4niAPXUz$806eb1d7b527f3ec8232fd89b49860f2bcca7601d417fdb7e0a477b62a9eb7c3', 'Roman', 'Kuzman', 2, 'admin'),
(7, 'stjepan@mias.eu', 'pbkdf2:sha256:1000000$0HKt2EXmTliBDLa5$9d5ebd14e123c9b35be0e73cfa9ee0a6dc31ecf48ebc8b1bd00f4f7ab24b9b4c', 'Stjepan', 'Derdic', 2, 'admin');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `companies`
--
ALTER TABLE `companies`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `customers`
--
ALTER TABLE `customers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `customers_fk_company` (`company_id`);

--
-- Indexes for table `invoices`
--
ALTER TABLE `invoices`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_invoice` (`invoice_year`,`company_id`,`invoice_number`),
  ADD KEY `fk_company_id` (`company_id`),
  ADD KEY `fk_customer_id` (`customer_id`);

--
-- Indexes for table `invoice_counter`
--
ALTER TABLE `invoice_counter`
  ADD PRIMARY KEY (`year`,`company_id`),
  ADD KEY `fk_cinvoice_counter_company_id` (`company_id`);

--
-- Indexes for table `invoice_items`
--
ALTER TABLE `invoice_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_invoice` (`invoice_id`),
  ADD KEY `fk_product` (`product_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`),
  ADD KEY `products_fk_company` (`company_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `company_id` (`company_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `companies`
--
ALTER TABLE `companies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `customers`
--
ALTER TABLE `customers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `invoices`
--
ALTER TABLE `invoices`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=62;

--
-- AUTO_INCREMENT for table `invoice_items`
--
ALTER TABLE `invoice_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=206;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `customers`
--
ALTER TABLE `customers`
  ADD CONSTRAINT `customers_fk_company` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`);

--
-- Constraints for table `invoices`
--
ALTER TABLE `invoices`
  ADD CONSTRAINT `fk_company_id` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`),
  ADD CONSTRAINT `fk_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`);

--
-- Constraints for table `invoice_counter`
--
ALTER TABLE `invoice_counter`
  ADD CONSTRAINT `fk_cinvoice_counter_company_id` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`);

--
-- Constraints for table `invoice_items`
--
ALTER TABLE `invoice_items`
  ADD CONSTRAINT `fk_invoice` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `products_fk_company` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`);

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
