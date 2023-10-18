CREATE TABLE if not exists `doctors` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `username` varchar(255) UNIQUE NOT NULL,
  `name` varchar(255),
  `password_hash` blob NOT NULL,
  `last_login` timestamp,
  `is_blocked` ENUM ('blocked', 'not_blocked') NOT NULL DEFAULT 'not_blocked'
);

CREATE TABLE if not exists `patients` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `born_date` timestamp,
  `Sex` ENUM ('male', 'female')
);

CREATE TABLE if not exists `administrators` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `username` varchar(255) UNIQUE NOT NULL,
  `name` varchar(255),
  `password_hash` blob NOT NULL
);

CREATE TABLE if not exists `symptoms` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE if not exists `diseases` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) UNIQUE NOT NULL
);

CREATE TABLE if not exists `ml_model` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `hash` blob,
  `version` varchar(255)
);

CREATE TABLE if not exists `requests` (
  `id` integer PRIMARY KEY AUTO_INCREMENT,
  `doctor_id` integer NOT NULL,
  `patient_id` integer NOT NULL,
  `predicted_disease_id` integer,
  `status` ENUM ('in_progress', 'ready', 'error') NOT NULL DEFAULT 'in_progress',
  `date` timestamp DEFAULT NOW(),
  `ml_model_id` integer,
  FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`id`),
  FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`),
  FOREIGN KEY (`predicted_disease_id`) REFERENCES `diseases` (`id`),
  FOREIGN KEY (`ml_model_id`) REFERENCES `ml_model` (`id`)
);

CREATE TABLE if not exists `request_symptoms` (
  `symptom_id` integer NOT NULL,
  `request_id` integer NOT NULL,
  UNIQUE (`symptom_id` ,`request_id`),
  FOREIGN KEY (`symptom_id`) REFERENCES `symptoms` (`id`),
  FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`)
);

CREATE TABLE if not exists `comments` (
  `doctor_id` integer NOT NULL,
  `request_id` integer NOT NULL,
  `comment` varchar(255) NOT NULL,
  UNIQUE (`doctor_id` ,`request_id`),
  FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`id`),
  FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`)
);
