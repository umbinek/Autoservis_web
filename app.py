from flask import Flask, render_template, redirect, url_for, session, request, abort

import database
from database import *

app = Flask(__name__)
app.secret_key = "hodnětajnéheslo"


def setup_session(username, access):
    session['username'] = username
    session['access'] = access


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'GET':
        print("GET")
        return render_template('register.html')

    access = ""
    for level in (level if level is not None else "" for level in
                  (request.form.get('access0'), request.form.get('access1'), request.form.get('access2'))):
        access += level

    username = request.form['username']
    contains_user(username)
    # todo fix to throw error if all is not filled or there was error while filling
    add_user(user_dict(username, request.form['password'], request.form['first_name'], request.form['last_name'],
                       request.form['email'], access))
    return redirect('/admin')


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    if not contains_user(username):
        return redirect('/home')
    if get_password(username) == request.form['password']:
        setup_session(username, get_access(username))
    return redirect('/home')


@app.route('/home')
def home():
    if 'username' not in session:
        return "Username or Password is wrong!"
    return render_template("home.html", username=session['username'], access=session['access'])


@app.route('/technic_orders')
def technic_orders():
    if '1' not in session['access']:
        abort(401)
    orders = database.get_orders_mechanic(session['username'])
    return render_template('mechanic/technic_orders.html', username=session['username'], orders=orders,
                           access=session['access'])


@app.route('/all_orders')
def all_orders():
    if '1' not in session['access']:
        abort(401)
    orders = database.get_free_orders()
    return render_template('mechanic/all_orders.html', username=session['username'], orders=orders,
                           access=session['access'])


@app.route('/new_order', methods=['POST', "GET"])
def new_order():
    if '0' not in session['access']:
        abort(401)
    if request.method == 'GET':
        return render_template('customer/new_order.html', username=session['username'], access=session['access'])

    spz = request.form['spz']
    model = request.form['model']
    rok = request.form['rok']
    description = request.form['popis']

    if not database.contains_car(spz):
        add_car(spz, model, rok)

    # todo fail adding order if car already in repair
    mechanic = None
    customer = session['username']

    add_user_order(mechanic, customer, spz, description)
    return redirect(url_for('user_orders'))


@app.route('/admin')
def admin():
    if '2' not in session['access']:
        abort(401)
    stats, orders = database.get_admin_stats()
    print("ORDERS_ADMIN" + str(orders))
    return render_template('admin/admin.html', username=session['username'], stats=stats, access=session['access'],
                           orders=orders)


@app.route("/user_orders")
def user_orders():
    if '0' not in session['access']:
        abort(401)
    orders = database.get_orders_customer(session['username'])
    return render_template('customer/user_orders.html', username=session['username'], access=session['access'],
                           orders=orders)


@app.route('/user_orders/<order_id>')
def user_order(order_id):
    if '0' not in session['access']:
        abort(401)

    current_order, parts, car = get_detailed_order(order_id)
    return render_template("customer/user_order.html", username=session['username'], access=session['access'],
                           order=current_order, parts=parts, car=car)


@app.route('/')
def landing_page():
    return render_template("landing_page.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/mechanic_orders/<order_id>')
def order(order_id):
    if ('1' not in session['access'] or database.get_order(order_id)['mechanic'] != session['username']) \
            and '2' not in session['access']:
        abort(401)
    current_order, parts, car = get_detailed_order(order_id)

    return render_template("mechanic/order.html", username=session['username'], access=session['access'],
                           order=current_order, parts=parts, car=car)


@app.route('/delete_part', methods=["POST"])
def delete_part():
    if '1' not in session['access'] and '2' not in session['access']:
        abort(401)
    order_id = request.form['order_id']
    database.delete_part(order_id, request.form['part_id'])
    return redirect(url_for("order", order_id=order_id))


@app.route('/add_part', methods=["POST"])
def add_part():
    print("ADD PART1")
    if '1' not in session['access'] and '2' not in session['access']:
        abort(401)

    order_id = request.form['order_id']
    name = request.form['name']
    price = request.form['price']
    is_part = request.form['is_part']

    print("ADD PART, order_id:" + str(order_id) + "name" + name + "price: " + str(price))
    add_orders_spare_part(name, price, order_id, is_part)

    return redirect(url_for("order", order_id=order_id))


@app.route("/add_<order_id>")
def add_order(order_id):
    if '1' not in session['access'] or database.get_order(order_id)['mechanic'] is not None:
        abort(401)
    database.assign_to_order(order_id, session['username'])
    return redirect('/all_orders')


# might need to chcek if user matches


@app.route("/technic")  # just try
def technic():
    return render_template("mechanic/technic.html")


@app.route("/kontakt")  # for "kotakt"
def contact():
    return render_template("kontakt.html")


@app.route("/onas")  # o nás
def onas():
    return render_template("onas.html")


if __name__ == '__main__':
    # todo add dialog boxes to confirm actions
    # todo text too big and not so good looking
    # todo better database creation and handling
    app.run(debug=True)
