CREATE TABLE IF NOT EXISTS `cards` (
`card_id`				int(11)		NOT NULL AUTO_INCREMENT		COMMENT 'The id of this card',
`board_id`				int(11)		NOT NULL					COMMENT 'The id of the list this card belongs',
`list_type`				int(11)		NOT NULL					COMMENT 'The type of list this card belongs to',
`content`				varchar(255)NOT NULL					COMMENT 'The content of this card',
PRIMARY KEY (`card_id`), 
FOREIGN KEY (`board_id`) REFERENCES boards(`board_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Lists";
  