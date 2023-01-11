import sqlite3
import random
import time
from typing import List, Tuple, Set, Optional, Dict
from datetime import datetime

User = Dict[str, str]
USER, MECHANIC, ADMIN = 0, 1, 2


# TODO MOST OF THIS CODE CAN BE REPLACED WITH SMARTER SQL COMMANDS
#  FOR EXAMPLE IN GET ADMIN STATS TO USE SUM AND AVG FIS THIS

def user_dict(login: str, password: str, first_name: str, last_name: str, email: str, access: str) -> User:
    return {
        "login": login,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "access": access
    }


def user_from_list(user_list):
    if len(user_list) != 6:
        return {}
    return user_dict(user_list[0], user_list[2], user_list[3], user_list[4], user_list[5], user_list[6])


def car_dict(license_spz: str, model: str, year: str):
    return {
        "license": license_spz,
        "model": model,
        "year": year
    }


def car_from_list(car_list):
    if len(car_list) != 3:
        return {}
    return car_dict(car_list[0], car_list[1], car_list[2])


def order_dict(order_id, mechanic: Optional[str], customer: str, car_spz: str, worked_hours: int, description: str,
               creation_date: int, price: Optional[int]):
    return {
        "id": order_id,
        "mechanic": mechanic,
        "customer": customer,
        "license": car_spz,
        "worked_hours": worked_hours,
        "description": description,
        "creation_date": datetime.fromtimestamp(creation_date).strftime("%d.%m.%y %H:%M"),
        "price": price
    }


def order_from_list(order_list):
    if len(order_list) != 7 and len(order_list) != 8:
        return {}
    if len(order_list) == 7:
        return order_dict(order_list[0], order_list[1], order_list[2], order_list[3], order_list[4], order_list[5],
                          order_list[6], None)
    return order_dict(order_list[0], order_list[1], order_list[2], order_list[3], order_list[4], order_list[5],
                      order_list[6], order_list[7])


def spare_part_dict(part_id, name: str, price: str, is_part):
    return {
        "id": part_id,
        "name": name,
        "price": price,
        "is_part": is_part == 1
    }


def spare_part_from_list(spare_list):
    if len(spare_list) != 4:
        return {}
    return spare_part_dict(spare_list[0], spare_list[1], spare_list[2], spare_list[3])


#####################################################################################
def add_user(user: User) -> bool:
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        if contains_user(user["login"]):
            return False
        cursor.execute('INSERT INTO users(login,password,first_name,last_name,email,access) values (?,?,?,?,?,?)',
                       (user["login"], user["password"], user["first_name"], user["last_name"], user["email"],
                        user["access"]))
        connection.commit()
        return True


def contains_user(login: str) -> bool:
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        data = cursor.execute('Select login FROM users WHERE login=?', (login,))
        row = data.fetchall()
        return len(row) > 0


def contains_car(spz: str) -> bool:
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        data = cursor.execute('Select license FROM cars WHERE license=?', (spz,))
        row = data.fetchall()
        return len(row) > 0


def get_password(login: str) -> str:
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        data = cursor.execute('Select password FROM users WHERE login=?', (login,))
        password = data.fetchone()[0]
        return password


def get_user(login: str) -> User:
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        user = user_from_list(
            cursor.execute('Select login, password, first_name, last_name, email, access FROM users WHERE login=?',
                           (login,)).fetchone())
        return user


def get_access(login: str) -> Set[int]:
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        rights = cursor.execute('SELECT access FROM users WHERE login=?', (login,)).fetchone()[0]
        return rights


def get_orders_mechanic(login: str):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        orders = cursor.execute('SELECT * FROM orders WHERE mechanic=?', (login,)).fetchall()
        return [order_from_list(order) for order in orders]


def get_orders_customer(login: str):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        orders = cursor.execute('SELECT * FROM orders WHERE customer=?', (login,)).fetchall()
        return [order_from_list(order) for order in orders]


def get_admin_stats():
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        orders = cursor.execute('SELECT * FROM orders').fetchall()
        month = 30
        result = {'total_order_number': len(orders), 'total_price': sum(order[7] for order in orders),
                  'average_order_duration': "No clue", "total_order_number_per_month": len(orders) / month,
                  "total_price_per_month": (sum(order[7] for order in orders)) / month,
                  "average_order_duration_per_month": "No clue"}

        if result['total_order_number'] == 0:
            result['average_price'] = 0
        else:
            result['average_price'] = result['total_price'] / result['total_order_number']


        ret_orders = []
        for order in orders:
            ret_orders.append((order_from_list(order)))



        return result, ret_orders


def get_free_orders():
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        orders = cursor.execute('SELECT * FROM orders WHERE mechanic IS NULL ').fetchall()
        return [order_from_list(order) for order in orders]


def assign_to_order(order_id: int, mechanic):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('UPDATE orders SET mechanic = ? WHERE id = ?', (mechanic, order_id,))
        connection.commit()
        return


# todo check return value
def add_car(car_license, model, year) -> bool:
    # todo check ret values
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO cars(license , model, year) values (?,?, ?)', (car_license, model, year))
        connection.commit()
        return True


def add_user_order(mechanic, customer, car, description):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        worked_hours = 0
        creation_date = int(time.time())
        cursor.execute(
            """INSERT INTO orders(mechanic, customer, car, worked_hours, description, creation_date) 
            values (?, ?, ?, ?, ?, ?)""",
            (mechanic, customer, car, worked_hours, description, creation_date,
             ))
        connection.commit()
        return True


def get_order(order_id):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        order = order_from_list(cursor.execute("""SELECT * FROM orders where id=?""", (order_id,)).fetchone())
        return order


def get_detailed_order(order_id):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        parts = [spare_part_from_list(order) for order in cursor.execute(
            """SELECT id, name, price, is_part FROM spare_part JOIN (select spare_part_id From orders_spare_part where order_id = ?) 
            osp on spare_part.id = osp.spare_part_id""",
            (order_id,)).fetchall()]

        if parts:
            order = order_from_list(cursor.execute("""SELECT order_id, mechanic, customer, car, worked_hours, description, creation_date, SUM(spare_part.price)
    FROM orders
             inner join orders_spare_part osp on orders.id = osp.order_id
             inner join spare_part on osp.spare_part_id = spare_part.id
    where order_id = ?""", (order_id,)).fetchone())
        else:
            order = order_from_list(cursor.execute("""SELECT * FROM orders where id=?""", (order_id,)).fetchone())
            order["price"] = 0

        car = car_from_list(cursor.execute("SELECT license, model, year FROM CARS JOIN (SELECT car FROM orders where id=?) ord on ord.car == cars.license ", (order_id,)).fetchone())
        return order, parts, car


def add_part(name, price, is_part):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO spare_part(name, price, is_part) values (?, ?, ?)', (name, price, is_part))
        part_id = cursor.lastrowid
        connection.commit()
        return part_id


def add_action(name, price):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO spare_part(name, price, is_part) values (?, ?)', (name, price, 0))
        part_id = cursor.lastrowid
        connection.commit()
        return part_id


def modify_description(order_id, description):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('UPDATE orders SET description = ? WHERE id = ?', (description, order_id,))
        connection.commit()
        return True


def delete_part(order_id, part_id):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()

        cursor.execute('DELETE FROM spare_part WHERE id = ?', (part_id,))
        cursor.execute('DELETE FROM orders_spare_part WHERE order_id =  ? AND spare_part_id = ?', (order_id, part_id,))
        connection.commit()
        return


def add_orders_spare_part(name, price, order_id, is_part):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        part_id = add_part(name, price, is_part)
        cursor.execute('INSERT INTO orders_spare_part(order_id, spare_part_id) values (?, ?)', (order_id, part_id))
        connection.commit()
