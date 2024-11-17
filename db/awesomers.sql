/*
SQLyog Ultimate v10.00 Beta1
MySQL - 5.5.5-10.4.32-MariaDB : Database - ecommerce
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`ecommerce` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

USE `ecommerce`;

/*Table structure for table `accounts` */

DROP TABLE IF EXISTS `accounts`;

CREATE TABLE `accounts` (
  `accountID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountEmail` varchar(255) NOT NULL,
  `accountPassword` varchar(255) NOT NULL,
  `accountUsername` varchar(255) NOT NULL,
  `accountRole` varchar(255) NOT NULL DEFAULT 'buyer',
  `accountArchived` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`accountID`),
  UNIQUE KEY `accountEmail` (`accountEmail`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `accounts` */

insert  into `accounts`(`accountID`,`accountEmail`,`accountPassword`,`accountUsername`,`accountRole`,`accountArchived`) values (26,'demerin@gmail.com','pbkdf2:sha256:600000$zaQaIx2olb3woHic$55ddd820d7ecfc260af69ba51c7763424bd546c1e5a88d3c82767b17ea777dd3','luke demerin','seller',0),(42,'buyer@gmail.com','pbkdf2:sha256:600000$M9Qc1Lnd10et2oPc$d547e276b37c80830094ba3fc62005dc763a5b2a8a3e50d30054ee5a8c225da4','buyer jones','buyer',0),(43,'seller@gmail.com','pbkdf2:sha256:600000$ALe1BW71L6YCXkAQ$837a22a31095bb725d2c0b2b3582f958dc9efb34fb519052166b4239d240b021','seller scott','seller',0),(46,'admin@gmail.com','pbkdf2:sha256:600000$UQcTCET1xbaFQlTu$cce2ce2a6329e5cf4e88ee3240391cf9ece1d44b32a77cff3317332607ed0516','admin admin','admin',0),(47,'archived@gmail.com','pbkdf2:sha256:600000$MxJBKn5ePCKN5qvX$157dafdfe57db7f8a96499b44590ea2c5a906d4756fc61bab1834310192002bf','archived andy','buyer',0),(48,'resetpass@gmail.com','pbkdf2:sha256:600000$VqDm53Mg0QX0QSaJ$0f6cef816f08c18736d8c73194687cdd057cf5f06c5ef45fadd3d8060bd340d8','reset password','buyer',0),(49,'admins@gmail.com','pbkdf2:sha256:600000$ePvk3dFLQG8q59n6$6ee93fe16f9c5337a92e790047e72c0c9771f687523100f411a4af653e1b0d1d','admin boss','admin',0),(50,'awesomersecommerce@gmail.com','pbkdf2:sha256:1000000$xYW7Ke7H1brSLvdl$00c5149095a86a19bc06900d71fc668a750907a63241367f466eed1ae566e0b0','awesomers ecommerce','buyer',0),(51,'s21contactemail@gmail.com','pbkdf2:sha256:1000000$gpmd9JqFcYJdRaoN$11dbf53307763b477fcac9fb1bd7044c28390663d195d894b6d926a3c3fc8b2b','slaking 21','buyer',0);

/*Table structure for table `addressbooks` */

DROP TABLE IF EXISTS `addressbooks`;

CREATE TABLE `addressbooks` (
  `addressBookID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `profileID` bigint(20) NOT NULL,
  `addressName` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`addressBookID`,`accountID`,`profileID`),
  KEY `addressAccountID` (`accountID`),
  KEY `buyerProfileID` (`profileID`),
  CONSTRAINT `addressAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `buyerProfileID` FOREIGN KEY (`profileID`) REFERENCES `profiles_buyer` (`buyerProfileID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `sellerProfileID` FOREIGN KEY (`profileID`) REFERENCES `profiles_seller` (`sellerProfileID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `addressbooks` */

/*Table structure for table `cart` */

DROP TABLE IF EXISTS `cart`;

CREATE TABLE `cart` (
  `cartID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `productID` bigint(20) NOT NULL,
  `cartItemName` varchar(255) NOT NULL,
  `cartItemQty` int(255) NOT NULL,
  PRIMARY KEY (`cartID`,`accountID`,`productID`),
  KEY `cartBuyerID` (`accountID`),
  CONSTRAINT `cartBuyerID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `cart` */

/*Table structure for table `orders` */

DROP TABLE IF EXISTS `orders`;

CREATE TABLE `orders` (
  `orderID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `orderDate` datetime NOT NULL,
  `shippingMethod` varchar(255) NOT NULL,
  `sellerAddress` varchar(255) NOT NULL,
  `currentAddress` varchar(255) NOT NULL,
  `buyerAddress` varchar(255) NOT NULL,
  `orderDatePlaced` datetime NOT NULL,
  PRIMARY KEY (`orderID`,`accountID`),
  KEY `ordersAccountID` (`accountID`),
  CONSTRAINT `ordersAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `orders` */

/*Table structure for table `orders_status` */

DROP TABLE IF EXISTS `orders_status`;

CREATE TABLE `orders_status` (
  `orderStatusID` bigint(20) NOT NULL AUTO_INCREMENT,
  `orderID` bigint(20) NOT NULL,
  `orderStatus` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`orderStatusID`,`orderID`),
  KEY `statusOrderID` (`orderID`),
  CONSTRAINT `statusOrderID` FOREIGN KEY (`orderID`) REFERENCES `orders` (`orderID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `orders_status` */

/*Table structure for table `payment` */

DROP TABLE IF EXISTS `payment`;

CREATE TABLE `payment` (
  `paymentID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `orderID` bigint(20) NOT NULL,
  `paymentMethod` varchar(255) NOT NULL,
  `paymentDatePaid` datetime NOT NULL,
  PRIMARY KEY (`paymentID`,`orderID`,`accountID`),
  KEY `paymentAccountID` (`accountID`),
  KEY `paymentOrderID` (`orderID`),
  CONSTRAINT `paymentAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `paymentOrderID` FOREIGN KEY (`orderID`) REFERENCES `orders` (`orderID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `payment` */

/*Table structure for table `products` */

DROP TABLE IF EXISTS `products`;

CREATE TABLE `products` (
  `productID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `picture` longblob DEFAULT NULL,
  `productName` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `category` varchar(255) NOT NULL,
  `subcategory` varchar(255) DEFAULT NULL,
  `variation` varchar(255) NOT NULL,
  `price` int(255) NOT NULL,
  `quantity` int(255) NOT NULL,
  `dateAdded` datetime NOT NULL,
  `isArchived` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`productID`,`accountID`),
  KEY `productsCategoryID` (`category`),
  KEY `productsSellerID` (`accountID`),
  CONSTRAINT `productsSellerID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `products` */

insert  into `products`(`productID`,`accountID`,`picture`,`productName`,`description`,`category`,`subcategory`,`variation`,`price`,`quantity`,`dateAdded`,`isArchived`) values (1,43,'lol.jpg','haha','joji','vlogs',NULL,'is',1000,1,'2024-11-10 12:05:14',0),(2,43,'lol.jpg','joji','Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor i','vlogs',NULL,'filthy, frank',1000,0,'2024-11-10 12:05:14',0),(3,43,'lol.jpg','a','a','a',NULL,'a',0,0,'2024-11-10 12:05:14',1),(4,43,'test.png','asd','asd','asdaas',NULL,'asda',2325,129,'2024-11-10 13:18:19',1),(5,43,'test.png','asd','asd','asd',NULL,'asd',120,127,'2024-11-10 13:20:23',1),(6,43,'test.png','asd','asd','asd',NULL,'asd',123,123,'2024-11-10 13:21:25',1),(7,43,'test.png','asd','asd','asdaas',NULL,'asd',123,123,'2024-11-10 13:22:14',1),(8,43,'test.png','asd','asd','asd',NULL,'asd',2000,6,'2024-11-10 13:25:35',1),(9,43,'test.png','he','ewq','qwe',NULL,'dasd',1,1,'2024-11-12 12:06:47',0),(10,43,'test.png','kasjd','lansiod','ansd',NULL,'lasdjpasd',123,10,'2024-11-12 12:11:11',0),(11,43,'19e624ae-a33c-11ef-9c01-3c7c3f2bb6c4_test.png','dsa','asd','sdds',NULL,'ssdds',321,123,'2024-11-15 18:26:39',0),(12,43,'44609495-a34b-11ef-b5de-3c7c3f2bb6c4_test.png','asdasd','asd','Desktops',NULL,'Desktops',123123,123123,'2024-11-15 20:15:13',0),(13,43,'5b43ec20-a3cc-11ef-8a90-3c7c3f2bb6c4_test.png','jameng house','the design is very fun','Desktops',NULL,'Desktops',123,22,'2024-11-16 11:39:17',0),(14,43,'be49df69-a3d7-11ef-a0d6-3c7c3f2bb6c4_test.png','asd','asdasd','Desktops',NULL,'Desktops',321,123,'2024-11-16 13:00:47',0),(15,43,'6825036c-a3d8-11ef-a639-3c7c3f2bb6c4_test.png','delete fields','delete','Desktops',NULL,'Desktops',2443,23,'2024-11-16 13:05:32',0),(16,43,'6e2a0906-a3d8-11ef-a2fa-3c7c3f2bb6c4_test.png','delete fields','321','Desktops',NULL,'Desktops',233,123,'2024-11-16 13:05:42',1),(17,43,'deabe4f8-a3dc-11ef-908b-3c7c3f2bb6c4_test.png','asd','123','Desktops',NULL,'Desktops',123,123,'2024-11-16 13:37:29',0),(18,43,'520d7c90-a3e2-11ef-bbcd-3c7c3f2bb6c4_test.png','Because this function is fairly verbose and used frequently in JavaScript, the $ has long been used as its alias, and many of the libraries available for use with JavaScript create a $() function that references an element from the DOM if you pass it the ','asdasd','Desktops',NULL,'Desktops',123,321,'2024-11-16 14:16:30',0);

/*Table structure for table `products_admin` */

DROP TABLE IF EXISTS `products_admin`;

CREATE TABLE `products_admin` (
  `productAdminID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `picture` longblob DEFAULT NULL,
  `productName` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `category` varchar(255) NOT NULL,
  `subcategory` varchar(255) DEFAULT NULL,
  `variation` varchar(255) NOT NULL,
  `price` int(255) NOT NULL,
  `quantity` int(255) NOT NULL,
  `dateAdded` datetime NOT NULL,
  `isArchived` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`productAdminID`,`accountID`),
  KEY `productsRequestsAccountID` (`accountID`),
  CONSTRAINT `adminProductID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `products_admin` */

/*Table structure for table `products_categories` */

DROP TABLE IF EXISTS `products_categories`;

CREATE TABLE `products_categories` (
  `categoryID` int(11) NOT NULL AUTO_INCREMENT,
  `categoryName` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`categoryID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `products_categories` */

/*Table structure for table `profiles_buyer` */

DROP TABLE IF EXISTS `profiles_buyer`;

CREATE TABLE `profiles_buyer` (
  `buyerProfileID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `buyerName` varchar(255) NOT NULL,
  `buyerPicture` longblob DEFAULT NULL,
  `buyerPhoneNum` varchar(255) NOT NULL,
  `buyerCountry` varchar(255) NOT NULL,
  `buyerDateCreated` datetime NOT NULL,
  `isArchived` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`buyerProfileID`,`accountID`),
  KEY `buyerProfileAccountID` (`accountID`),
  CONSTRAINT `buyerProfileAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `profiles_buyer` */

/*Table structure for table `profiles_seller` */

DROP TABLE IF EXISTS `profiles_seller`;

CREATE TABLE `profiles_seller` (
  `sellerProfileID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `storeName` varchar(255) NOT NULL,
  `storePicture` longblob DEFAULT NULL,
  `storePhoneNum` varchar(255) NOT NULL,
  `storeCountry` varchar(255) NOT NULL,
  `storeDateCreated` datetime NOT NULL,
  `isArchived` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`sellerProfileID`,`accountID`),
  KEY `sellerProfileAccountID` (`accountID`),
  CONSTRAINT `sellerProfileAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `profiles_seller` */

/*Table structure for table `requests` */

DROP TABLE IF EXISTS `requests`;

CREATE TABLE `requests` (
  `requestID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `accountEmail` varchar(255) NOT NULL,
  `requestType` varchar(255) NOT NULL,
  `requestArchived` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`requestID`,`accountID`),
  UNIQUE KEY `requestsAccountEmail` (`accountEmail`),
  KEY `requestsAccountID` (`accountID`),
  CONSTRAINT `requestAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `requests` */

insert  into `requests`(`requestID`,`accountID`,`accountEmail`,`requestType`,`requestArchived`) values (4,26,'demerin@gmail.com','BUYER TO BE SELLER',1),(23,43,'seller@gmail.com','BUYER TO BE SELLER',1),(24,42,'buyer@gmail.com','BUYER TO BE SELLER',1);

/*Table structure for table `reviews` */

DROP TABLE IF EXISTS `reviews`;

CREATE TABLE `reviews` (
  `reviewID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `productID` bigint(20) NOT NULL,
  `rating` int(255) NOT NULL,
  `reviewDescription` varchar(255) NOT NULL,
  `reviewPicture` longblob NOT NULL,
  `reviewLikes` int(255) DEFAULT NULL,
  `reviewComments` varchar(255) DEFAULT NULL,
  `reviewDateAdded` datetime NOT NULL,
  `isArchived` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`reviewID`,`accountID`,`productID`),
  KEY `reviewsAccountID` (`accountID`),
  KEY `reviewsProductID` (`productID`),
  CONSTRAINT `reviewsAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `reviewsProductID` FOREIGN KEY (`productID`) REFERENCES `products` (`productID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `reviews` */

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
