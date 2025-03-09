drop database if exists db;
create database db;
use db;


create table users(
    id INT PRIMARY KEY AUTO_INCREMENT, 
    name VARCHAR(50), 
    email VARCHAR(50), 
    password VARCHAR(255)
    );

create table prediction1 (
    id INT PRIMARY KEY AUTO_INCREMENT, 
    email VARCHAR(225),
    name VARCHAR(50),
    disease VARCHAR(1000)
    );
    
create table prediction2 (
    id INT PRIMARY KEY AUTO_INCREMENT, 
    email VARCHAR(225),
    name VARCHAR(50),
    disease VARCHAR(1000)
    );
