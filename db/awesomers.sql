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
  `accountFirstName` varchar(255) NOT NULL,
  `accountLastName` varchar(255) NOT NULL,
  `accountRole` varchar(255) NOT NULL DEFAULT 'buyer',
  `accountArchived` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`accountID`),
  UNIQUE KEY `accountEmail` (`accountEmail`)
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `accounts` */

insert  into `accounts`(`accountID`,`accountEmail`,`accountPassword`,`accountFirstName`,`accountLastName`,`accountRole`,`accountArchived`) values (26,'demerin@gmail.com','pbkdf2:sha256:600000$zaQaIx2olb3woHic$55ddd820d7ecfc260af69ba51c7763424bd546c1e5a88d3c82767b17ea777dd3','luke','demerin','seller',0),(42,'buyer@gmail.com','pbkdf2:sha256:600000$M9Qc1Lnd10et2oPc$d547e276b37c80830094ba3fc62005dc763a5b2a8a3e50d30054ee5a8c225da4','buyer','jones','buyer',0),(43,'seller@gmail.com','pbkdf2:sha256:600000$ALe1BW71L6YCXkAQ$837a22a31095bb725d2c0b2b3582f958dc9efb34fb519052166b4239d240b021','seller','scott','seller',0),(46,'admin@gmail.com','pbkdf2:sha256:600000$UQcTCET1xbaFQlTu$cce2ce2a6329e5cf4e88ee3240391cf9ece1d44b32a77cff3317332607ed0516','admin','admin','admin',0),(47,'archived@gmail.com','pbkdf2:sha256:600000$MxJBKn5ePCKN5qvX$157dafdfe57db7f8a96499b44590ea2c5a906d4756fc61bab1834310192002bf','archived','andy','buyer',0),(48,'resetpass@gmail.com','pbkdf2:sha256:600000$VqDm53Mg0QX0QSaJ$0f6cef816f08c18736d8c73194687cdd057cf5f06c5ef45fadd3d8060bd340d8','reset','password','buyer',0),(49,'admins@gmail.com','pbkdf2:sha256:600000$ePvk3dFLQG8q59n6$6ee93fe16f9c5337a92e790047e72c0c9771f687523100f411a4af653e1b0d1d','admin','boss','admin',0),(50,'awesomersecommerce@gmail.com','pbkdf2:sha256:1000000$xYW7Ke7H1brSLvdl$00c5149095a86a19bc06900d71fc668a750907a63241367f466eed1ae566e0b0','awesomers','ecommerce','buyer',0),(51,'s21contactemail@gmail.com','pbkdf2:sha256:1000000$gpmd9JqFcYJdRaoN$11dbf53307763b477fcac9fb1bd7044c28390663d195d894b6d926a3c3fc8b2b','slaking','21','buyer',0),(52,'testNew@gmail.com','pbkdf2:sha256:1000000$6O8Cq6c47kb4y05F$addca0ec5f5b2fe8aa380263aed3e4ea8b84d8255cdd0a6dabb8ce6c7f7f3c42','test','new','buyer',0),(53,'buyer2@gmail.com','pbkdf2:sha256:1000000$M26hWWVyjiUPojZV$57b9854582b4634e5ad44ca9a93580e72d22d4ba1814fb61abc51afb67581cdc','buyers','2','buyer',0);

/*Table structure for table `address_books` */

DROP TABLE IF EXISTS `address_books`;

CREATE TABLE `address_books` (
  `addressBookID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `profileID` bigint(20) NOT NULL,
  `addressName` varchar(255) DEFAULT NULL,
  `addressBldg` varchar(255) DEFAULT NULL,
  `addressCity` varchar(255) DEFAULT NULL,
  `addressCountry` varchar(255) DEFAULT NULL,
  `addressProvince` varchar(255) DEFAULT NULL,
  `addressPostal` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`addressBookID`,`accountID`,`profileID`),
  KEY `addressAccountID` (`accountID`),
  KEY `buyerProfileID` (`profileID`),
  CONSTRAINT `addressAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `buyerProfileID` FOREIGN KEY (`profileID`) REFERENCES `profiles_buyer` (`buyerProfileID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `sellerProfileID` FOREIGN KEY (`profileID`) REFERENCES `profiles_seller` (`sellerProfileID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `address_books` */

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
  `brand` varchar(255) DEFAULT 'No brand',
  `description` varchar(255) DEFAULT NULL,
  `category` varchar(255) NOT NULL,
  `subcategory` varchar(255) DEFAULT NULL,
  `variation` varchar(255) NOT NULL,
  `price` int(255) NOT NULL,
  `quantity` int(255) NOT NULL,
  `dateAdded` datetime NOT NULL,
  `dateEdited` datetime DEFAULT NULL,
  `dateArchived` datetime DEFAULT NULL,
  `isActive` tinyint(1) NOT NULL DEFAULT 0,
  `isArchived` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`productID`,`accountID`),
  KEY `productsCategoryID` (`category`),
  KEY `productsSellerID` (`accountID`),
  CONSTRAINT `productsSellerID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `products` */

insert  into `products`(`productID`,`accountID`,`picture`,`productName`,`brand`,`description`,`category`,`subcategory`,`variation`,`price`,`quantity`,`dateAdded`,`dateEdited`,`dateArchived`,`isActive`,`isArchived`) values (1,43,'98e0459f-a4e6-11ef-bbf5-e4f3d99e8070_','haha',NULL,'joji','Desktops',NULL,'Desktops',1000,1,'2024-11-10 12:05:14',NULL,NULL,0,0),(2,43,NULL,'joji',NULL,'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor i','vlogs',NULL,'filthy, frank',1000,0,'2024-11-10 12:05:14',NULL,NULL,0,0),(3,43,NULL,'a',NULL,'a','a',NULL,'a',0,0,'2024-11-10 12:05:14',NULL,NULL,0,1),(4,43,NULL,'asd',NULL,'asd','asdaas',NULL,'asda',2325,129,'2024-11-10 13:18:19',NULL,NULL,0,1),(5,43,NULL,'asd',NULL,'asd','asd',NULL,'asd',120,127,'2024-11-10 13:20:23',NULL,NULL,1,1),(6,43,NULL,'asd',NULL,'asd','asd',NULL,'asd',123,123,'2024-11-10 13:21:25',NULL,NULL,1,1),(7,43,'0c0749e1-aa46-11ef-a2df-3c7c3f2bb6c4_','aproduct1','None','asd','asdaas',NULL,'asd',123,123,'2024-11-10 13:22:14','2024-11-24 17:25:29',NULL,1,0),(8,43,NULL,'TANGINA MO',NULL,'XD PA MORE ASSHOLE','asd',NULL,'asd',2000,6,'2024-11-10 13:25:35',NULL,NULL,1,0),(9,43,NULL,'he',NULL,'ewq','qwe',NULL,'dasd',1,1,'2024-11-12 12:06:47',NULL,NULL,1,1),(10,43,NULL,'kasjd',NULL,'lansiod','ansd',NULL,'lasdjpasd',123,10,'2024-11-12 12:11:11',NULL,NULL,1,0),(11,43,NULL,'dsa',NULL,'asd','sdds',NULL,'ssdds',321,123,'2024-11-15 18:26:39',NULL,NULL,1,0),(12,43,NULL,'asdasd',NULL,'asd','Desktops',NULL,'Desktops',123123,123123,'2024-11-15 20:15:13',NULL,NULL,1,0),(13,43,NULL,'jameng house',NULL,'the design is very fun','Desktops',NULL,'Desktops',123,22,'2024-11-16 11:39:17',NULL,NULL,1,0),(14,43,NULL,'asd',NULL,'asdasd','Desktops',NULL,'Desktops',321,123,'2024-11-16 13:00:47',NULL,NULL,1,1),(15,43,NULL,'delete fields',NULL,'delete','Desktops',NULL,'Desktops',2443,23,'2024-11-16 13:05:32',NULL,NULL,1,0),(16,43,NULL,'delete fields',NULL,'321','Desktops',NULL,'Desktops',233,123,'2024-11-16 13:05:42',NULL,NULL,1,1),(17,43,'c82f9897-a68a-11ef-9d70-3c7c3f2bb6c4_','product1','None','123','Desktops',NULL,'Desktops',123,123,'2024-11-16 13:37:29','2024-11-19 23:27:26',NULL,1,0),(18,43,'de4adbf4-a68a-11ef-8a79-3c7c3f2bb6c4_','Because this function is fairly verbose and used frequently in JavaScript, the $ has long been used as its alias, and many of the libraries available for use with JavaScript create a $() function that references an element from the DOM if you pass it the ','None','asdasd','Desktops',NULL,'Desktops',123,321,'2024-11-16 14:16:30','2024-11-19 23:28:03',NULL,1,0),(19,43,NULL,'noImageTest',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 18:13:43',NULL,NULL,0,0),(20,43,NULL,'multipleImageTest',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 18:15:37',NULL,NULL,0,0),(21,43,NULL,'multipleImageTestWithHTMLUpdate',NULL,'','Desktops',NULL,'Desktops',123,3,'2024-11-17 18:20:17',NULL,NULL,0,0),(22,43,'d3a8f69b-a4d1-11ef-b3d9-e4f3d99e8070_Acer_Wallpaper_01_3840x2400.jpg','testExecuteForList',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 18:50:57',NULL,NULL,0,0),(23,43,'d3adcc64-a4d1-11ef-bda4-e4f3d99e8070_Acer_Wallpaper_02_3840x2400.jpg','testExecuteForList',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 18:50:57',NULL,NULL,0,0),(24,43,'d3b02f1b-a4d1-11ef-bea3-e4f3d99e8070_Acer_Wallpaper_03_3840x2400.jpg','testExecuteForList',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 18:50:57',NULL,NULL,0,0),(25,43,'16946f3f-a4d3-11ef-8cd4-e4f3d99e8070_Acer_Wallpaper_01_3840x2400.jpg','testExecutemanySqlVal',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 18:59:59',NULL,NULL,0,0),(26,43,'1696d28f-a4d3-11ef-8949-e4f3d99e8070_Acer_Wallpaper_02_3840x2400.jpg','testExecutemanySqlVal',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 18:59:59',NULL,NULL,0,0),(27,43,'169b9709-a4d3-11ef-820d-e4f3d99e8070_Acer_Wallpaper_03_3840x2400.jpg','testExecutemanySqlVal',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 18:59:59',NULL,NULL,0,0),(28,43,'1381535d-a4e1-11ef-85ae-e4f3d99e8070_','testOneImgFile',NULL,'asd','Desktops',NULL,'Desktops',123,2,'2024-11-17 19:46:14',NULL,NULL,0,0),(29,43,'0bef1cdf-a54c-11ef-8d6b-3c7c3f2bb6c4_','testBrand','brand','','Desktops',NULL,'Desktops',123,3,'2024-11-18 09:25:50',NULL,NULL,0,0),(30,43,'c191e261-a54c-11ef-b2dd-3c7c3f2bb6c4_','testIsActive','','','Desktops',NULL,'Desktops',123,3,'2024-11-18 09:30:55',NULL,NULL,1,0),(31,43,'e3e34179-a54c-11ef-bb48-3c7c3f2bb6c4_','testDefaultbrand','No brand','','Desktops',NULL,'Desktops',123,3,'2024-11-18 09:31:53',NULL,NULL,0,0),(32,43,'b7fddd45-a54f-11ef-ae0c-3c7c3f2bb6c4_','testDateEditedArchived','No brand','','Desktops',NULL,'Desktops',123,3,'2024-11-18 09:52:07',NULL,NULL,0,0),(33,43,'0002b8ce-a550-11ef-af14-3c7c3f2bb6c4_','testDateWhenEdited','No brand','edited here','Desktops',NULL,'Desktops',123,3,'2024-11-18 09:53:48','2024-11-18 09:54:08',NULL,0,0),(34,43,'0a674c7a-a62b-11ef-b0e7-3c7c3f2bb6c4_','testDelete','No brand','','Desktops',NULL,'Desktops',4444,4,'2024-11-19 12:02:06',NULL,NULL,0,0),(35,43,'5a11adbc-a684-11ef-bd3c-3c7c3f2bb6c4_','testActivated','No brand','','Desktops',NULL,'Desktops',123,3,'2024-11-19 22:41:24',NULL,NULL,0,0),(36,43,'793f22c7-a7dd-11ef-a87a-3c7c3f2bb6c4_','testEditJojiWithNewUpdate','No brand','','Desktops',NULL,'Desktops',123,3,'2024-11-21 15:51:53',NULL,NULL,0,0),(37,43,'a77f3ce4-a7dd-11ef-90aa-3c7c3f2bb6c4_','testBrand1','No brand','','Desktops',NULL,'Desktops',123,3,'2024-11-21 15:53:11',NULL,NULL,0,0),(38,43,'60325534-a982-11ef-b8a8-3c7c3f2bb6c4_','testAlert','No brand','','Desktops',NULL,'Desktops',123,3,'2024-11-23 18:04:49',NULL,NULL,0,0);

/*Table structure for table `products_admin` */

DROP TABLE IF EXISTS `products_admin`;

CREATE TABLE `products_admin` (
  `productAdminID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `picture` longblob DEFAULT NULL,
  `productName` varchar(255) NOT NULL,
  `brand` varchar(255) DEFAULT 'No brand',
  `description` varchar(255) DEFAULT NULL,
  `category` varchar(255) NOT NULL,
  `subcategory` varchar(255) DEFAULT NULL,
  `variation` varchar(255) NOT NULL,
  `price` int(255) NOT NULL,
  `quantity` int(255) NOT NULL,
  `dateAdded` datetime NOT NULL,
  `dateEdited` datetime DEFAULT NULL,
  `dateArchived` datetime DEFAULT NULL,
  `isArchived` tinyint(1) NOT NULL DEFAULT 0,
  `isActive` tinyint(1) NOT NULL DEFAULT 0,
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

/*Table structure for table `products_imgs` */

DROP TABLE IF EXISTS `products_imgs`;

CREATE TABLE `products_imgs` (
  `productImgId` bigint(20) NOT NULL AUTO_INCREMENT,
  `productID` bigint(20) NOT NULL,
  `accountID` bigint(20) NOT NULL,
  `picture` longblob DEFAULT NULL,
  PRIMARY KEY (`productImgId`,`productID`,`accountID`),
  KEY `imgSellerID` (`accountID`),
  KEY `imgProductAdminID` (`productID`),
  CONSTRAINT `imgProductAdminID` FOREIGN KEY (`productID`) REFERENCES `products_admin` (`productAdminID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `imgProductID` FOREIGN KEY (`productID`) REFERENCES `products` (`productID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `imgSellerID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `products_imgs` */

/*Table structure for table `profiles_buyer` */

DROP TABLE IF EXISTS `profiles_buyer`;

CREATE TABLE `profiles_buyer` (
  `buyerProfileID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `buyerFirstName` varchar(255) NOT NULL,
  `buyerLastName` varchar(255) NOT NULL,
  `buyerPicture` longblob NOT NULL,
  `buyerPhoneNum` varchar(255) NOT NULL,
  `buyerCountry` varchar(255) NOT NULL,
  `buyerDateCreated` datetime NOT NULL,
  `buyerDateEdited` datetime DEFAULT NULL,
  `isArchived` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`buyerProfileID`,`accountID`),
  KEY `buyerProfileAccountID` (`accountID`),
  CONSTRAINT `buyerProfileAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `profiles_buyer` */

insert  into `profiles_buyer`(`buyerProfileID`,`accountID`,`buyerFirstName`,`buyerLastName`,`buyerPicture`,`buyerPhoneNum`,`buyerCountry`,`buyerDateCreated`,`buyerDateEdited`,`isArchived`) values (6,42,'buyer','jones','42_hot_wheels.jpg','09771231237','Philippines','2024-11-24 21:55:32','2024-11-24 23:48:15',0);

/*Table structure for table `profiles_seller` */

DROP TABLE IF EXISTS `profiles_seller`;

CREATE TABLE `profiles_seller` (
  `sellerProfileID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `storeName` varchar(255) NOT NULL,
  `storePicture` longblob NOT NULL,
  `storePhoneNum` varchar(255) NOT NULL,
  `storeCountry` varchar(255) NOT NULL,
  `storeDateCreated` datetime NOT NULL,
  `storeDateEdited` datetime DEFAULT NULL,
  `isArchived` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`sellerProfileID`,`accountID`),
  KEY `sellerProfileAccountID` (`accountID`),
  CONSTRAINT `sellerProfileAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `profiles_seller` */

insert  into `profiles_seller`(`sellerProfileID`,`accountID`,`storeName`,`storePicture`,`storePhoneNum`,`storeCountry`,`storeDateCreated`,`storeDateEdited`,`isArchived`) values (6,43,'gigamax','43_i_love_bts.jpg','09123456677','Philippines','2024-11-24 21:59:18','2024-11-25 00:03:55',0);

/*Table structure for table `requests` */

DROP TABLE IF EXISTS `requests`;

CREATE TABLE `requests` (
  `requestID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `accountEmail` varchar(255) NOT NULL,
  `accountFirstName` varchar(255) NOT NULL,
  `accountLastName` varchar(255) NOT NULL,
  `validIDType` varchar(255) NOT NULL,
  `pictureValidID` longblob NOT NULL,
  `validIDFullName` varchar(255) NOT NULL,
  `validIDNum` varchar(255) NOT NULL,
  `bankName` varchar(255) NOT NULL,
  `pictureBankDocument` longblob NOT NULL,
  `bankAccName` varchar(255) NOT NULL,
  `bankAccNum` varchar(255) NOT NULL,
  `requestType` varchar(255) NOT NULL,
  `requestDateCreated` datetime NOT NULL,
  `requestArchived` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`requestID`,`accountID`),
  UNIQUE KEY `requestsAccountEmail` (`accountEmail`),
  KEY `requestsAccountID` (`accountID`),
  CONSTRAINT `requestAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `requests` */

insert  into `requests`(`requestID`,`accountID`,`accountEmail`,`accountFirstName`,`accountLastName`,`validIDType`,`pictureValidID`,`validIDFullName`,`validIDNum`,`bankName`,`pictureBankDocument`,`bankAccName`,`bankAccNum`,`requestType`,`requestDateCreated`,`requestArchived`) values (4,26,'demerin@gmail.com','','','','','','','','','','','BUYER TO BE SELLER','0000-00-00 00:00:00',1),(23,43,'seller@gmail.com','','','','','','','','','','','BUYER TO BE SELLER','0000-00-00 00:00:00',1),(34,42,'buyer@gmail.com','buyer','jones','Passport','42_test.png','jeprox','123321','bangko','42_pirateAdobeProducts.png','jeprox','322311','Seller registration','2024-11-25 00:01:05',0);

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
