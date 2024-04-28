CREATE TABLE IF NOT EXISTS `lists` (
`list_id`				int(11)		NOT NULL AUTO_INCREMENT		COMMENT 'The id of the list',
`board_id`				int(11)     NOT NULL					COMMENT 'The id of the board this list belongs to',
`list_type`				varchar(5)	NOT NULL	                COMMENT 'The type of this list (to_do, doing, compl)',
PRIMARY KEY (`list_id`),
FOREIGN KEY (`board_id`) REFERENCES boards(`board_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Lists";
