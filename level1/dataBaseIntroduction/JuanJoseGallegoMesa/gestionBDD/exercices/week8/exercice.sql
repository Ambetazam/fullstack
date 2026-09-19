CREATE DATABASE colegio;

USE DATABASE colegio;


CREATE TABLE docentes(id_docentes INT AUTOINCREMENT PRIMARY KEY, nombre VARCHAR(100) NOT NULL, correo VARCHAR(100) UNIQUE NOT NULL);
CREATE TABLE categories(id_categories INT AUTOINCREMENT PRIMARY KEY, nombre VARCHAR(80) NOT NULL, description VARCHAR(200));
CREATE TABLE students(id_students INT AUTOINCREMENT PRIMARY KEY, nombre VARCHAR(100) NOT NULL, correo VARCHAR(120) UNIQUE NOT NULL, age INT);
CREATE TABLE courses(id_courses INT AUTOINCREMENT PRIMARY KEY, nombre VARCHAR(100) NOT NULL, hours INT, id_docentes INT NOT NULL, id_categories INT NOT NULL, FOREIGN KEY(id_docentes) REFERENCES docentes(id_docentes), FOREIGN KEY(id_categories) REFERENCES categories(id_categories) );
CREATE TABLE signings(id_signings INT AUTOINCREMENT PRIMARY KEY, id_students INT NOT NULL, id_courses INT NOT NULL, dateSign DATE, finalNote DECIMAL (3,1) NOT NULL, FOREIGN KEY(id_students) REFERENCES students(id_students), FOREIGN KEY(id_courses) REFERENCES courses(id_courses));
