from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import os
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key


import stripe

stripe.api_key = 'sk_test_51QUEUK04UusKdRBhuvrjPYD9Gc64vpfSoSxCD94UF5xOChidJOQokfuWPWEsu9QaMZiZGLOWg5GXTVqZkDtn2LcS00RSAAcHu3'


UPLOAD_FOLDER = './static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ensure the uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    """
    Check if the file has a valid extension.
    """
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'xlsx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database connection function
def create_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Bismillah@786",  # Replace with your actual DB password
        database="landscaping_platform"
    )

# Route for Homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route for Signup Customer
@app.route('/signup-customer', methods=['GET', 'POST'])
def signup_customer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        phone = request.form['phone']
        address = request.form['address']
        zipcode = request.form['zipcode']

        try:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO customers (full_name, email, password, phone_number, address, zipcode) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, email, hashed_password, phone, address, zipcode)
            )
            connection.commit()
            cursor.close()
            connection.close()
            flash('Customer signed up successfully!', 'success')
            return redirect(url_for('signup_customer'))

        except Error as e:
            flash(f"Error: {str(e)}", 'danger')
            return redirect(url_for('signup_customer'))

    return render_template('signup-customer.html')

# Route for Signup Landscaper
@app.route('/signup-landscaper', methods=['GET', 'POST'])
def signup_landscaper():
    if request.method == 'POST':
        business_name = request.form['business_name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        phone = request.form['phone']
        services_offered = request.form['services']
        address = request.form['address']
        zipcode = request.form['zipcode']

        try:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO landscaperstable (business_name, email, password, phone_number, services_offered, address, zipcode) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (business_name, email, hashed_password, phone, services_offered, address, zipcode)
            )
            connection.commit()

            if cursor.rowcount > 0:
                flash('Landscaper signed up successfully!', 'success')

            cursor.close()
            connection.close()
            return redirect(url_for('signup_landscaper'))

        except Error as e:
            flash(f"Error: {str(e)}", 'danger')
            return redirect(url_for('signup_landscaper'))

    return render_template('signup-landscaper.html')

# Route for Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('username')
    password = data.get('password')
    user_type = data.get('user_type')

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        # Query for landscaper or customer based on user_type
        if user_type == 'landscaper':
            cursor.execute("SELECT * FROM landscaperstable WHERE email = %s", (email,))
        elif user_type == 'customer':
            cursor.execute("SELECT * FROM customers WHERE email = %s", (email,))
        else:
            return jsonify({'success': False, 'message': 'Invalid user type'}), 400

        user = cursor.fetchone()
        cursor.close()
        connection.close()

        # Check if user exists and password is correct
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            if user_type == 'landscaper':
                session['user'] = user['business_name']
                session['email'] = user['email']
                session['phone'] = user['phone_number']
                session['services_offered'] = user['services_offered']
            elif user_type == 'customer':
                session['user'] = user['full_name']
                session['email'] = user['email']
                session['phone'] = user['phone_number']
                session['address'] = user['address']

            session['user_type'] = user_type
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user = {
            'username': session.get('user'),
            'email': session.get('email'),
            'phone': session.get('phone'),
        }
        if session.get('user_type') == 'customer':
            user['address'] = session.get('address')
            return render_template('dashboard.html', user=user)  # Customer Dashboard
        else:
            user['business_name'] = session.get('business_name')
            user['services_offered'] = session.get('services_offered')
            return render_template('landscaper_dashboard.html', user=user)  # Landscaper Dashboard
    else:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('index'))

@app.route('/landscaper_dashboard', methods=['GET'])
def landscaper_dashboard():
    if 'user_id' not in session or session['user_type'] != 'landscaper':
        flash('Please log in as a landscaper to access the dashboard.', 'danger')
        return redirect(url_for('login'))

    landscaper_id = session['user_id']  # Logged-in landscaper's ID
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch pending connection requests for the logged-in landscaper
        cursor.execute("""
            SELECT 
                r.id AS request_id, 
                c.full_name AS customer_name, 
                c.email, 
                r.request_date 
            FROM requests r
            JOIN customers c ON r.customer_id = c.id
            WHERE r.landscaper_id = %s AND r.status = 'pending'
            ORDER BY r.request_date DESC
        """, (landscaper_id,))
        requests = cursor.fetchall()

        # Debugging: Print fetched requests to the terminal
        print(f"Pending Requests for Landscaper {landscaper_id}: {requests}")

        # Pass the fetched requests to the template
        return render_template('landscaper_dashboard.html', requests=requests)
    except Error as e:
        flash(f"Error fetching requests: {str(e)}", 'danger')
        return render_template('landscaper_dashboard.html', requests=[])
    finally:
        cursor.close()
        connection.close()

@app.route('/send_request', methods=['POST'])
def send_request():
    customer_id = session.get('user_id')  # Assuming user_id is stored in session
    landscaper_id = request.form.get('landscaper_id')
    
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO requests (customer_id, landscaper_id) VALUES (%s, %s)",
            (customer_id, landscaper_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        flash("Connection request sent!", "success")
        return redirect(url_for('search_landscapers'))
    except Error as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('search_landscapers'))

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if 'user_id' not in session:
        flash('Please log in to access messages.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_type = session['user_type']
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Fetch contacts
        if user_type == 'customer':
            cursor.execute("""
                SELECT l.id, l.business_name AS name
                FROM requests r
                JOIN landscaperstable l ON r.landscaper_id = l.id
                WHERE r.customer_id = %s AND r.status = 'accepted'
            """, (user_id,))
        elif user_type == 'landscaper':
            cursor.execute("""
                SELECT c.id, c.full_name AS name
                FROM requests r
                JOIN customers c ON r.customer_id = c.id
                WHERE r.landscaper_id = %s AND r.status = 'accepted'
            """, (user_id,))
        contacts = cursor.fetchall()

        # Fetch messages for the active contact
        active_contact_id = request.args.get('contact_id', type=int)
        active_contact = next((c for c in contacts if c['id'] == active_contact_id), None)

        messages = []
        if active_contact:
            cursor.execute("""
                SELECT sender_id, receiver_id, message AS text, user_type, filepath
                FROM chat
                WHERE (sender_id = %s AND receiver_id = %s)
                   OR (sender_id = %s AND receiver_id = %s)
                ORDER BY timestamp ASC
            """, (user_id, active_contact_id, active_contact_id, user_id))
            messages = cursor.fetchall()

        return render_template(
            'messages.html',
            contacts=contacts,
            active_contact=active_contact,
            messages=messages
        )
    except Error as e:
        flash(f"Error fetching messages: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))
    finally:
        cursor.close()
        connection.close()

@app.route('/send_message', methods=['POST'])
def send_message():
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash('Please log in to send messages.', 'danger')
        return redirect(url_for('login'))

    sender_id = session['user_id']  # Sender's ID from session
    sender_type = session.get('user_type')  # User type (customer or landscaper)

    if sender_type not in ['customer', 'landscaper']:
        flash('Invalid user type. Please log in again.', 'danger')
        return redirect(url_for('login'))

    # Debug: Print sender type
    print(f"Sender Type: {sender_type}")

    receiver_id = request.form.get('receiver_id')  # Receiver ID
    message = request.form.get('message')  # Message content
    file = request.files.get('file')  # File upload (optional)

    # Debug: Print receiver ID
    print(f"Receiver ID: {receiver_id}")

    filepath = None

    # Save file if uploaded
    # if file and allowed_file(file.filename):
    #     filename = secure_filename(file.filename)
    #     filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #     file.save(filepath)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename).replace("\\", "/")  # Ensure consistent forward slashes
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Save file to the static/uploads folder


    try:
        # Insert the message into the database
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO chat (sender_id, receiver_id, message, user_type, filepath)
                VALUES (%s, %s, %s, %s, %s)
            """, (sender_id, receiver_id, message, sender_type, filepath))
            connection.commit()

        flash('Message sent successfully.', 'success')
    except Error as e:
        flash(f"Error saving message: {str(e)}", 'danger')
    finally:
        if connection:
            connection.close()

    return redirect(url_for('messages', contact_id=receiver_id))



# Route to search projects
@app.route('/search_projects', methods=['GET', 'POST'])
def search_projects():
    projects = []
    zipcode = None
    if request.method == 'POST':
        zipcode = request.form['zipcode']  # Get the entered zip code
        try:
            connection = create_connection()
            with connection.cursor(dictionary=True) as cursor:
                query = '''
                    SELECT 
                        ProjectID, CustomerID, StartDate, EndDate, Status, zipcode 
                    FROM 
                        projects
                    WHERE 
                        zipcode = %s AND Status = 'Open';
                '''
                cursor.execute(query, (zipcode,))
                projects = cursor.fetchall()  # Fetch all matching projects
        except Error as e:
            flash(f"Error fetching projects: {str(e)}", "danger")
        finally:
            if connection:
                connection.close()
    return render_template('search_projects.html', projects=projects, zipcode=zipcode)



@app.route('/bid/<int:project_id>', methods=['POST'])
def place_bid(project_id):
    if 'user_id' not in session:
        flash('Please log in to place a bid.', 'danger')
        return redirect(url_for('login'))

    bid_amount = request.form['bid_amount']
    user_id = session['user_id']

    try:
        connection = create_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT Status FROM projects WHERE ProjectID = %s", (project_id,))
            project = cursor.fetchone()
            if not project or project['Status'] != 'Open':
                flash('Project is not available for bidding.', 'warning')
                return redirect(url_for('search_projects'))

            cursor.execute(
                "INSERT INTO bids (ProjectID, UserID, BidAmount) VALUES (%s, %s, %s)",
                (project_id, user_id, bid_amount),
            )
            connection.commit()
        flash('Your bid has been placed successfully!', 'success')
    except Error as e:
        flash(f"Error placing bid: {str(e)}", 'danger')
    finally:
        connection.close()

    return redirect(url_for('search_projects'))



@app.route('/connection_requests', methods=['POST'])
def connection_requests():
    if 'user_id' not in session or session.get('user_type') != 'customer':
        flash('You must be logged in as a customer to send a connection request.', 'danger')
        return redirect(url_for('index'))

    customer_id = session['user_id']
    landscaper_id = request.form.get('landscaper_id')  # Ensure this matches the form field name

    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Insert the connection request
        cursor.execute(
            "INSERT INTO requests (customer_id, landscaper_id, status) VALUES (%s, %s, 'pending')",
            (customer_id, landscaper_id)
        )
        connection.commit()
        cursor.close()
        connection.close()

        flash('Connection request sent successfully!', 'success')
        return redirect(url_for('search_landscapers'))

    except Error as e:
        flash(f"Error: {str(e)}", 'danger')
        return redirect(url_for('search_landscapers'))
    
@app.route('/update_request_status', methods=['POST'])
def update_request_status():
    if 'user_id' not in session or session['user_type'] != 'landscaper':
        flash('You must be logged in as a landscaper to update request status.', 'danger')
        return redirect(url_for('login'))

    request_id = request.form.get('request_id')
    action = request.form.get('action')  # 'accept' or 'reject'

    try:
        connection = create_connection()
        cursor = connection.cursor()
        if action == 'accept':
            cursor.execute("""
                UPDATE requests
                SET status = 'accepted'
                WHERE id = %s
            """, (request_id,))
            flash('Request accepted.', 'success')
        elif action == 'reject':
            cursor.execute("""
                UPDATE requests
                SET status = 'rejected'
                WHERE id = %s
            """, (request_id,))
            flash('Request rejected.', 'info')
        connection.commit()
    except Error as e:
        flash(f"Error updating request status: {str(e)}", 'danger')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('landscaper_dashboard'))

@app.route('/pending_requests', methods=['GET'])
def pending_requests():
    if 'user_id' not in session or session['user_type'] != 'landscaper':
        flash('Please log in as a landscaper to view pending requests.', 'danger')
        return redirect(url_for('login'))

    landscaper_id = session['user_id']
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch pending requests for the logged-in landscaper
        cursor.execute("""
            SELECT 
                r.id AS request_id, 
                c.full_name AS customer_name, 
                c.email, 
                r.request_date 
            FROM requests r
            JOIN customers c ON r.customer_id = c.id
            WHERE r.landscaper_id = %s AND r.status = 'pending'
            ORDER BY r.request_date DESC
        """, (landscaper_id,))
        requests = cursor.fetchall()

        return render_template('pending_requests.html', requests=requests)
    except Error as e:
        flash(f"Error fetching requests: {str(e)}", 'danger')
        return render_template('pending_requests.html', requests=[])
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Route for About Us Page
@app.route('/about')
def about():
    return render_template('about.html')

# Route for Contact Us Page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route for Services Page
@app.route('/services')
def services():
    return render_template('services.html')

# Route for Invoices Page
# Route for Invoices Page
@app.route('/invoices', methods=['GET', 'POST'])
def invoices():
    if 'user_id' not in session:
        flash('Please log in to view invoices.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_type = session['user_type']
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        if user_type == 'customer':
            # Fetch invoices assigned to this customer
            cursor.execute("""
                SELECT i.id, i.work_description, i.total_amount, i.status, i.logo, i.attachment,
                       l.business_name AS landscaper_name
                FROM invoices i
                JOIN landscaperstable l ON i.landscaper_id = l.id
                WHERE i.customer_id = %s
            """, (user_id,))
            invoices = cursor.fetchall()

            # Debugging: Check if invoices are fetched correctly
            print("Customer Invoices:", invoices)

            return render_template('invoices.html', invoices=invoices, customers=[])

        elif user_type == 'landscaper':
            # Fetch connected customers for the dropdown (customers with accepted requests)
            cursor.execute("""
                SELECT c.id, c.full_name
                FROM requests r
                JOIN customers c ON r.customer_id = c.id
                WHERE r.landscaper_id = %s AND r.status = 'accepted'
            """, (user_id,))
            customers = cursor.fetchall()

            # Fetch invoices issued by this landscaper
            cursor.execute("""
                SELECT i.id, i.work_description, i.total_amount, i.status, i.logo, i.attachment,
                       c.full_name AS customer_name
                FROM invoices i
                JOIN customers c ON i.customer_id = c.id
                WHERE i.landscaper_id = %s
            """, (user_id,))
            invoices = cursor.fetchall()

            # Debugging: Check if invoices are fetched correctly
            print("Landscaper Invoices:", invoices)
            print("Connected Customers:", customers)

            return render_template('invoices.html', invoices=invoices, customers=customers)

    except Error as e:
        flash(f"Error fetching invoices: {str(e)}", 'danger')
        return render_template('invoices.html', invoices=[], customers=[])
    finally:
        cursor.close()
        connection.close()


# Route for Invoices Page
@app.route('/help')
def help():
    return render_template('contact.html')

@app.route('/search_landscapers', methods=['GET', 'POST'])
def search_landscapers():
    landscapers = None
    pending_requests = []
    customer_id = session.get('user_id')  # Get logged-in customer's ID

    if request.method == 'POST':
        if 'landscaper_id' in request.form:
            landscaper_id = int(request.form['landscaper_id'])

            try:
                connection = create_connection()
                cursor = connection.cursor()

                # Check if a request already exists
                cursor.execute(
                    "SELECT id FROM requests WHERE customer_id = %s AND landscaper_id = %s",
                    (customer_id, landscaper_id),
                )
                existing_request = cursor.fetchone()

                if not existing_request:
                    # Insert a new request only if it doesn't exist
                    cursor.execute(
                        "INSERT INTO requests (customer_id, landscaper_id, status) VALUES (%s, %s, 'pending')",
                        (customer_id, landscaper_id),
                    )
                    connection.commit()

                cursor.close()
                connection.close()
            except Error as e:
                flash(f"Error: {str(e)}", "danger")

    # Fetch landscapers and pending requests based on ZIP code
    zip_code = request.form.get('zip_code') or request.args.get('zip_code')
    if zip_code:
        try:
            connection = create_connection()
            cursor = connection.cursor(dictionary=True)

            # Fetch landscapers based on ZIP code
            cursor.execute("SELECT * FROM landscaperstable WHERE zipcode = %s", (zip_code,))
            landscapers = cursor.fetchall()

            # Fetch pending requests for the logged-in customer
            cursor.execute(
                "SELECT landscaper_id FROM requests WHERE customer_id = %s AND status = 'pending'",
                (customer_id,),
            )
            pending_requests = [row['landscaper_id'] for row in cursor.fetchall()]

            cursor.close()
            connection.close()
        except Error as e:
            flash(f"Error: {str(e)}", "danger")

    return render_template(
        'search_landscapers.html',
        landscapers=landscapers,
        pending_requests=pending_requests,
        zipcode=zip_code,
    )




# Route for Logout
@app.route('/logout')
def logout():
    session.clear()  # Clears all session data
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))


@app.route('/create_invoice', methods=['POST'])
def create_invoice():
    if 'user_id' not in session or session['user_type'] != 'landscaper':
        flash('Only landscapers can create invoices.', 'danger')
        return redirect(url_for('invoices'))

    landscaper_id = session['user_id']
    customer_id = request.form['customer_id']
    work_description = request.form['work_description']
    total_amount = request.form['total_amount']
    logo = request.files.get('logo')
    attachment = request.files.get('attachment')

    logo_path = None
    attachment_path = None

    if logo:
        logo_filename = secure_filename(logo.filename)
        logo_path = os.path.join('uploads', logo_filename)
        logo.save(os.path.join(app.config['UPLOAD_FOLDER'], logo_filename))

    if attachment:
        attachment_filename = secure_filename(attachment.filename)
        attachment_path = os.path.join('uploads', attachment_filename)
        attachment.save(os.path.join(app.config['UPLOAD_FOLDER'], attachment_filename))

    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO invoices (landscaper_id, customer_id, work_description, logo, attachment, total_amount)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (landscaper_id, customer_id, work_description, logo_path, attachment_path, total_amount))
        connection.commit()
        flash('Invoice created successfully!', 'success')
    except Error as e:
        flash(f'Error creating invoice: {str(e)}', 'danger')
    finally:
        if connection:
            connection.close()

    return redirect(url_for('invoices'))

# @app.route('/update_invoice_status/<int:invoice_id>', methods=['POST'])
# def update_invoice_status(invoice_id):
#     action = request.form.get('action')
#     status = 'Approved' if action == 'approve' else 'Rejected'

#     try:
#         connection = create_connection()
#         cursor = connection.cursor()
#         cursor.execute("""
#             UPDATE invoices
#             SET status = %s
#             WHERE id = %s
#         """, (status, invoice_id))
#         connection.commit()
#         if action == 'approve':
#             flash('Invoice approved. Proceed to payment.', 'success')
#             return redirect(url_for('pay_invoice', invoice_id=invoice_id))
#         else:
#             flash('Invoice rejected.', 'info')
#             return redirect(url_for('invoices'))
#     except Error as e:
#         flash(f'Error updating invoice: {str(e)}', 'danger')
#         return redirect(url_for('invoices'))
#     finally:
#         cursor.close()
#         connection.close()

@app.route('/pay_invoice/<int:invoice_id>', methods=['GET', 'POST'])
def pay_invoice(invoice_id):
    if request.method == 'GET':
        # Fetch invoice details for the payment page
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT i.id, i.total_amount, i.work_description, l.business_name
                FROM invoices i
                JOIN landscaperstable l ON i.landscaper_id = l.id
                WHERE i.id = %s
            """, (invoice_id,))
            invoice = cursor.fetchone()
            if not invoice:
                flash('Invoice not found.', 'danger')
                return redirect(url_for('invoices'))
            return render_template('pay_invoice.html', invoice=invoice)
        except Error as e:
            flash(f"Error fetching invoice: {str(e)}", 'danger')
            return redirect(url_for('invoices'))
        finally:
            cursor.close()
            connection.close()

    if request.method == 'POST':
        # Process the payment
        flash('Payment processed successfully!', 'success')
        return redirect(url_for('invoices'))



@app.route('/update_invoice_status/<int:invoice_id>', methods=['POST'])
def update_invoice_status(invoice_id):
    action = request.form.get('action')
    status = 'Approved' if action == 'approve' else 'Rejected'

    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE invoices
            SET status = %s
            WHERE id = %s
        """, (status, invoice_id))
        connection.commit()

        if action == 'approve':
            flash('Invoice approved. Proceed to payment.', 'success')
            return redirect(url_for('pay_invoice', invoice_id=invoice_id))
        else:
            flash('Invoice rejected.', 'info')
            return redirect(url_for('invoices'))
    except Error as e:
        flash(f'Error updating invoice: {str(e)}', 'danger')
        return redirect(url_for('invoices'))
    finally:
        cursor.close()
        connection.close()



# Run the application
if __name__ == '__main__':
    app.run(debug=True)
