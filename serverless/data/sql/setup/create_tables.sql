DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS dones;

CREATE TABLE `tasks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(1024) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `dones` (
  `id` int NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `dones_ibfk_1` FOREIGN KEY (`id`) REFERENCES `tasks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_c;


