CREATE TABLE `news_content` (
  `no` unsigned NOT NULL AUTO_INCREMENT,
  `news_id` varchar(100) NOT NULL,
  `date` date DEFAULT NULL,
  `time` time DEFAULT NULL,
  `source` varchar(10) DEFAULT NULL,
  `title` varchar(50) DEFAULT NULL,
  `reporter` varchar(45) DEFAULT NULL,
  `link` text,
  `content` longtext,
  PRIMARY KEY (`no`),
  UNIQUE KEY `no_UNIQUE` (`no`),
  UNIQUE KEY `news_id_UNIQUE` (`news_id`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `news_tag` (
  `no` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `source` varchar(10) NOT NULL,
  `news_id` varchar(100) NOT NULL,
  `tag` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`no`),
  KEY `FK_news_tag_news_id_idx` (`news_id`),
  CONSTRAINT `FK_news_tag_news_id` FOREIGN KEY (`news_id`) REFERENCES `news_content` (`news_id`)
) ENGINE=InnoDB AUTO_INCREMENT=102 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci