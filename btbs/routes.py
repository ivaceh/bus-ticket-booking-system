from btbs import app, db, bcrypt, limiter, logger
from flask import redirect, render_template, url_for, session, flash, request
from markupsafe import escape
from btbs.models import User, Bus, Booking, Destination
from btbs.forms import LoginForm, RegisterForm, createUserForm, bookBusTicketForm, createBusForm, createDestinationForm
import pymysql
from datetime import datetime
import sqlalchemy
from btbs import db
from btbs import app, bcrypt, limiter, logger

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

# login post
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            username = escape(form.username.data.strip())
            password = escape(form.password.data.strip())
            user = User.query.filter_by(username=username).first()
            assert user is not None, "User should exist in the database"
            if user and bcrypt.check_password_hash(user.password, password):
                session['logged_in'] = True
                session['username'] = username
                session['balance'] = user.balance
                session['is_admin'] = user.is_admin
                if not user.is_admin:
                    session['isnot_admin'] = True
                else:
                    session.pop('isnot_admin', None)
                logger.info(f"User {username} logged in successfully.", 'success')
                if user.is_admin:
                    return redirect('/admin-main')
                else:
                    return redirect('/user-main')
            else:
                logger.warning(f"Failed login attempt for username: {username}")
                flash('Invalid username or password', 'danger')
                return redirect(url_for('login_page'))
        except pymysql.MySQLError as e:
            app.logger.error(f"MySQL error during login: {e}")
            flash('A database error occurred during login. Please try again.', 'danger')
        except Exception as e:
            app.logger.error(f"Error during login: {e}")
            flash('An error occurred during login. Please try again.', 'danger')
        finally:
            db.session.close()
    elif form.is_submitted():
        flash('Form validation failed. Please check your inputs.', 'danger')
    return render_template('login.html', form=form)

# logout
@app.route('/logout')
def logout():
    username = session.get('username')
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('balance', None)
    session.pop('is_admin', None)
    logger.info(f"User {username} logged out successfully.")
    flash('Logged out successfully', 'success')
    return redirect(url_for('home_page'))

# register page
@app.route('/register-page')
def register_page():
    form = RegisterForm()
    return render_template('register.html', form=form)

# register post
@app.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            username = escape(form.username.data.strip())
            email = escape(form.email.data.strip())
            password = bcrypt.generate_password_hash(escape(form.password.data.strip())).decode('utf-8')
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            assert user.id is not None, "User ID should be assigned after commit"
            logger.info(f"New user registered: {username}")
            flash('Account created successfully. Please login.', 'success')
            return redirect(url_for('login_page'))
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            app.logger.error(f"Integrity error during registration: {e}")
            flash('A database error occurred during registration. Please try again.', 'error')
        except Exception as e:
            app.logger.error(f"Error during registration: {e}")
            flash('An error occurred during registration. Please try again.', 'danger')
        finally:
            db.session.close()
    else:
        flash('Form validation failed. Please check your inputs.')
    return render_template('register.html', form=form)

@app.route('/admin-main')
def admin_main():
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    return render_template('admin_main.html')


@app.route('/user-main')
def user_main():
    if not session.get('logged_in') or session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    return render_template('user_main.html')

# --------------------- Database CRUD operation for User table | Header ---------------------

@app.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    user = User.query.get_or_404(user_id)
    assert user is not None, "User should exist in the database"
    if request.method == 'POST':
        try:
            user.username = escape(request.form['username'].strip())
            user.email = escape(request.form['email'].strip())
            user.is_admin = 'is_admin' in request.form
            db.session.commit()
            logger.info(f"User {user.username} updated successfully.")
            flash('User updated successfully.', 'success')
            return redirect(url_for('view_users'))
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            app.logger.error(f"Integrity error during user update: {e}")
            flash('A database error occurred during user update. Please try again.', 'danger')
        except Exception as e:
            app.logger.error(f"Error during user update: {e}")
            flash('An error occurred during user update. Please try again.', 'danger')
        finally:
            db.session.close()
    return render_template('user/edit_user.html', user=user)

@app.route('/delete-user/<int:user_id>')
def delete_user(user_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        logger.info(f"User {user.username} deleted successfully.")
        flash('User deleted successfully.', 'success')
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        flash('Cannot delete user as they have active bookings. Deleting them would damage our reputation.', 'danger')
    return redirect(url_for('view_users'))

@app.route('/view-users')
def view_users():
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    users = User.query.all()
    return render_template('user/view_users.html', users=users)

@app.route('/create-user', methods=['GET', 'POST'])
def create_user():
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    
    form = createUserForm()
    if form.validate_on_submit():
        username = escape(form.username.data.strip())
        email = escape(form.email.data.strip())
        password = bcrypt.generate_password_hash(escape(form.password.data.strip())).decode('utf-8')
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"New user created: {username}")
        flash('New user created successfully.', 'success')
        return redirect(url_for('view_users'))
    
    return render_template('user/create_user.html', form=form)

# --------------------- Database CRUD operation for User table | Footer ---------------------

# --------------------- Database CRUD operation for Bus table | Header ---------------------

@app.route('/view-buses')
def view_buses():
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    buses = Bus.query.all()
    return render_template('bus/view_bus.html', buses=buses)

# edit bus
@app.route('/edit-bus/<int:bus_id>', methods=['GET', 'POST'])
def edit_bus(bus_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    bus = Bus.query.get_or_404(bus_id)
    assert bus is not None, "Bus should exist in the database"
    if request.method == 'POST':
        try:
            bus.name = escape(request.form['busName'].strip())
            bus.capacity = escape(request.form['capacity'].strip())
            db.session.commit()
            logger.info(f"Bus {bus.name} updated successfully.")
            flash('Bus updated successfully.', 'success')
            return redirect(url_for('view_buses'))
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            app.logger.error(f"Integrity error during bus update: {e}")
            flash('A database error occurred during bus update. Please try again.', 'danger')
        except Exception as e:
            app.logger.error(f"Error during bus update: {e}")
            flash('An error occurred during bus update. Please try again.', 'danger')
        finally:
            db.session.close()
    return render_template('bus/edit_bus.html', bus=bus)

# delete bus
@app.route('/delete-bus/<int:bus_id>')
def delete_bus(bus_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    bus = Bus.query.get_or_404(bus_id)
    try:
        db.session.delete(bus)
        db.session.commit()
        logger.info(f"Bus {bus.name} deleted successfully.")
        flash('Bus deleted successfully.', 'success')
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        flash('Cannot delete bus as it is currently in use in bookings. Deleting it would harm customers.', 'danger')
    return redirect(url_for('view_buses'))

@app.route('/add-bus', methods=['GET', 'POST'])
def add_bus():
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    form = createBusForm()
    if form.validate_on_submit():
        name = escape(form.name.data)
        capacity = escape(form.capacity.data)
        new_bus = Bus(name=name, capacity=capacity)
        db.session.add(new_bus)
        db.session.commit()
        logger.info(f"New bus added: {name}")
        flash('New bus added successfully.', 'success')
        return redirect(url_for('view_buses'))
    return render_template('bus/add_bus.html', form=form)

# --------------------- Database CRUD operation for Bus table | Footer ---------------------
#
#
# --------------------- Database CRUD operations for Destination Table ---------------------

@app.route('/view-destinations')
def view_destinations():
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    destinations = Destination.query.all()
    return render_template('destination/view_destination.html', destinations=destinations)

@app.route('/edit-destination/<int:destination_id>', methods=['GET', 'POST'])
def edit_destination(destination_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    destination = Destination.query.get_or_404(destination_id)
    assert destination is not None, "Destination should exist in the database"
    if request.method == 'POST':
        try:
            destination.name = escape(request.form['destinationName'].strip())
            destination.price = escape(request.form['price'].strip())
            destination.distance = escape(request.form['distance'].strip())
            db.session.commit()
            logger.info(f"Destination {destination.name} updated successfully.")
            flash('Destination updated successfully.', 'success')
            return redirect(url_for('view_destinations'))
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            app.logger.error(f"Integrity error during destination update: {e}")
            flash('A database error occurred during destination update. Please try again.', 'danger')
        except Exception as e:
            app.logger.error(f"Error during destination update: {e}")
            flash('An error occurred during destination update. Please try again.', 'danger')
        finally:
            db.session.close()
    return render_template('destination/edit_destination.html', destination=destination)

@app.route('/delete-destination/<int:destination_id>')
def delete_destination(destination_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.')
        return redirect(url_for('login_page'))
    destination = Destination.query.get_or_404(destination_id)
    try:
        db.session.delete(destination)
        db.session.commit()
        logger.info(f"Destination {destination.name} deleted successfully.")
        flash('Destination deleted successfully.', 'success')
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        flash('Cannot delete destination as it is currently in use in bookings. Deleting it would harm customers.', 'danger')
    return redirect(url_for('view_destinations'))

@app.route('/add-destination', methods=['GET', 'POST'])
def add_destination():
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.')
        return redirect(url_for('login_page'))
    form = createDestinationForm()
    if form.validate_on_submit():
        name = escape(form.name.data)
        price = escape(form.price.data)
        distance = escape(form.distance.data)
        new_destination = Destination(name=name, price=price, distance=distance)
        db.session.add(new_destination)
        db.session.commit()
        logger.info(f"New destination added: {name}")
        flash('New destination added successfully.', 'success')
        return redirect(url_for('view_destinations'))
    return render_template('destination/add_destination.html', form=form)
# --------------------- Database CRUD operations for Destination Table -->END ---------------------
#

# --------------------- Database CRUD operations for Booking Table --------------------

@app.route('/view-bookings')
def view_bookings():
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    bookings = Booking.query.all()
    return render_template('booking/view_bookedUsers.html', bookings=bookings)

@app.route('/edit-booking/<int:booking_id>', methods=['GET', 'POST'])
def edit_booking(booking_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    booking = Booking.query.get_or_404(booking_id)
    if request.method == 'POST':
        try:
            booking.bus_id = escape(request.form['bus_id'])
            booking.destination_id = escape(request.form['destination_id'])
            booking.travel_date = datetime.strptime(escape(request.form['travel_date']), '%Y-%m-%d')
            db.session.commit()
            logger.info(f"Booking {booking.booking_id} updated successfully.")
            flash('Booking updated successfully.', 'success')
            return redirect(url_for('view_bookings'))
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            app.logger.error(f"Integrity error during booking update: {e}")
            flash('A database error occurred during booking update. Please try again.', 'error')
        except Exception as e:
            app.logger.error(f"Error during booking update: {e}")
            flash('An error occurred during booking update. Please try again.', 'error')
        finally:
            db.session.close()
    return render_template('booking/edit_bookedUsers.html', booking=booking)

@app.route('/delete-booking/<int:booking_id>')
def delete_booking(booking_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    logger.info(f"Booking {booking.booking_id} deleted successfully.")
    flash('Booking deleted successfully.', 'success')
    return redirect(url_for('view_bookings'))

# --------------------- Database CRUD operations for Booking Table -->END --------------------

#
# --------------------- Routes where regular user booked their ticket or cancel them ---------------------
@app.route('/bookTicketForm', methods=['GET', 'POST'])
def bookTicketForm():
    if not session.get('logged_in'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    form = bookBusTicketForm()
    destinations = Destination.query.all()
    buses = Bus.query.all()
    if form.validate_on_submit():
        return redirect(url_for('book_ticket'))
    return render_template('booking/booking.html', form=form, destinations=destinations, buses=buses)

@app.route('/bookTicket', methods=['POST'])
def book_ticket():
    if not session.get('logged_in'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    form = bookBusTicketForm()
    if form.validate_on_submit():
        username = session.get('username')
        if not username:
            flash('You must be logged in to book a ticket.')
            return redirect(url_for('login_page'))
        
        user = User.query.filter_by(username=username).first()
        assert user is not None, "User should exist in the database"
        if not user:
            flash('User not found.')
            return redirect(url_for('login_page'))

        bus_id = form.bus_id.data
        destination_id = form.destination_id.data
        travel_date = form.travel_date.data
        booking_date = datetime.now()

        new_booking = Booking(
            user_id=user.id,
            bus_id=bus_id,
            destination_id=destination_id,
            travel_date=travel_date,
            booking_date=booking_date
        )
        try:
            db.session.add(new_booking)
            db.session.commit()
            assert new_booking.booking_id is not None, "Booking ID should be assigned after commit"
            logger.info(f"New booking created: {new_booking.booking_id}")
            flash('Ticket booked successfully.', 'success')
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            app.logger.error(f"Integrity error during booking: {e}")
            flash('A database error occurred during booking. Please try again.', 'error')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error during booking: {e}")
            flash(f'Error booking ticket: {e}')
        finally:
            db.session.close()
        return redirect(url_for('my_tickets'))
    destinations = Destination.query.all()
    buses = Bus.query.all()
    return render_template('booking/booking.html', form=form, destinations=destinations, buses=buses)

@app.route('/MyTickets')
def my_tickets():
    if not session.get('logged_in'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    username = session.get('username')
    if not username:
        flash('You must be logged in to view your tickets.')
        return redirect(url_for('login_page'))
    
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found.')
        return redirect(url_for('login_page'))
    
    bookings = db.session.query(Booking, Bus, Destination).join(Bus, Booking.bus_id == Bus.id).join(Destination, Booking.destination_id == Destination.id).filter(Booking.user_id == user.id).all()
    return render_template('booking/MyTicket.html', bookings=bookings)

@app.route('/cancel-booking/<int:booking_id>', methods=['GET', 'POST'])
def cancel_booking(booking_id):
    if not session.get('logged_in'):
        flash('Access denied.', 'danger')
        return redirect(url_for('login_page'))
    username = session.get('username')
    if not username:
        flash('You must be logged in to cancel a booking.')
        return redirect(url_for('login_page'))
        
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found.')
        return redirect(url_for('login_page'))
        
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != user.id:
        flash('You are not authorized to cancel this booking.')
        return redirect(url_for('my_tickets'))
    
    try:
        db.session.delete(booking)
        db.session.commit()
        logger.info(f"Booking {booking.booking_id} cancelled successfully.")
        flash('Booking cancelled successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error cancelling booking: {e}')
    finally:
        db.session.close()
    
    return redirect(url_for('my_tickets'))