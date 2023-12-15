DROP PROCEDURE IF EXISTS drop_all_tables;

DELIMITER $$
CREATE PROCEDURE drop_all_tables()
BEGIN
    DECLARE _done INT DEFAULT FALSE;
    DECLARE _tableName VARCHAR(255);
    DECLARE _cursor CURSOR FOR
        SELECT table_name 
        FROM information_schema.TABLES
        WHERE table_schema = SCHEMA();
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET _done = TRUE;

    SET FOREIGN_KEY_CHECKS = 0;

    OPEN _cursor;

    REPEAT FETCH _cursor INTO _tableName;

    IF NOT _done THEN
        SET @stmt_sql = CONCAT('DROP TABLE ', _tableName);
        PREPARE stmt1 FROM @stmt_sql;
        EXECUTE stmt1;
        DEALLOCATE PREPARE stmt1;
    END IF;

    UNTIL _done END REPEAT;

    CLOSE _cursor;
    SET FOREIGN_KEY_CHECKS = 1;
END$$

DELIMITER ;

call drop_all_tables(); 

DROP PROCEDURE IF EXISTS `drop_all_tables`;

CREATE TABLE `doctors` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `username` varchar(255) UNIQUE NOT NULL,
  `name` varchar(255),
  `password_hash` blob NOT NULL,
  `last_login` timestamp,
  FULLTEXT KEY(name)
);

CREATE TABLE `patients` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `insurance_certificate` varchar(255) UNIQUE NOT NULL,
  `born_date` timestamp,
  `sex` ENUM ('MALE', 'FEMALE', 'OTHER'),
  FULLTEXT KEY(name),
  FULLTEXT KEY(insurance_certificate)
);

CREATE TABLE `administrators` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `username` varchar(255) UNIQUE NOT NULL,
  `name` varchar(255),
  `password_hash` blob NOT NULL
);

CREATE TABLE `symptoms` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) UNIQUE NOT NULL,
  `ru_name` varchar(255) UNIQUE NOT NULL,
  FULLTEXT KEY(ru_name)
);

CREATE TABLE `diseases` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) UNIQUE NOT NULL,
  `ru_name` varchar(255) UNIQUE NOT NULL,
  FULLTEXT KEY(ru_name)
);

CREATE TABLE `ml_model` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `hash` blob,
  `version` varchar(255)
);

CREATE TABLE `requests` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `doctor_id` integer NOT NULL,
  `patient_id` integer NOT NULL,
  `predicted_disease_id` integer,
  `status` ENUM ('IN_PROGRESS', 'READY', 'ERROR') NOT NULL DEFAULT 'IN_PROGRESS',
  `date` timestamp DEFAULT NOW(),
  `ml_model_id` integer,
  `is_commented` boolean DEFAULT FALSE,
  FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`id`),
  FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`),
  FOREIGN KEY (`predicted_disease_id`) REFERENCES `diseases` (`id`),
  FOREIGN KEY (`ml_model_id`) REFERENCES `ml_model` (`id`)
);

CREATE TABLE `request_symptoms` (
  `symptom_id` integer NOT NULL,
  `request_id` integer NOT NULL,
  UNIQUE (`symptom_id` ,`request_id`),
  FOREIGN KEY (`symptom_id`) REFERENCES `symptoms` (`id`),
  FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`)
);

CREATE TABLE `comments` (
  `id` integer PRIMARY KEY AUTO_INCREMENT, 
  `doctor_id` integer NOT NULL,
  `request_id` integer NOT NULL,
  `comment` varchar(255) NOT NULL,
  `date` timestamp DEFAULT NOW(),
  `status` ENUM ('OLD', 'NEW') DEFAULT 'NEW',
  FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`id`),
  FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`)
);

DROP TRIGGER IF EXISTS after_comment_insert;

DELIMITER $$
CREATE TRIGGER after_comment_insert
AFTER INSERT
ON comments FOR EACH ROW
BEGIN
   UPDATE requests
   SET is_commented = TRUE
   WHERE id = NEW.request_id;
END;$$
DELIMITER ;

DROP TRIGGER IF EXISTS after_comment_update;

DELIMITER $$
CREATE TRIGGER after_comment_update
AFTER UPDATE
ON comments FOR EACH ROW
BEGIN
   IF OLD.status = 'NEW' AND NEW.status = 'OLD' THEN
      IF NOT EXISTS (SELECT 1 FROM comments WHERE request_id = OLD.request_id AND status = 'NEW') THEN
         UPDATE requests
         SET is_commented = FALSE
         WHERE id = OLD.request_id;
      END IF;
   ELSEIF OLD.status = 'OLD' AND NEW.status = 'NEW' THEN
      UPDATE requests
      SET is_commented = TRUE
      WHERE id = NEW.request_id;
   END IF;
END;$$
DELIMITER ;