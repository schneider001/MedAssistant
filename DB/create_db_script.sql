CREATE TABLE `doctors` (
  `id` serial PRIMARY KEY,
  `username` varchar(255),
  `name` varchar(255),
  `password_hash` blob,
  `last_login` timestamp,
  `is_blocked` ENUM ('blocked', 'not_blocked')
);

CREATE TABLE `patients` (
  `id` integer PRIMARY KEY,
  `name` varchar(255),
  `born_date` timestamp,
  `Sex` ENUM ('male', 'female')
);

CREATE TABLE `symptoms` (
  `id` integer PRIMARY KEY,
  `name` varchar(255)
);

CREATE TABLE `diseases` (
  `id` integer PRIMARY KEY,
  `name` varchar(255)
);

CREATE TABLE `requests` (
  `id` integer PRIMARY KEY,
  `doctor_id` integer,
  `patient_id` integer,
  `predicted_disease_id` integer,
  `status` ENUM ('in_progress', 'ready', 'error'),
  `date` timestamp,
  `ml_model_id` integer
);

CREATE TABLE `request_symptoms` (
  `symptom_id` integer,
  `request_id` integer
);

CREATE TABLE `ml_model` (
  `id` integer PRIMARY KEY,
  `hash` blob,
  `version` varchar(255)
);

CREATE TABLE `administrators` (
  `id` integer PRIMARY KEY,
  `username` varchar(255),
  `name` varchar(255),
  `password_hash` blob
);

CREATE TABLE `comments` (
  `doctor_id` integer,
  `request_id` integer,
  `comment` varchar(255)
);

ALTER TABLE `request_symptoms` ADD FOREIGN KEY (`symptom_id`) REFERENCES `symptoms` (`id`);

ALTER TABLE `request_symptoms` ADD FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`);

ALTER TABLE `requests` ADD FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`id`);

ALTER TABLE `requests` ADD FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`);

ALTER TABLE `requests` ADD FOREIGN KEY (`predicted_disease_id`) REFERENCES `diseases` (`id`);

ALTER TABLE `requests` ADD FOREIGN KEY (`ml_model_id`) REFERENCES `ml_model` (`id`);

ALTER TABLE `comments` ADD FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`id`);

ALTER TABLE `comments` ADD FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`);
