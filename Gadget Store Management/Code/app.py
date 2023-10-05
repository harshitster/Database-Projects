import psycopg2 as pg2
from flask import Flask, render_template, request, redirect
import datetime

app = Flask(__name__)

DATABASE = 'Project'
USER = 'postgres'
PASSWORD = 'Xbox1xfifa19@postgres'

DATA = {}

def get_cursor():
    conn = pg2.connect(database=DATABASE, user=USER, password=PASSWORD)
    cur = conn.cursor()
    return conn, cur

def close_connection(conn):
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        login_username = request.form.get('username')
        login_password = request.form.get('password')

        try:
            conn, cur = get_cursor()
            cur.execute("SELECT login_username FROM users")

            usernames = cur.fetchall()
            flag0 = 0
            for username in usernames:
                if login_username == username[0]:
                    flag0 = 1
                    break
            
            if flag0 == 0:
                #TODO
                close_connection(conn)
                return render_template('index.html')
            else:
                cur.execute("SELECT login_password FROM users WHERE login_username = '{}'".format(login_username))
                password = cur.fetchall()[0][0]
                close_connection(conn)

                if password != login_password:
                    #TODO
                    return render_template('index.html')
                else:
                    DATA['user'] = login_username
                    return render_template('options.html', username=login_username)
        except:
            close_connection(conn)
            return redirect('/')


@app.route('/options', methods=['GET', 'POST'])
def options():
    if request.method == 'GET':
        return render_template('options.html', username=DATA['user'])
    elif request.method == 'POST':
        return redirect('/options')


@app.route('/validate_customer', methods=['GET', 'POST'])
def validate_customers():
    if request.method == 'GET':
        return render_template('validate_customer.html', username=DATA['user'])
    elif request.method == 'POST':
        cus_email = request.form.get('cus_email')

        try:
            conn, cur = get_cursor()
            cur.execute("SELECT * FROM customer WHERE cus_email = '{}'".format(cus_email))
            customer = cur.fetchall()[0]

            if not customer:
                close_connection(conn)
                return redirect('/validate')
            else:
                DATA['customer'] = customer
                close_connection(conn)
                return redirect('/bill')
        except:
            close_connection(conn)
            return redirect('/validate_customer')
        

@app.route('/create_customer', methods = ['GET', 'POST'])
def create_customer():
    if request.method == 'GET':
        return render_template('create_customer.html', username=DATA['user'])
    elif request.method == 'POST':
        cus_name = request.form.get('cus_name')
        cus_email = request.form.get('cus_email')
        cus_phone = request.form.get('cus_phone')
        cus_add = request.form.get('cus_add')
        cus_dob = request.form.get('cus_dob')

        try:
            conn, cur = get_cursor()
            postgres_insert_query = """ INSERT INTO customer(cus_email, cus_name, cus_phone, cus_add, cus_dob) VALUES (%s, %s, %s, %s, %s)"""
            values = (cus_email, cus_name, cus_phone, cus_add, cus_dob)
            cur.execute(postgres_insert_query, values)
            conn.commit()

            cur.execute("SELECT * FROM customer WHERE cus_email = '{}'".format(cus_email))
            customer = cur.fetchall()[0]

            DATA['customer'] = customer
            
            close_connection(conn)
            return redirect('/bill')
        except:
            close_connection(conn)
            return redirect('/create_customer')


@app.route('/update_customer', methods=['GET', 'POST'])
def update_customer():
    if request.method == 'GET':
        return render_template('update_customer.html', username=DATA['user'])
    elif request.method == 'POST':
        cus_email = request.form.get('cus_email')
        return redirect("/update_customer_details?email={}".format(cus_email))


@app.route('/update_customer_details', methods=['GET', 'POST'])
def update_customer_details():
    if request.method == 'GET':
        try:
            conn, cur = get_cursor()

            cur.execute("SELECT * FROM customer WHERE cus_email = '{}'".format(request.args.get('email')))
            customer_details = cur.fetchall()[0]

            cus_email = customer_details[0]
            cus_name = customer_details[1]
            cus_phone = customer_details[2]
            cus_add = customer_details[3]
            cus_dob = customer_details[4]

            close_connection(conn)
            return render_template('update_customer_details.html', 
                                    cus_email=cus_email, 
                                    cus_name=cus_name,
                                    cus_phone=cus_phone,
                                    cus_add=cus_add,
                                    cus_dob=cus_dob,
                                    username=DATA['user'])
        except:
            close_connection(conn)
            return render_template('update_customer.html')
    elif request.method == 'POST':
        cus_name = request.form.get('cus_name')
        cus_email = request.form.get('cus_email')
        cus_phone = request.form.get('cus_phone')
        cus_add = request.form.get('cus_add')
        cus_dob = request.form.get('cus_dob')

        try:
            conn, cur = get_cursor()
            postgres_update_query = """ UPDATE customer
                                    SET cus_name = %s,
                                    cus_phone = %s,
                                    cus_add = %s,
                                    cus_dob = %s
                                    WHERE cus_email = %s"""
            cur.execute(postgres_update_query, (cus_name, cus_phone, cus_add, cus_dob, cus_email))
            conn.commit()

            cur.execute("SELECT * FROM customer WHERE cus_email = '{}'".format(cus_email))
            customer = cur.fetchall()[0]

            DATA['customer'] = customer
            
            close_connection(conn)
            return redirect('/bill')     
        except:
            close_connection(conn)
            return render_template('update_customer.html')


@app.route('/delete_customer', methods=['GET', 'POST'])
def delete_customer():
    if request.method == 'GET':
        return render_template('delete_customer.html', username=DATA['user'])
    elif request.method == 'POST':
        cus_email = request.form.get('cus_email')

        try:
            conn, cur = get_cursor()
            cur.execute("DELETE FROM customer WHERE cus_email = '{}'".format(cus_email))
            conn.commit()

            close_connection(conn)
            return render_template('options.html', username=DATA['user'])
        except:
            close_connection(conn)
            return redirect('/delete_customer')


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'GET':
        return render_template('add_product.html', username=DATA['user'])
    elif request.method == 'POST':
        prod_type = request.form.get('prod_type')
        prod_name = request.form.get('prod_name')
        prod_storage = request.form.get('prod_storage')
        prod_price = request.form.get('prod_price')

        try:
            conn, cur = get_cursor()
            cur.execute("SELECT * FROM product WHERE prod_type = '{}' AND prod_name = '{}' AND prod_storage = '{}' AND prod_price = '{}'".format(prod_type, prod_name, prod_storage, prod_price))
            product = cur.fetchall()

            if product:
                close_connection(conn)
                return render_template('options.html', username=DATA['user'])
            
            postgres_insert_query = """ INSERT INTO product(prod_type, prod_name, prod_storage, prod_price) VALUES (%s, %s, %s, %s)"""
            values = (prod_type, prod_name, prod_storage, prod_price)
            cur.execute(postgres_insert_query, values)
            conn.commit()

            close_connection(conn)
            return render_template('options.html', username=DATA['user'])
        except:
            close_connection(conn)
            return redirect('/add_product')


@app.route('/delete_product', methods=['GET', 'POST'])
def delete_product():
    if request.method == 'GET':
        try:
            conn, cur = get_cursor()
            cur.execute("SELECT DISTINCT(prod_type) FROM product")
            pt_data = cur.fetchall()
            product_types = []

            for product_type in pt_data:
                product_types.append(product_type[0])

            close_connection(conn)
            return render_template('delete_product.html', product_types=product_types, username=DATA['user'])
        except:
            close_connection(conn)
            return redirect('/delete_product')
    elif request.method == 'POST':
        prod_type = request.form.get('prod_type')
        print(prod_type)
        return redirect('/delete_product_type?product_type={}'.format(prod_type))


@app.route('/delete_product_type', methods=['GET', 'POST'])
def delete_product_type():
    if request.method == 'GET':
        prod_type = request.args.get('product_type')

        try:
            conn, cur = get_cursor()
            cur.execute("SELECT * FROM product WHERE prod_type = '{}'".format(prod_type))
            products = cur.fetchall()

            close_connection(conn)
            return render_template('delete_product_type.html', products=products, username=DATA['user'])
        except:
            close_connection(conn)
            return redirect('/delete_product')
    elif request.method == 'POST':
        prod_id = request.form.get('prod_id')

        try:
            conn, cur = get_cursor()
            cur.execute("DELETE FROM product WHERE prod_id = {}".format(prod_id))
            conn.commit()

            close_connection(conn)
            return render_template('options.html', username=DATA['user'])
        except:
            close_connection(conn)
            return redirect('/delete_product')


@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'GET':
        try:
            conn, cur = get_cursor()
            cur.execute("SELECT DISTINCT(prod_type) FROM product")
            pt_data = cur.fetchall()

            product_types = []
            for product_type in pt_data:
                product_types.append(product_type[0])
                
            close_connection(conn)
            return render_template('products.html', product_types=product_types, username=DATA['user'])
        except:
            close_connection(conn)
            return redirect('/products')
    elif request.method == 'POST':
        prod_type = request.form.get('prod_type')
        return redirect('/product_type_list?product_type={}'.format(prod_type))


@app.route('/product_type_list', methods=['GET'])
def product_type_list():
    if request.method == 'GET':
        prod_type = request.args.get('product_type')
        
        try:
            conn, cur = get_cursor()
            cur.execute("SELECT prod_name, prod_storage, prod_price FROM product WHERE prod_type='{}'".format(prod_type))
            products = cur.fetchall()

            close_connection(conn)
            return render_template('product_type_list.html', products=products)
        except:
            close_connection(conn)
            return redirect('/products')


@app.route('/bill', methods=['GET', 'POST'])
def billing():
    if request.method == 'GET':
        try:
            conn, cur = get_cursor()
            cur.execute("SELECT DISTINCT(prod_type) FROM product")
            pt_data = cur.fetchall()

            product_types = []
            for product_type in pt_data:
                product_types.append(product_type[0])
                
            close_connection(conn)
            return render_template('bill_product_type.html', product_types=product_types, username=DATA['user'])
        except:
            close_connection(conn)
            return redirect('/bill')
    elif request.method == 'POST':
        prod_type = request.form.get('prod_type')
        return redirect('/bill_product_list?prod_type={}'.format(prod_type))


@app.route('/bill_product_list', methods=['GET', 'POST'])
def bill_product_list():
    if request.method == 'GET':
        prod_type = request.args.get('prod_type')
        
        try:
            conn, cur = get_cursor()
            cur.execute("SELECT prod_id, prod_name, prod_storage, prod_price FROM product WHERE prod_type='{}'".format(prod_type))
            products = cur.fetchall()

            close_connection(conn)
            return render_template('bill_product.html', products=products, username=DATA['user'])
        except:
            close_connection(conn)
            return redirect('/bill')
    elif request.method == 'POST':
        prod_id = request.form.get('prod_id')

        if 'prods_cart' not in DATA:
            DATA['prods_cart'] = [prod_id]
        else:
            DATA['prods_cart'].append(prod_id)

        return render_template('pen_bill.html', username=DATA['user'])


@app.route('/bill_final', methods=['GET', 'POST'])
def bill_final():
    if request.method == 'GET':
        product_list = DATA['prods_cart']
        
        try:
            conn, cur = get_cursor()
            postgres_select_query = 'SELECT prod_type, prod_name, prod_storage, prod_price FROM product WHERE prod_id IN %(product_list)s'
            cur.execute(postgres_select_query, { 'product_list': tuple(product_list) })
            products = cur.fetchall()

            total_amount = 0
            for product in products:
                amount = product[-1]
                amount = int(amount[1::])
                total_amount += amount
            
            total_amount = '$' + str(total_amount)

            close_connection(conn)
            return render_template('show_cart.html', products=products, total_amount=total_amount, username=DATA['user'])
        except:
            close_connection(conn)
            return redirect('/bill')
    elif request.method == 'POST':
        bill_payment = request.form.get('payment_mode')
        ct = datetime.datetime.now()
        bill_id = str(int(ct.timestamp()))
        cus_email = DATA['customer'][0]
        prod_ids = DATA['prods_cart']
        username = DATA['user']

        try:
            conn, cur = get_cursor()
            cur.execute("INSERT INTO bill(bill_id, bill_date, cus_email, payment_mode) VALUES ('{}', CURRENT_DATE, '{}', '{}')".format(bill_id, cus_email, bill_payment))
            conn.commit()

            for prod_id in prod_ids:
                cur.execute("INSERT INTO purchase(cus_email, bill_id, prod_id, username) VALUES('{}', '{}', {}, '{}')".format(cus_email, bill_id, prod_id, username))
                conn.commit()

            del DATA['customer']
            del DATA['prods_cart']

            close_connection(conn)
            return render_template('options.html', username=username)
        except:
            close_connection(conn)
            return render_template('options.html', username=username)

@app.route('/query', methods=['POST'])
def query():
    if request.method == 'POST':
        query = request.form.get('query')
        DATA['query'] = query
        return redirect('/query_result')


@app.route('/query_result', methods=['GET', 'POST'])
def query_result():
    if request.method == 'GET':
        try:
            conn, cur = get_cursor()
            query = DATA['query']
            cur.execute(query)
            
            query_result = cur.fetchall()
            close_connection(conn)
            print(query_result)
            return render_template('query_result.html', query_results=query_result, username=DATA['user'])
        except:
            close_connection(conn)
            return redirect('/options')
    elif request.method == 'POST':
        del DATA['user']
        return redirect('/options')
