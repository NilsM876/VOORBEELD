-- MySQL dump 10.13  Distrib 8.4.9, for Win64 (x86_64)
--
-- Host: pdbmbook.com    Database: db2026_25
-- ------------------------------------------------------
-- Server version	8.4.11-0ubuntu0.26.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `asset`
--

DROP TABLE IF EXISTS `asset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `asset` (
  `asset_id` int NOT NULL AUTO_INCREMENT,
  `ticker` varchar(30) NOT NULL,
  `exchange` varchar(30) DEFAULT NULL,
  `asset_name` varchar(200) DEFAULT NULL,
  `currency` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`asset_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `asset`
--

LOCK TABLES `asset` WRITE;
/*!40000 ALTER TABLE `asset` DISABLE KEYS */;
INSERT INTO `asset` VALUES (1,'Fictief Alpha',NULL,NULL,NULL),(2,'Fictief Beta',NULL,NULL,NULL),(3,'Fictief Gamma',NULL,NULL,NULL),(4,'Fictief Delta',NULL,NULL,NULL);
/*!40000 ALTER TABLE `asset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comment`
--

DROP TABLE IF EXISTS `comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comment` (
  `comment_id` int NOT NULL AUTO_INCREMENT,
  `portfolio_id` int NOT NULL,
  `user_id` int NOT NULL,
  `content` text NOT NULL,
  `created_at` timestamp NOT NULL,
  `parent_comment_id` int DEFAULT NULL,
  PRIMARY KEY (`comment_id`),
  KEY `portfolio_id` (`portfolio_id`),
  KEY `user_id` (`user_id`),
  KEY `parent_comment_id` (`parent_comment_id`),
  CONSTRAINT `comment_ibfk_1` FOREIGN KEY (`portfolio_id`) REFERENCES `portfolio` (`portfolio_id`),
  CONSTRAINT `comment_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`),
  CONSTRAINT `comment_ibfk_3` FOREIGN KEY (`parent_comment_id`) REFERENCES `comment` (`comment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comment`
--

LOCK TABLES `comment` WRITE;
/*!40000 ALTER TABLE `comment` DISABLE KEYS */;
/*!40000 ALTER TABLE `comment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `leaderboardentry`
--

DROP TABLE IF EXISTS `leaderboardentry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leaderboardentry` (
  `entry_id` int NOT NULL AUTO_INCREMENT,
  `analysis_id` int NOT NULL,
  `user_id` int NOT NULL,
  `published_at` timestamp NOT NULL,
  `is_visible` tinyint(1) NOT NULL,
  PRIMARY KEY (`entry_id`),
  UNIQUE KEY `analysis_id` (`analysis_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `leaderboardentry_ibfk_1` FOREIGN KEY (`analysis_id`) REFERENCES `portfolioanalysis` (`analysis_id`),
  CONSTRAINT `leaderboardentry_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leaderboardentry`
--

LOCK TABLES `leaderboardentry` WRITE;
/*!40000 ALTER TABLE `leaderboardentry` DISABLE KEYS */;
INSERT INTO `leaderboardentry` VALUES (1,1,1,'2026-10-27 12:52:35',1),(2,2,2,'2026-10-27 12:52:35',1),(3,3,3,'2026-10-27 12:52:36',1);
/*!40000 ALTER TABLE `leaderboardentry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `optimizedholding`
--

DROP TABLE IF EXISTS `optimizedholding`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `optimizedholding` (
  `analysis_id` int NOT NULL,
  `asset_id` int NOT NULL,
  `weight` decimal(10,8) NOT NULL,
  PRIMARY KEY (`analysis_id`,`asset_id`),
  KEY `asset_id` (`asset_id`),
  CONSTRAINT `optimizedholding_ibfk_1` FOREIGN KEY (`analysis_id`) REFERENCES `portfolioanalysis` (`analysis_id`),
  CONSTRAINT `optimizedholding_ibfk_2` FOREIGN KEY (`asset_id`) REFERENCES `asset` (`asset_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `optimizedholding`
--

LOCK TABLES `optimizedholding` WRITE;
/*!40000 ALTER TABLE `optimizedholding` DISABLE KEYS */;
INSERT INTO `optimizedholding` VALUES (1,1,0.33333333),(1,2,0.66666667),(2,3,1.00000000);
/*!40000 ALTER TABLE `optimizedholding` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `portfolio`
--

DROP TABLE IF EXISTS `portfolio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `portfolio` (
  `portfolio_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `portfolio_name` varchar(150) NOT NULL,
  `is_public` tinyint(1) NOT NULL,
  `created_at` timestamp NOT NULL,
  PRIMARY KEY (`portfolio_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `portfolio_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `portfolio`
--

LOCK TABLES `portfolio` WRITE;
/*!40000 ALTER TABLE `portfolio` DISABLE KEYS */;
INSERT INTO `portfolio` VALUES (1,1,'Portefeuille van persoon A',1,'2026-10-27 12:52:35'),(2,2,'Portefeuille van persoon B',1,'2026-10-27 12:52:35'),(3,3,'Portefeuille van persoon C',1,'2026-10-27 12:52:36');
/*!40000 ALTER TABLE `portfolio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `portfolioanalysis`
--

DROP TABLE IF EXISTS `portfolioanalysis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `portfolioanalysis` (
  `analysis_id` int NOT NULL AUTO_INCREMENT,
  `portfolio_id` int NOT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `risk_free_rate` decimal(12,8) DEFAULT NULL,
  `annual_return` decimal(12,8) DEFAULT NULL,
  `annual_volatility` decimal(12,8) DEFAULT NULL,
  `sharpe_ratio` decimal(12,8) DEFAULT NULL,
  `optimized_return` decimal(12,8) DEFAULT NULL,
  `optimized_volatility` decimal(12,8) DEFAULT NULL,
  `optimized_sharpe` decimal(12,8) DEFAULT NULL,
  `optimization_method` varchar(100) DEFAULT NULL,
  `calculation_version` varchar(30) DEFAULT NULL,
  `calculated_at` timestamp NOT NULL,
  PRIMARY KEY (`analysis_id`),
  KEY `portfolio_id` (`portfolio_id`),
  CONSTRAINT `portfolioanalysis_ibfk_1` FOREIGN KEY (`portfolio_id`) REFERENCES `portfolio` (`portfolio_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `portfolioanalysis`
--

LOCK TABLES `portfolioanalysis` WRITE;
/*!40000 ALTER TABLE `portfolioanalysis` DISABLE KEYS */;
INSERT INTO `portfolioanalysis` VALUES (1,1,NULL,NULL,0.02000000,0.08400000,0.12649111,0.50596443,0.07333333,0.09428090,0.56568542,'Hoogste Sharpe ratio bij nulcorrelaties','1','2026-10-27 12:52:35'),(2,2,NULL,NULL,0.02000000,0.08000000,0.15000000,0.40000000,0.08000000,0.15000000,0.40000000,'Hoogste Sharpe ratio bij nulcorrelaties','1','2026-10-27 12:52:35'),(3,3,NULL,NULL,0.02000000,0.01000000,0.10000000,-0.10000000,NULL,NULL,NULL,'Hoogste Sharpe ratio bij nulcorrelaties','1','2026-10-27 12:52:36');
/*!40000 ALTER TABLE `portfolioanalysis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `portfolioholding`
--

DROP TABLE IF EXISTS `portfolioholding`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `portfolioholding` (
  `portfolio_id` int NOT NULL,
  `asset_id` int NOT NULL,
  `amount` decimal(18,2) NOT NULL,
  `expected_return` decimal(12,8) NOT NULL,
  `volatility` decimal(12,8) NOT NULL,
  `price` decimal(18,6) DEFAULT NULL,
  `input_weight` decimal(10,8) DEFAULT NULL,
  `optimized_weight` decimal(10,8) DEFAULT NULL,
  PRIMARY KEY (`portfolio_id`,`asset_id`),
  KEY `asset_id` (`asset_id`),
  CONSTRAINT `portfolioholding_ibfk_1` FOREIGN KEY (`portfolio_id`) REFERENCES `portfolio` (`portfolio_id`),
  CONSTRAINT `portfolioholding_ibfk_2` FOREIGN KEY (`asset_id`) REFERENCES `asset` (`asset_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `portfolioholding`
--

LOCK TABLES `portfolioholding` WRITE;
/*!40000 ALTER TABLE `portfolioholding` DISABLE KEYS */;
INSERT INTO `portfolioholding` VALUES (1,1,600.00,0.10000000,0.20000000,NULL,0.60000000,0.33333333),(1,2,400.00,0.06000000,0.10000000,NULL,0.40000000,0.66666667),(2,3,1000.00,0.08000000,0.15000000,NULL,1.00000000,1.00000000),(3,4,1000.00,0.01000000,0.10000000,NULL,1.00000000,NULL);
/*!40000 ALTER TABLE `portfolioholding` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `portfoliounlock`
--

DROP TABLE IF EXISTS `portfoliounlock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `portfoliounlock` (
  `user_id` int NOT NULL,
  `portfolio_id` int NOT NULL,
  `amount_eur` decimal(6,2) NOT NULL,
  `unlocked_at` timestamp NOT NULL,
  PRIMARY KEY (`user_id`,`portfolio_id`),
  KEY `portfolio_id` (`portfolio_id`),
  CONSTRAINT `portfoliounlock_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`),
  CONSTRAINT `portfoliounlock_ibfk_2` FOREIGN KEY (`portfolio_id`) REFERENCES `portfolio` (`portfolio_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `portfoliounlock`
--

LOCK TABLES `portfoliounlock` WRITE;
/*!40000 ALTER TABLE `portfoliounlock` DISABLE KEYS */;
/*!40000 ALTER TABLE `portfoliounlock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription`
--

DROP TABLE IF EXISTS `subscription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription` (
  `subscription_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `payment_provider_id` varchar(255) DEFAULT NULL,
  `subscription_status` varchar(30) NOT NULL,
  `start_date` timestamp NULL DEFAULT NULL,
  `end_date` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`subscription_id`),
  UNIQUE KEY `payment_provider_id` (`payment_provider_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `subscription_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription`
--

LOCK TABLES `subscription` WRITE;
/*!40000 ALTER TABLE `subscription` DISABLE KEYS */;
/*!40000 ALTER TABLE `subscription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'persoon A','persoon A@sharply.local','geen login','2026-10-27 12:52:35'),(2,'persoon B','persoon B@sharply.local','geen login','2026-10-27 12:52:35'),(3,'persoon C','persoon C@sharply.local','geen login','2026-10-27 12:52:36');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-27 13:03:47
