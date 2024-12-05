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
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `accounts` */

insert  into `accounts`(`accountID`,`accountEmail`,`accountPassword`,`accountFirstName`,`accountLastName`,`accountRole`,`accountArchived`) values (26,'demerin@gmail.com','pbkdf2:sha256:600000$zaQaIx2olb3woHic$55ddd820d7ecfc260af69ba51c7763424bd546c1e5a88d3c82767b17ea777dd3','luke','demerin','seller',0),(42,'buyer@gmail.com','pbkdf2:sha256:600000$M9Qc1Lnd10et2oPc$d547e276b37c80830094ba3fc62005dc763a5b2a8a3e50d30054ee5a8c225da4','buyer','jones','buyer',0),(43,'seller@gmail.com','pbkdf2:sha256:600000$ALe1BW71L6YCXkAQ$837a22a31095bb725d2c0b2b3582f958dc9efb34fb519052166b4239d240b021','seller','scott','seller',0),(46,'admin@gmail.com','pbkdf2:sha256:600000$UQcTCET1xbaFQlTu$cce2ce2a6329e5cf4e88ee3240391cf9ece1d44b32a77cff3317332607ed0516','admin','admin','admin',0),(47,'archived@gmail.com','pbkdf2:sha256:600000$MxJBKn5ePCKN5qvX$157dafdfe57db7f8a96499b44590ea2c5a906d4756fc61bab1834310192002bf','archived','andy','buyer',0),(48,'resetpass@gmail.com','pbkdf2:sha256:600000$VqDm53Mg0QX0QSaJ$0f6cef816f08c18736d8c73194687cdd057cf5f06c5ef45fadd3d8060bd340d8','reset','password','buyer',0),(50,'awesomersecommerce@gmail.com','pbkdf2:sha256:1000000$xYW7Ke7H1brSLvdl$00c5149095a86a19bc06900d71fc668a750907a63241367f466eed1ae566e0b0','awesomers','ecommerce','buyer',0),(52,'testNew@gmail.com','pbkdf2:sha256:1000000$6O8Cq6c47kb4y05F$addca0ec5f5b2fe8aa380263aed3e4ea8b84d8255cdd0a6dabb8ce6c7f7f3c42','test','new','buyer',0),(53,'buyer2@gmail.com','pbkdf2:sha256:1000000$M26hWWVyjiUPojZV$57b9854582b4634e5ad44ca9a93580e72d22d4ba1814fb61abc51afb67581cdc','buyers','2','buyer',0),(56,'admins@gmail.com','pbkdf2:sha256:1000000$dn5PTcENNaBEThz6$2fab09731d8cd6712614047f79d2200cc5eea3c4fbbb5ee4fb430f3f05f1dbb5','admin','2','admin',0);

/*Table structure for table `address_book` */

DROP TABLE IF EXISTS `address_book`;

CREATE TABLE `address_book` (
  `addressBookID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `profileID` bigint(20) NOT NULL,
  `recipientName` varchar(255) NOT NULL,
  `addressCountry` varchar(255) NOT NULL,
  `addressProvince` varchar(255) DEFAULT NULL,
  `addressCity` varchar(255) NOT NULL,
  `addressDistrict` varchar(255) NOT NULL,
  `addressStreetName` varchar(255) NOT NULL,
  `addressUnitName` varchar(255) DEFAULT NULL,
  `addressPostal` varchar(255) NOT NULL,
  `addressPhoneNum` varchar(255) NOT NULL,
  `addressCategory` varchar(255) NOT NULL,
  `addressDateCreated` datetime NOT NULL,
  `addressDateEdited` datetime DEFAULT NULL,
  `isDefault` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`addressBookID`,`accountID`,`profileID`),
  KEY `addressAccountID` (`accountID`),
  KEY `buyerProfileID` (`profileID`),
  CONSTRAINT `addressAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=84 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `address_book` */

insert  into `address_book`(`addressBookID`,`accountID`,`profileID`,`recipientName`,`addressCountry`,`addressProvince`,`addressCity`,`addressDistrict`,`addressStreetName`,`addressUnitName`,`addressPostal`,`addressPhoneNum`,`addressCategory`,`addressDateCreated`,`addressDateEdited`,`isDefault`) values (14,43,7,'seller scott','Philippines','','seller city','vendor strict','7676 street','','9111','09122234121','Home','2024-11-27 00:00:00','2024-12-03 00:00:00',0),(78,43,7,'seller scott','Pitcairn','','12','321','321','','123','09122234121','Home','2024-11-30 00:00:00','2024-12-03 00:00:00',1),(82,42,10,'buyer jones','Philippines','Laguna','city haus','districto','123 st','','1010','09123456677','Home','2024-12-03 17:45:14',NULL,0),(83,42,10,'buyer jones','Philippines','Batangas','batangas city','district mo','9191 st','','19827','09123456677','Home','2024-12-03 17:45:35',NULL,1);

/*Table structure for table `address_store` */

DROP TABLE IF EXISTS `address_store`;

CREATE TABLE `address_store` (
  `addressStoreID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `profileID` bigint(20) NOT NULL,
  `storeName` varchar(255) NOT NULL,
  `storeCountry` varchar(255) NOT NULL,
  `storeProvince` varchar(255) DEFAULT NULL,
  `storeCity` varchar(255) NOT NULL,
  `storeDistrict` varchar(255) NOT NULL,
  `storeStreetName` varchar(255) NOT NULL,
  `storeUnitName` varchar(255) DEFAULT NULL,
  `storePostal` varchar(255) NOT NULL,
  `storePhoneNum` varchar(255) NOT NULL,
  `storeDateCreated` datetime NOT NULL,
  `storeDateEdited` datetime DEFAULT NULL,
  PRIMARY KEY (`addressStoreID`,`accountID`,`profileID`),
  KEY `storeProfileID` (`profileID`),
  CONSTRAINT `storeProfileID` FOREIGN KEY (`profileID`) REFERENCES `profiles_seller` (`sellerProfileID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `address_store` */

insert  into `address_store`(`addressStoreID`,`accountID`,`profileID`,`storeName`,`storeCountry`,`storeProvince`,`storeCity`,`storeDistrict`,`storeStreetName`,`storeUnitName`,`storePostal`,`storePhoneNum`,`storeDateCreated`,`storeDateEdited`) values (4,43,14,'gigamax','Philippines','','123','123','123','123','123','091283','2024-12-01 00:00:00','2024-12-01 00:00:00');

/*Table structure for table `cart` */

DROP TABLE IF EXISTS `cart`;

CREATE TABLE `cart` (
  `cartID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `productID` bigint(20) NOT NULL,
  `cartQuantity` int(255) NOT NULL,
  PRIMARY KEY (`cartID`,`accountID`,`productID`),
  KEY `cartBuyerID` (`accountID`),
  CONSTRAINT `cartBuyerID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `cart` */

insert  into `cart`(`cartID`,`accountID`,`productID`,`cartQuantity`) values (24,53,1,1),(47,42,15,2);

/*Table structure for table `order_details` */

DROP TABLE IF EXISTS `order_details`;

CREATE TABLE `order_details` (
  `orderDetailsID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `sellerProfileID` bigint(20) NOT NULL,
  `buyerAddressID` bigint(20) NOT NULL,
  `orderStatus` varchar(255) NOT NULL,
  `paymentMethod` varchar(255) NOT NULL,
  `datePlaced` datetime DEFAULT NULL,
  `dateShipped` datetime DEFAULT NULL,
  `datePaid` datetime DEFAULT NULL,
  `dateDelivered` datetime DEFAULT NULL,
  `dateCompleted` datetime DEFAULT NULL,
  PRIMARY KEY (`orderDetailsID`,`accountID`,`sellerProfileID`,`buyerAddressID`),
  KEY `orderDetailsAccountID` (`accountID`),
  KEY `addressID` (`buyerAddressID`),
  KEY `storeID` (`sellerProfileID`),
  CONSTRAINT `addressID` FOREIGN KEY (`buyerAddressID`) REFERENCES `address_book` (`addressBookID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `orderDetailsAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `storeID` FOREIGN KEY (`sellerProfileID`) REFERENCES `profiles_seller` (`sellerProfileID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `order_details` */

insert  into `order_details`(`orderDetailsID`,`accountID`,`sellerProfileID`,`buyerAddressID`,`orderStatus`,`paymentMethod`,`datePlaced`,`dateShipped`,`datePaid`,`dateDelivered`,`dateCompleted`) values (7,42,14,83,'To Ship','Cash on Delivery','2024-12-05 21:07:24',NULL,NULL,NULL,NULL);

/*Table structure for table `orders` */

DROP TABLE IF EXISTS `orders`;

CREATE TABLE `orders` (
  `orderID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `productID` bigint(20) NOT NULL,
  `orderDetailsID` bigint(20) NOT NULL,
  `orderQuantity` int(255) NOT NULL,
  PRIMARY KEY (`orderID`,`accountID`,`productID`,`orderDetailsID`),
  KEY `orderAccountID` (`accountID`),
  KEY `orderProductID` (`productID`),
  KEY `orderOrderDetailsID` (`orderDetailsID`),
  CONSTRAINT `orderAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `orderOrderDetailsID` FOREIGN KEY (`orderDetailsID`) REFERENCES `order_details` (`orderDetailsID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `orderProductID` FOREIGN KEY (`productID`) REFERENCES `products` (`productID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `orders` */

insert  into `orders`(`orderID`,`accountID`,`productID`,`orderDetailsID`,`orderQuantity`) values (10,42,41,7,1),(11,42,40,7,4),(12,42,39,7,1);

/*Table structure for table `payment` */

DROP TABLE IF EXISTS `payment`;

CREATE TABLE `payment` (
  `paymentID` bigint(20) NOT NULL AUTO_INCREMENT,
  `accountID` bigint(20) NOT NULL,
  `paymentMethod` varchar(255) NOT NULL,
  PRIMARY KEY (`paymentID`,`accountID`),
  KEY `paymentAccountID` (`accountID`),
  CONSTRAINT `paymentAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `payment` */

/*Table structure for table `product_categories` */

DROP TABLE IF EXISTS `product_categories`;

CREATE TABLE `product_categories` (
  `productCategoryID` bigint(20) NOT NULL AUTO_INCREMENT,
  `productID` bigint(20) NOT NULL,
  `categoryName` varchar(255) NOT NULL,
  PRIMARY KEY (`productCategoryID`,`productID`),
  KEY `categoryProductID` (`productID`),
  CONSTRAINT `categoryProductID` FOREIGN KEY (`productID`) REFERENCES `products` (`productID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `product_categories` */

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
  `quantitySold` int(255) DEFAULT NULL,
  PRIMARY KEY (`productID`,`accountID`),
  KEY `productsCategoryID` (`category`),
  KEY `productsSellerID` (`accountID`),
  CONSTRAINT `productsSellerID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `products` */

insert  into `products`(`productID`,`accountID`,`picture`,`productName`,`brand`,`description`,`category`,`subcategory`,`variation`,`price`,`quantity`,`dateAdded`,`dateEdited`,`dateArchived`,`isActive`,`isArchived`,`quantitySold`) values (1,43,'43_pirateAdobeProducts.png','haha','None','joji','Desktops',NULL,'Desktops',1000,1,'2024-11-10 00:00:00','2024-12-01 00:00:00',NULL,0,0,NULL),(2,43,'43_i_love_bts.jpg','joji','None','Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor i','vlogs',NULL,'filthy, frank',1000,0,'2024-11-10 00:00:00','2024-12-01 00:00:00',NULL,0,0,NULL),(3,43,'43_i_love_bts.jpg','a',NULL,'a','a',NULL,'a',0,0,'2024-11-10 00:00:00',NULL,NULL,0,1,NULL),(4,43,'43_i_love_bts.jpg','asd',NULL,'asd','asdaas',NULL,'asda',2325,129,'2024-11-10 00:00:00',NULL,NULL,0,1,NULL),(5,43,'43_i_love_bts.jpg','asd',NULL,'asd','asd',NULL,'asd',120,127,'2024-11-10 00:00:00',NULL,NULL,1,1,NULL),(6,43,'43_i_love_bts.jpg','asd',NULL,'asd','asd',NULL,'asd',123,123,'2024-11-10 00:00:00',NULL,NULL,1,1,NULL),(7,43,'0c0749e1-aa46-11ef-a2df-3c7c3f2bb6c4_','aproduct1','None','asd','asdaas',NULL,'asd',123,123,'2024-11-10 00:00:00','2024-11-24 00:00:00',NULL,1,1,NULL),(8,43,'43_i_love_bts.jpg','TANGINA MO','None','XD PA MORE ASSHOLE','asd',NULL,'asd',2000,0,'2024-11-10 00:00:00','2024-12-01 00:00:00',NULL,1,0,NULL),(9,43,'43_i_love_bts.jpg','he',NULL,'ewq','qwe',NULL,'dasd',1,1,'2024-11-12 00:00:00',NULL,NULL,1,1,NULL),(10,43,'43_i_love_bts.jpg','kasjd',NULL,'lansiod','ansd',NULL,'lasdjpasd',123,0,'2024-11-12 00:00:00',NULL,NULL,1,0,NULL),(11,43,'43_i_love_bts.jpg','dsa',NULL,'asd','sdds',NULL,'ssdds',321,123,'2024-11-15 00:00:00',NULL,NULL,1,0,NULL),(12,43,'79126b1d-af2a-11ef-bbc7-3c7c3f2bb6c4_','asdasd','None','asd','Desktops',NULL,'Desktops',123123,123123,'2024-11-15 00:00:00','2024-11-30 00:00:00',NULL,1,0,NULL),(13,43,'43_i_love_bts.jpg','jameng house',NULL,'the design is very fun','Desktops',NULL,'Desktops',123,22,'2024-11-16 00:00:00',NULL,NULL,1,0,NULL),(14,43,'43_i_love_bts.jpg','asd',NULL,'asdasd','Desktops',NULL,'Desktops',321,123,'2024-11-16 00:00:00',NULL,NULL,1,1,NULL),(15,43,'7e57e8d8-af2a-11ef-aeb0-3c7c3f2bb6c4_','delete fields','None','delete','Desktops',NULL,'Desktops',2443,23,'2024-11-16 00:00:00','2024-11-30 00:00:00',NULL,1,0,NULL),(16,43,'43_i_love_bts.jpg','delete fields',NULL,'321','Desktops',NULL,'Desktops',233,123,'2024-11-16 00:00:00',NULL,NULL,1,1,NULL),(17,43,'c82f9897-a68a-11ef-9d70-3c7c3f2bb6c4_','product1','None','123','Desktops',NULL,'Desktops',123,123,'2024-11-16 00:00:00','2024-11-19 00:00:00',NULL,1,0,NULL),(18,43,'de4adbf4-a68a-11ef-8a79-3c7c3f2bb6c4_','Because this function is fairly verbose and used frequently in JavaScript, the $ has long been used as its alias, and many of the libraries available for use with JavaScript create a $() function that references an element from the DOM if you pass it the ','None','asdasd','Desktops',NULL,'Desktops',123,321,'2024-11-16 00:00:00','2024-11-19 00:00:00',NULL,1,1,NULL),(19,43,'43_i_love_bts.jpg','noImageTest',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 00:00:00',NULL,NULL,0,0,NULL),(20,43,'43_i_love_bts.jpg','multipleImageTest',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 00:00:00',NULL,NULL,0,0,NULL),(21,43,'43_i_love_bts.jpg','multipleImageTestWithHTMLUpdate',NULL,'','Desktops',NULL,'Desktops',123,0,'2024-11-17 00:00:00',NULL,NULL,0,0,NULL),(22,43,'d3a8f69b-a4d1-11ef-b3d9-e4f3d99e8070_Acer_Wallpaper_01_3840x2400.jpg','testExecuteForList',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 00:00:00',NULL,NULL,0,0,NULL),(23,43,'d3adcc64-a4d1-11ef-bda4-e4f3d99e8070_Acer_Wallpaper_02_3840x2400.jpg','testExecuteForList',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 00:00:00',NULL,NULL,0,0,NULL),(24,43,'d3b02f1b-a4d1-11ef-bea3-e4f3d99e8070_Acer_Wallpaper_03_3840x2400.jpg','testExecuteForList',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 00:00:00',NULL,NULL,0,0,NULL),(25,43,'16946f3f-a4d3-11ef-8cd4-e4f3d99e8070_Acer_Wallpaper_01_3840x2400.jpg','testExecutemanySqlVal',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 00:00:00',NULL,NULL,0,0,NULL),(26,43,'1696d28f-a4d3-11ef-8949-e4f3d99e8070_Acer_Wallpaper_02_3840x2400.jpg','testExecutemanySqlVal',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 00:00:00',NULL,NULL,0,0,NULL),(27,43,'169b9709-a4d3-11ef-820d-e4f3d99e8070_Acer_Wallpaper_03_3840x2400.jpg','testExecutemanySqlVal',NULL,'','Desktops',NULL,'Desktops',123,321,'2024-11-17 00:00:00',NULL,NULL,0,0,NULL),(28,43,'1381535d-a4e1-11ef-85ae-e4f3d99e8070_','testOneImgFile',NULL,'asd','Desktops',NULL,'Desktops',123,2,'2024-11-17 00:00:00',NULL,NULL,0,0,NULL),(29,43,'0bef1cdf-a54c-11ef-8d6b-3c7c3f2bb6c4_','testBrand','brand','','Desktops',NULL,'Desktops',123,3,'2024-11-18 00:00:00',NULL,NULL,0,0,NULL),(30,43,'c191e261-a54c-11ef-b2dd-3c7c3f2bb6c4_','testIsActive','','','Desktops',NULL,'Desktops',123,3,'2024-11-18 00:00:00',NULL,NULL,1,0,NULL),(31,43,'e3e34179-a54c-11ef-bb48-3c7c3f2bb6c4_','testDefaultbrand','No brand','','Desktops',NULL,'Desktops',123,3,'2024-11-18 00:00:00',NULL,NULL,0,0,NULL),(32,43,'b7fddd45-a54f-11ef-ae0c-3c7c3f2bb6c4_','testDateEditedArchived','No brand','','Desktops',NULL,'Desktops',123,3,'2024-11-18 00:00:00',NULL,NULL,0,0,NULL),(33,43,'0002b8ce-a550-11ef-af14-3c7c3f2bb6c4_','testDateWhenEdited','No brand','edited here','Desktops',NULL,'Desktops',123,3,'2024-11-18 00:00:00','2024-11-18 00:00:00',NULL,0,0,NULL),(34,43,'0a674c7a-a62b-11ef-b0e7-3c7c3f2bb6c4_','testDelete','No brand','','Desktops',NULL,'Desktops',4444,4,'2024-11-19 00:00:00',NULL,NULL,0,0,NULL),(35,43,'5a11adbc-a684-11ef-bd3c-3c7c3f2bb6c4_','testActivated','No brand','','Desktops',NULL,'Desktops',123,3,'2024-11-19 00:00:00',NULL,NULL,0,0,NULL),(36,43,'793f22c7-a7dd-11ef-a87a-3c7c3f2bb6c4_','testEditJojiWithNewUpdate','No brand','','Desktops',NULL,'Desktops',123,3,'2024-11-21 00:00:00',NULL,NULL,0,0,NULL),(37,43,'a77f3ce4-a7dd-11ef-90aa-3c7c3f2bb6c4_','testBrand1','No brand','','Desktops',NULL,'Desktops',123,3,'2024-11-21 00:00:00',NULL,NULL,0,0,NULL),(38,43,'60325534-a982-11ef-b8a8-3c7c3f2bb6c4_','testAlert','No brand','','Desktops',NULL,'Desktops',123,3,'2024-11-23 00:00:00',NULL,NULL,0,0,NULL),(39,43,'3a1c6ede-af2a-11ef-ac07-3c7c3f2bb6c4_','testNewButton','No brand','','Desktops',NULL,'Desktops',123,2,'2024-11-30 00:00:00',NULL,NULL,0,0,1),(40,43,'43_pirateAdobeProducts.png','testNewDate','','','Desktops',NULL,'Desktops',333,29,'2024-12-03 00:00:00',NULL,NULL,0,0,4),(41,43,'43_hot_wheels.jpg','testLatest','No brand','3','Desktops',NULL,'Desktops',123,2,'2024-12-03 00:00:00',NULL,NULL,0,0,1),(42,43,'43_pirateAdobeProducts.png','testNewDateTime','No brand','','Desktops',NULL,'Desktops',3332,0,'2024-12-03 06:58:02','2024-12-03 07:38:06',NULL,0,0,NULL);

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
  CONSTRAINT `profileAccountID` FOREIGN KEY (`accountID`) REFERENCES `accounts` (`accountID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `profiles_buyer` */

insert  into `profiles_buyer`(`buyerProfileID`,`accountID`,`buyerFirstName`,`buyerLastName`,`buyerPicture`,`buyerPhoneNum`,`buyerCountry`,`buyerDateCreated`,`buyerDateEdited`,`isArchived`) values (7,43,'seller','scott','43_pirateAdobeProducts.png','09122234121','Philippines','2024-11-26 00:00:00',NULL,0),(10,42,'buyer','jones','42_test.png','09123456677','Philippines','2024-11-29 00:00:00','2024-12-01 00:00:00',0);

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
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `profiles_seller` */

insert  into `profiles_seller`(`sellerProfileID`,`accountID`,`storeName`,`storePicture`,`storePhoneNum`,`storeCountry`,`storeDateCreated`,`storeDateEdited`,`isArchived`) values (14,43,'gigamax','43_hot_wheels.jpg','091283','Philippines','2024-12-01 00:00:00',NULL,0);

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
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `requests` */

insert  into `requests`(`requestID`,`accountID`,`accountEmail`,`accountFirstName`,`accountLastName`,`validIDType`,`pictureValidID`,`validIDFullName`,`validIDNum`,`bankName`,`pictureBankDocument`,`bankAccName`,`bankAccNum`,`requestType`,`requestDateCreated`,`requestArchived`) values (4,26,'demerin@gmail.com','','','','','','','','','','','BUYER TO BE SELLER','0000-00-00 00:00:00',1),(35,42,'buyer@gmail.com','buyer','jones','Passport','42_pirateAdobeProducts.png','jeprox','0122','bangko','42_i_love_bts.jpg','jeprox','2100','Seller registration','2024-11-25 00:00:00',0),(36,43,'seller@gmail.com','seller','scott','Driver\'s License','43_i_love_bts.jpg','jopay','1212','bangkosp','43_test.png','japoy','2233','Seller registration','2024-11-25 00:00:00',1);

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
