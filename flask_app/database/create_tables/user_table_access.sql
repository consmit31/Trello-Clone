CREATE TABLE IF NOT EXISTS `user_table_access` (
`user_id`       int(11) NOT NULL,
`board_id`      int(11) NOT NULL,
PRIMARY KEY (`user_id`, `board_id`),
FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
FOREIGN KEY (`board_id`) REFERENCES `boards` (`board_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="User access to boards";