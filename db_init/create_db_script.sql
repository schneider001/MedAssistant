CREATE TABLE IF NOT EXISTS `doctors` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `username` varchar(255) UNIQUE NOT NULL,
  `name` varchar(255),
  `password_hash` blob NOT NULL,
  `last_login` timestamp
);

CREATE TABLE IF NOT EXISTS `patients` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `insurance_certificate` varchar(255) UNIQUE NOT NULL,
  `born_date` timestamp,
  `sex` ENUM ('MALE', 'FEMAIL')
);

CREATE TABLE IF NOT EXISTS `administrators` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `username` varchar(255) UNIQUE NOT NULL,
  `name` varchar(255),
  `password_hash` blob NOT NULL
);

CREATE TABLE IF NOT EXISTS `symptoms` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS `diseases` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS `ml_model` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `hash` blob,
  `version` varchar(255)
);

CREATE TABLE IF NOT EXISTS `requests` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `doctor_id` integer NOT NULL,
  `patient_id` integer NOT NULL,
  `predicted_disease_id` integer,
  `status` ENUM ('IN_PROGRESS', 'READY', 'ERROR') NOT NULL DEFAULT 'IN_PROGRESS',
  `date` timestamp DEFAULT NOW(),
  `ml_model_id` integer,
  FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`id`),
  FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`),
  FOREIGN KEY (`predicted_disease_id`) REFERENCES `diseases` (`id`),
  FOREIGN KEY (`ml_model_id`) REFERENCES `ml_model` (`id`)
);

CREATE TABLE IF NOT EXISTS `request_symptoms` (
  `symptom_id` integer NOT NULL,
  `request_id` integer NOT NULL,
  UNIQUE (`symptom_id` ,`request_id`),
  FOREIGN KEY (`symptom_id`) REFERENCES `symptoms` (`id`),
  FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`)
);

CREATE TABLE IF NOT EXISTS `comments` (
  `doctor_id` integer NOT NULL,
  `request_id` integer NOT NULL,
  `comment` varchar(255) NOT NULL,
  UNIQUE (`doctor_id` ,`request_id`),
  FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`id`),
  FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`)
);