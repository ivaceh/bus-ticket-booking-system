from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_mysqldb import MySQL
import os
import yaml

app = Flask(__name__)

# Load database configuration from a YAML file or directly set configuration
db = yaml.load(open('db.yaml'), Loader=yaml.FullLoader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('admin.html')

@app.route('/login')
def login():
    return render_template('admin-login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('admin-dashboard.html')

# app route create, delete, read, update

@app.route('/create')
def create():
    return render_template('create.html')
    
@app.route('/update')
def update():
    return render_template('update.html')

@app.route('/delete')
def delete():
    return render_template('delete.html')

@app.route('/login', methods=['POST'])
def login_post():
    if request.method == 'POST':
        login = request.form
        username = login['username']
        password = login['password']

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM user WHERE username = %s AND password = %s", (username, password))

        if result > 0:
            return render_template('admin-dashboard.html')
        else:
            return render_template('admin-login.html', message="Invalid Username or Password. Please try again.")
        
@app.route('/create', methods=['POST']) # Create booking has this input: Destination, Bus Name, Seats Available, Date.
def create_post():
    if request.method == 'POST':
        create = request.form
        destination = create['destination']
        bus_name = create['busID']
        seats_available = create['seats']
        date = create['travel_date']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO bookings(destination, busName, seats, travel_date) VALUES(%s, %s, %s, %s)", (destination, bus_name, seats_available, date))
        mysql.connection.commit()
        cur.close()
        
        if cur.rowcount > 0:
            return render_template('admin-dashboard.html', message="Bookings Successfully Created")
        else:
            return render_template('create.html', message="Failed to Create Bookings. Please try again.")
    
# update bookings
@app.route('/update', methods=['POST'])
def update_post():
    if request.method == 'POST':
        update_data = request.form
        booking_id = update_data['bookingID']
        destination = update_data['destination']
        bus_name = update_data['busID']
        seats_available = update_data['seats']
        date = update_data['travel_date']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE bookings SET destination=%s, busName=%s, seats=%s, travel_date=%s WHERE bookingID=%s", (destination, bus_name, seats_available, date, booking_id))
        mysql.connection.commit()
        cur.close()

        if cur.rowcount > 0:
            return render_template('admin-dashboard.html', message="Bookings Successfully Updated")
        else:
            return render_template('update.html', message="Failed to Update Bookings. Please try again.")
    
# delete bookings
@app.route('/delete', methods=['POST'])
def delete_post():
    if request.method == 'POST':
        delete_data = request.form
        booking_id = delete_data['bookingID']

        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM bookings WHERE bookingID=%s", (booking_id,))
        mysql.connection.commit()
        cur.close()

    if cur.rowcount > 0:
        return render_template('admin-dashboard.html', message="Booking Deleted Successfully")
    else:
        return render_template('delete.html', message="Failed to Delete Booking. Please try again.")
    
# read bookings using jsonify
@app.route('/read', methods=['GET'])
def read():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM bookings")
    result = cur.fetchall()
    return jsonify(result)

# Add a new route to serve as HTML page
@app.route('/bookings')
def index():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'read.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)