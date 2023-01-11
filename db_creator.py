import sqlite3
import random
from typing import List, Tuple, Set


def create_tables() -> None:
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE users
        (login TEXT PRIMARY KEY NOT NULL , 
        password TEXT NOT NULL , 
        first_name TEXT NOT NULL ,
        last_name TEXT NOT NULL ,
        email TEXT NOT NULL ,
        access TEXT NOT NULL 
        )""")

    cursor.execute("""CREATE TABLE cars(
    license TEXT PRIMARY KEY NOT NULL ,
    model TEXT NOT NULL ,
    year DATE NOT NULL 
    )""")

    cursor.execute("""CREATE TABLE orders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mechanic TEXT ,
    customer TEXT NOT NULL ,
    car TEXT NOT NULL ,
    worked_hours INT NOT NULL ,
    description TEXT NOT NULL ,
    creation_date TIMESTAMP NOT NULL ,
    price INT NOT NULL DEFAULT 0,
    FOREIGN KEY (car) REFERENCES cars(license),
    FOREIGN KEY (mechanic) REFERENCES users(login),
    FOREIGN KEY (customer) REFERENCES users(login)
    )""")

    cursor.execute("""CREATE TABLE spare_part (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name VARCHAR(255) NOT NULL,
      price INTEGER(10) NOT NULL,
      is_part INTEGER(1) NOT NULL 
);""")

    cursor.execute("""CREATE TABLE orders_spare_part (
     order_id INTEGER NOT NULL,
     spare_part_id INTEGER NOT NULL,
     PRIMARY KEY (order_id, spare_part_id),
     FOREIGN KEY (order_id) REFERENCES orders(id),
     FOREIGN KEY (spare_part_id) REFERENCES spare_part(id)
);""")

    connection.commit()
    connection.close()


def destroy_database() -> None:
    connection = sqlite3.connect('database.db')
    print("Nothing to delete")
    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
