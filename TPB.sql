-- --------------------------------------------------------
-- 호스트:                          127.0.0.1
-- 서버 버전:                        8.0.40 - MySQL Community Server - GPL
-- 서버 OS:                        Win64
-- HeidiSQL 버전:                  12.4.0.6659
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- tpb 데이터베이스 구조 내보내기
CREATE DATABASE IF NOT EXISTS `tpb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `tpb`;

-- 테이블 tpb.item 구조 내보내기
CREATE TABLE IF NOT EXISTS `item` (
  `Inum` int NOT NULL,
  `Iname` varchar(50) NOT NULL DEFAULT '',
  `Istart` date NOT NULL,
  `Istatus` binary(2) NOT NULL DEFAULT '\0\0',
  `Mnum` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`Inum`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='아이템 테이블';

-- 테이블 데이터 tpb.item:~1 rows (대략적) 내보내기
DELETE FROM `item`;
INSERT INTO `item` (`Inum`, `Iname`, `Istart`, `Istatus`, `Mnum`) VALUES
	(1, 'light', '2024-10-31', _binary 0x3100, 0);

-- 테이블 tpb.map 구조 내보내기
CREATE TABLE IF NOT EXISTS `map` (
  `Mnum` int NOT NULL,
  `Mname` varchar(20) NOT NULL DEFAULT '',
  `Mpremap` varchar(20) NOT NULL DEFAULT '',
  `Mstatus` varchar(20) NOT NULL DEFAULT '',
  `Mvisited` binary(2) NOT NULL DEFAULT '\0\0',
  PRIMARY KEY (`Mnum`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='맵 테이블';

-- 테이블 데이터 tpb.map:~1 rows (대략적) 내보내기
DELETE FROM `map`;
INSERT INTO `map` (`Mnum`, `Mname`, `Mpremap`, `Mstatus`, `Mvisited`) VALUES
	(1, 'start', '', '', _binary 0x0000);

-- 테이블 tpb.question 구조 내보내기
CREATE TABLE IF NOT EXISTS `question` (
  `Qnum` int NOT NULL,
  `Qname` varchar(300) NOT NULL DEFAULT '',
  `Qanswer` varchar(200) NOT NULL DEFAULT '',
  `Qstatus` binary(20) NOT NULL DEFAULT '\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0',
  `Qlocation` varchar(40) NOT NULL DEFAULT '',
  `Qreward` varchar(100) NOT NULL DEFAULT '',
  `Qprepare` binary(2) NOT NULL DEFAULT '\0\0',
  `Mnum` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`Qnum`),
  KEY `FK__map` (`Mnum`),
  CONSTRAINT `FK__map` FOREIGN KEY (`Mnum`) REFERENCES `map` (`Mnum`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='문제 테이블';

-- 테이블 데이터 tpb.question:~1 rows (대략적) 내보내기
DELETE FROM `question`;
INSERT INTO `question` (`Qnum`, `Qname`, `Qanswer`, `Qstatus`, `Qlocation`, `Qreward`, `Qprepare`, `Mnum`) VALUES
	(1, 'start', 'start', _binary 0x0000000000000000000000000000000000000000, 'start', 'light', _binary 0x0000, 1);

-- 테이블 tpb.user 구조 내보내기
CREATE TABLE IF NOT EXISTS `user` (
  `Unum` int NOT NULL,
  `Uname` varchar(20) DEFAULT NULL,
  `Ustart` date DEFAULT NULL,
  `Utime` int DEFAULT NULL,
  `Ulocation` varchar(50) DEFAULT NULL,
  `Uvisited` varchar(50) DEFAULT NULL,
  `Uitem` varchar(50) DEFAULT NULL,
  `Uendkey1` binary(2) DEFAULT NULL,
  `Uednkey2` binary(2) DEFAULT NULL,
  PRIMARY KEY (`Unum`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='유저정보';

-- 테이블 데이터 tpb.user:~1 rows (대략적) 내보내기
DELETE FROM `user`;
INSERT INTO `user` (`Unum`, `Uname`, `Ustart`, `Utime`, `Ulocation`, `Uvisited`, `Uitem`, `Uendkey1`, `Uednkey2`) VALUES
	(1, 'toby', '2024-10-31', NULL, '1', NULL, NULL, NULL, NULL);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
