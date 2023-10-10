CREATE TABLE `doctors` (
  `id` integer AUTO_INCREMENT PRIMARY KEY,
  `username` varchar(255),
  `password` varchar(255),
  `last_login` timestamp
);

CREATE TABLE `patients` (
  `id` integer PRIMARY KEY,
  `name` varchar(255),
  `age` integer,
  `sex` ENUM ('male', 'female')
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
  `doctor_disease_id` integer,
  `status` ENUM ('in_progress', 'ready', 'error'),
  `date` timestamp,
  `ml_model_id` integer
);

CREATE TABLE `request_symptoms` (
  `symptom_id` integer,
  `request_id` integer
);

CREATE TABLE `doctor_patients` (
  `doctor_id` integer,
  `patient_id` integer
);

CREATE TABLE `request_diseases` (
  `disease_id` integer,
  `request_id` integer,
  `weight` float
);

CREATE TABLE `ml_model` (
  `id` integer PRIMARY KEY,
  `hash` varchar(255),
  `version` varchar(255)
);

ALTER TABLE `request_symptoms` ADD FOREIGN KEY (`symptom_id`) REFERENCES `symptoms` (`id`);

ALTER TABLE `request_symptoms` ADD FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`);

ALTER TABLE `requests` ADD FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`id`);

ALTER TABLE `requests` ADD FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`);

ALTER TABLE `requests` ADD FOREIGN KEY (`doctor_disease_id`) REFERENCES `diseases` (`id`);

ALTER TABLE `doctor_patients` ADD FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`id`);

ALTER TABLE `doctor_patients` ADD FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`);

ALTER TABLE `request_diseases` ADD FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`);

ALTER TABLE `request_diseases` ADD FOREIGN KEY (`disease_id`) REFERENCES `diseases` (`id`);

ALTER TABLE `requests` ADD FOREIGN KEY (`ml_model_id`) REFERENCES `ml_model` (`id`);