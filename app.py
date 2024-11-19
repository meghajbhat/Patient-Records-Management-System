from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secret key for your app

# MySQL database connection
def create_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='admin_user',  # Update with your database username
            password='admin_pass',  # Update with your database password
            database='HospitalDB'  # Ensure the database is 'HospitalDB'
        )
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Signup route for doctors and patients
@app.route('/signup/<user_type>', methods=['GET', 'POST'])
def signup(user_type):
    if request.method == 'POST':
        connection = create_connection()
        if connection:
            password = generate_password_hash(request.form['password'])
            if user_type == 'doctors':
                cur = connection.cursor()
                cur.execute(
                    "INSERT INTO doctors (name, phone_no, email, job_title, degree, year, employer, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        request.form['name'], request.form['phone_no'], request.form['email'],
                        request.form['job_title'], request.form['degree'], request.form['year'],
                        request.form['employer'], password
                    )
                )
                connection.commit()
                cur.close()
                flash('Doctor registered successfully!')
            elif user_type == 'patients':
                cur = connection.cursor()
                cur.execute(
                    "INSERT INTO Patient (name, dob, symptoms, phone_no, blood_group, insurance, email, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        request.form['name'], request.form['dob'], request.form['symptoms'],
                        request.form['phone_no'], request.form['blood_group'], request.form['insurance'],
                        request.form['email'], password
                    )
                )
                connection.commit()
                cur.close()
                flash('Patient registered successfully!')
            connection.close()
        else:
            flash('Database connection failed.')
        return redirect(url_for('index'))
    return render_template(f'{user_type}_signup.html')

# Login route for doctors and patients
@app.route('/login/<user_type>', methods=['GET', 'POST'])
def login(user_type):
    if request.method == 'POST':
        connection = create_connection()
        if connection:
            email = request.form['email']
            password = request.form['password']
            user = None
            
            # Check user type and fetch appropriate data
            if user_type == 'doctors':
                cur = connection.cursor(dictionary=True)
                cur.execute("SELECT * FROM doctors WHERE email = %s", (email,))
                user = cur.fetchone()  # Fetch the doctor record
                cur.close()
            elif user_type == 'patients':
                cur = connection.cursor(dictionary=True)
                cur.execute("SELECT * FROM Patient WHERE email = %s", (email,))
                user = cur.fetchone()  # Fetch the patient record
                cur.close()

            # Verify user and password
            if user and check_password_hash(user['password'], password):
                session['user'] = user  # Save user details in the session
                session['user']['user_type'] = user_type  # Add user_type to the session
                flash('Logged in successfully!', 'success')
                
                # Redirect based on user type
                if user_type == 'patients':
                    return redirect(url_for('patients_welcome'))  # Patient welcome page
                elif user_type == 'doctors':
                    return redirect(url_for('doctors_welcome'))  # Doctor welcome page

            else:
                flash('Invalid credentials.', 'danger')
            connection.close()
        else:
            flash('Database connection failed.', 'danger')
    return render_template(f'{user_type}_login.html')  # Dynamically render the correct login page





# Welcome page for doctors
@app.route('/doctors_welcome')
def doctors_welcome():
    if 'user' not in session or session['user']['user_type'] != 'doctors':
        return redirect(url_for('index'))

    doctor_id = session['user']['D_ID']
    connection = create_connection()
    appointments = []
    bills = []

    if connection:
        try:
            cur = connection.cursor(dictionary=True)
            
            # Fetch appointments for the logged-in doctor
            cur.execute("""
                SELECT a.A_ID, a.time, a.status, a.notes, p.name AS patient_name
                FROM Appointment a
                JOIN Patient p ON a.P_ID = p.P_ID
                WHERE a.D_ID = %s
            """, (doctor_id,))
            appointments = cur.fetchall()

            # Fetch bills linked to the doctor's appointments
            cur.execute("""
                SELECT b.B_ID, b.date, b.amount, b.payment_status, a.A_ID
                FROM Bill b
                JOIN Appointment a ON b.B_ID = a.A_ID
                WHERE a.D_ID = %s
            """, (doctor_id,))
            bills = cur.fetchall()

            cur.close()
        except Exception as e:
            flash(f"Error fetching data: {e}", 'danger')
        finally:
            connection.close()

    return render_template('doctors_welcome.html', appointments=appointments, bills=bills, user=session['user'])



# Welcome page for patients
@app.route('/patients_welcome')
def patients_welcome():
    if 'user' not in session:
        return redirect(url_for('index'))  # If user is not logged in, redirect to home
    return render_template('patients_welcome.html', user=session['user'])  # Pass user info to the welcome page


# Logout route
@app.route('/logout')
def logout():
    session.clear()  # Clear session
    flash('You have logged out successfully.')
    return redirect(url_for('index'))  # Redirect to home page after logout

# Admin login and dashboard
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        connection = create_connection()
        if connection:
            cur = connection.cursor(dictionary=True)
            cur.execute("SELECT * FROM administrator WHERE username = %s", (request.form['username'],))
            admin = cur.fetchone()
            cur.close()
            connection.close()

            if admin and admin['password'] == request.form['password']:
                session['username'] = admin['username']
                session['logged_in'] = True
                flash('Login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid username or password!', 'danger')
        else:
            flash('Database connection failed', 'danger')
    return render_template('admin_login.html')

# Admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')




# DOCTORS

# Admin view doctors route
@app.route('/admin/view_doctors')
def view_doctors():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    connection = create_connection()
    if connection:
        try:
            cur = connection.cursor(dictionary=True)
            # Fetch all columns from the doctors table
            cur.execute("SELECT * FROM doctors")
            doctors = cur.fetchall()
            cur.close()
        except Exception as e:
            flash(f"Error fetching doctors: {e}", 'danger')
            doctors = []
        finally:
            connection.close()

        return render_template('view_doctors.html', doctors=doctors)
    flash('Database connection failed.', 'danger')
    return redirect(url_for('admin_dashboard'))

    
# Admin search doctors route
@app.route('/admin/search_doctors', methods=['GET', 'POST'])
def search_doctors():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    search_query = request.form.get('search_query', '')  # Get the search query
    connection = create_connection()

    if connection:
        cur = connection.cursor(dictionary=True)
        if search_query:
            # Search doctors by name
            cur.execute("SELECT * FROM doctors WHERE name LIKE %s", (f"%{search_query}%",))
        else:
            # Fetch all doctors if no search query is provided
            cur.execute("SELECT * FROM doctors")
        
        doctors = cur.fetchall()
        cur.close()
        connection.close()
        return render_template('search_doctors.html', doctors=doctors, search_query=search_query)
    
    flash('Database connection failed.', 'danger')
    return redirect(url_for('admin_dashboard'))

# Admin delete doctor route
@app.route('/admin/delete_doctor/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    connection = create_connection()
    if connection:
        try:
            cur = connection.cursor()
            # Delete doctor by ID
            cur.execute("DELETE FROM doctors WHERE D_ID = %s", (doctor_id,))
            connection.commit()
            cur.close()
            return render_template('delete_doctors.html')  # Render confirmation page
        except Exception as e:
            flash(f"Error deleting doctor: {e}", 'danger')
        finally:
            connection.close()
    else:
        flash('Database connection failed.', 'danger')

    return redirect(url_for('view_doctors'))

# Admin edit doctor route
@app.route('/admin/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    connection = create_connection()
    if request.method == 'POST':
        # Update doctor's information
        name = request.form['name']
        phone_no = request.form['phone_no']
        email = request.form['email']
        job_title = request.form['job_title']
        degree = request.form['degree']
        year = request.form['year']
        employer = request.form['employer']

        if connection:
            try:
                cur = connection.cursor()
                # Editting and updating doctor info
                cur.execute("""
                    UPDATE doctors 
                    SET name=%s, phone_no=%s, email=%s, job_title=%s, degree=%s, year=%s, employer=%s
                    WHERE D_ID=%s
                """, (name, phone_no, email, job_title, degree, year, employer, doctor_id))
                connection.commit()
                cur.close()
                flash('Doctor information updated successfully!', 'success')
                return redirect(url_for('view_doctors'))
            except Exception as e:
                flash(f"Error updating doctor: {e}", 'danger')
            finally:
                connection.close()
        else:
            flash('Database connection failed.', 'danger')
            return redirect(url_for('view_doctors'))
    else:
        # Fetch doctor's current information
        if connection:
            try:
                cur = connection.cursor(dictionary=True)
                cur.execute("SELECT * FROM doctors WHERE D_ID = %s", (doctor_id,))
                doctor = cur.fetchone()
                cur.close()
                if doctor:
                    return render_template('edit_doctors.html', doctor=doctor)
                else:
                    flash('Doctor not found.', 'danger')
                    return redirect(url_for('view_doctors'))
            except Exception as e:
                flash(f"Error fetching doctor: {e}", 'danger')
            finally:
                connection.close()
        else:
            flash('Database connection failed.', 'danger')
            return redirect(url_for('view_doctors'))



# Doctor appointment viewing
@app.route('/doctor/appointments')
def doctor_appointments():
    if 'user' not in session or session['user']['user_type'] != 'doctors':
        return redirect(url_for('index'))

    doctor_id = session['user']['D_ID']
    connection = create_connection()
    if connection:
        try:
            cur = connection.cursor(dictionary=True)
            # Display all appointments for the doctor including patient information for each appointment and any prescription given.
            cur.execute("""
                SELECT a.A_ID, a.time, a.status, a.notes, p.name AS patient_name, pr.name AS prescription_name
                FROM Appointment a
                JOIN Patient p ON a.P_ID = p.P_ID
                LEFT JOIN Prescription pr ON a.A_ID = pr.Pr_ID
                WHERE a.D_ID = %s
            """, (doctor_id,))
            appointments = cur.fetchall()
            cur.close()
            return render_template('doctors_welcome.html', appointments=appointments, user=session['user'])
        except Exception as e:
            flash(f"Error fetching appointments: {e}", 'danger')
        finally:
            connection.close()
    flash('Database connection failed.', 'danger')
    return redirect(url_for('index'))
    
    
# Doctor views prescriptions
@app.route('/doctor/prescriptions')
def view_prescriptions():
    if 'user' not in session or session['user']['user_type'] != 'doctors':
        return redirect(url_for('index'))

    doctor_id = session['user']['D_ID']
    connection = create_connection()
    if connection:
        try:
            cur = connection.cursor(dictionary=True)
            # List of prescriptions doctor has provided during appointments.
            cur.execute("""
                SELECT p.Pr_ID, p.name AS prescription_name, p.dosage, p.instructions, p.duration,
                       a.time AS appointment_time, pat.name AS patient_name
                FROM Prescription p
                JOIN Appointment a ON p.Pr_ID = a.A_ID
                JOIN Patient pat ON a.P_ID = pat.P_ID
                WHERE a.D_ID = %s
            """, (doctor_id,))
            prescriptions = cur.fetchall()
            cur.close()
            return render_template('view_prescriptions.html', prescriptions=prescriptions)
        except Exception as e:
            flash(f"Error fetching prescriptions: {e}", 'danger')
        finally:
            connection.close()

    flash('Database connection failed.', 'danger')
    return redirect(url_for('doctors_welcome'))






# Doctor prescription adding
@app.route('/doctor/add_prescription/<int:appointment_id>', methods=['GET', 'POST'])
def add_prescription(appointment_id):
    if 'user' not in session or session['user']['user_type'] != 'doctors':
        return redirect(url_for('index'))

    if request.method == 'POST':
        prescription_name = request.form['prescription_name']
        dosage = request.form['dosage']
        instructions = request.form['instructions']
        duration = request.form['duration']
        connection = create_connection()

        if connection:
            try:
                cur = connection.cursor()
                cur.execute("""
                    INSERT INTO Prescription (Pr_ID, name, dosage, instructions, duration)
                    VALUES (%s, %s, %s, %s, %s)
                """, (appointment_id, prescription_name, dosage, instructions, duration))
                connection.commit()
                cur.close()
                flash('Prescription added successfully!', 'success')
                return redirect(url_for('doctor_appointments'))
            except Exception as e:
                flash(f"Error adding prescription: {e}", 'danger')
            finally:
                connection.close()
        flash('Database connection failed.', 'danger')
    return render_template('add_prescription.html', appointment_id=appointment_id)



# Doctor Bill generation
@app.route('/doctor/generate_bill/<int:appointment_id>', methods=['GET', 'POST'])
def generate_bill(appointment_id):
    if 'user' not in session or session['user']['user_type'] != 'doctors':
        return redirect(url_for('index'))

    if request.method == 'POST':
        amount = request.form['amount']
        payment_status = request.form['payment_status']
        connection = create_connection()

        if connection:
            try:
                cur = connection.cursor()
                cur.execute("""
                    INSERT INTO Bill (B_ID, date, amount, payment_status)
                    VALUES (%s, CURDATE(), %s, %s)
                """, (appointment_id, amount, payment_status))
                connection.commit()
                cur.close()
                flash('Bill generated successfully!', 'success')
                return redirect(url_for('doctors_welcome'))
            except Exception as e:
                flash(f"Error generating bill: {e}", 'danger')
            finally:
                connection.close()
        flash('Database connection failed.', 'danger')
    return render_template('generate_bill.html', appointment_id=appointment_id)


#Doctor view bill route
@app.route('/view_bill/<int:appointment_id>')
def view_bill(appointment_id):
    if 'user' not in session or session['user']['user_type'] != 'doctors':
        return redirect(url_for('index'))

    connection = create_connection()
    bill = None

    if connection:
        try:
            cur = connection.cursor(dictionary=True)
            # Fetch the bill details based on the appointment ID
            cur.execute("""
                SELECT b.B_ID, b.date, b.amount, b.payment_status, a.time AS appointment_time, 
                       p.name AS patient_name, d.name AS doctor_name
                FROM Bill b
                JOIN Appointment a ON b.B_ID = a.A_ID
                JOIN Patient p ON a.P_ID = p.P_ID
                JOIN doctors d ON a.D_ID = d.D_ID
                WHERE b.B_ID = %s
            """, (appointment_id,))
            bill = cur.fetchone()
            cur.close()
        except Exception as e:
            flash(f"Error fetching bill details: {e}", 'danger')
        finally:
            connection.close()

    if not bill:
        flash('No bill found for this appointment.', 'warning')
        return redirect(url_for('doctors_welcome'))

    return render_template('view_bill.html', bill=bill)



# patient welcome page
@app.route('/patient/dashboard')
def patient_dashboard():
    if 'user' not in session or session['user']['user_type'] != 'patients':
        return redirect(url_for('index'))

    patient_id = session['user']['P_ID']
    connection = create_connection()
    if connection:
        try:
            cur = connection.cursor(dictionary=True)
            cur.execute("""
                SELECT a.time, a.status, d.name AS doctor_name, p.name AS prescription, b.amount, b.payment_status
                FROM Appointment a
                LEFT JOIN doctors d ON a.D_ID = d.D_ID
                LEFT JOIN Prescription p ON a.A_ID = p.Pr_ID
                LEFT JOIN Bill b ON a.A_ID = b.B_ID
                WHERE a.P_ID = %s
            """, (patient_id,))
            appointments = cur.fetchall()
            cur.close()
            return render_template('patients_welcome.html', appointments=appointments, user=session['user'])
        except Exception as e:
            flash(f"Error fetching appointments: {e}", 'danger')
        finally:
            connection.close()
    flash('Database connection failed.', 'danger')
    return redirect(url_for('index'))



# PATIENTS

# Admin view patients route
@app.route('/admin/view_patients')
def view_patients():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    connection = create_connection()
    if connection:
        cur = connection.cursor(dictionary=True)
        try:
            # Fetch all columns, including Age, from the Patient table
            cur.execute("SELECT P_ID, name, DOB, Age, symptoms, phone_no, blood_group, insurance, email FROM Patient")
            patients = cur.fetchall()
        except Exception as e:
            flash(f"Error fetching patients: {e}", 'danger')
            patients = []
        cur.close()
        connection.close()
        return render_template('view_patients.html', patients=patients)
    flash('Database connection failed.', 'danger')
    return redirect(url_for('admin_dashboard'))


    
# Admin search patients route
@app.route('/admin/search_patients', methods=['GET', 'POST'])
def search_patients():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    search_query = request.form.get('search_query', '')  # Get the search query
    connection = create_connection()

    if connection:
        cur = connection.cursor(dictionary=True)
        if search_query:
            # Search patients by name
            cur.execute("SELECT * FROM Patient WHERE name LIKE %s", (f"%{search_query}%",))
        else:
            # Fetch all patients if no search query is provided
            cur.execute("SELECT * FROM Patient")
        
        patients = cur.fetchall()
        cur.close()
        connection.close()
        return render_template('search_patients.html', patients=patients, search_query=search_query)
    
    flash('Database connection failed.', 'danger')
    return redirect(url_for('admin_dashboard'))
    
# Admin delete patients route
@app.route('/admin/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    connection = create_connection()
    if connection:
        try:
            cur = connection.cursor()
            # Delete patient by ID
            cur.execute("DELETE FROM Patient WHERE P_ID = %s", (patient_id,))
            connection.commit()
            cur.close()
            flash('Patient deleted successfully!', 'success')
        except Exception as e:
            flash(f"Error deleting patient: {e}", 'danger')
        finally:
            connection.close()
    else:
        flash('Database connection failed.', 'danger')

    return redirect(url_for('view_patients'))


# Admin edit patients route
@app.route('/admin/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    connection = create_connection()
    if request.method == 'POST':
        # Update patient information
        name = request.form['name']
        dob = request.form['dob']
        phone_no = request.form['phone_no']
        email = request.form['email']

        if connection:
            try:
                cur = connection.cursor()
                cur.execute("""
                    UPDATE Patient 
                    SET name=%s, DOB=%s, phone_no=%s, email=%s
                    WHERE P_ID=%s
                """, (name, dob, phone_no, email, patient_id))
                connection.commit()
                cur.close()
                flash('Patient information updated successfully!', 'success')
                return redirect(url_for('view_patients'))
            except Exception as e:
                flash(f"Error updating patient: {e}", 'danger')
            finally:
                connection.close()
        else:
            flash('Database connection failed.', 'danger')
            return redirect(url_for('view_patients'))
    else:
        # Fetch patient's current information
        if connection:
            try:
                cur = connection.cursor(dictionary=True)
                cur.execute("SELECT * FROM Patient WHERE P_ID = %s", (patient_id,))
                patient = cur.fetchone()
                cur.close()
                if patient:
                    return render_template('edit_patients.html', patient=patient)
                else:
                    flash('Patient not found.', 'danger')
                    return redirect(url_for('view_patients'))
            except Exception as e:
                flash(f"Error fetching patient: {e}", 'danger')
            finally:
                connection.close()
        else:
            flash('Database connection failed.', 'danger')
            return redirect(url_for('view_patients'))



# Admin view administrators route
@app.route('/admin/view_administrators')
def view_administrators():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    connection = create_connection()
    if connection:
        cur = connection.cursor(dictionary=True)
        cur.execute("SELECT * FROM administrator")
        administrators = cur.fetchall()
        cur.close()
        connection.close()
        return render_template('view_administrators.html', administrators=administrators)
    flash('Database connection failed.', 'danger')
    return redirect(url_for('admin_dashboard'))
    
    
# Admin views appointments
@app.route('/admin/view_appointments')
def view_all_appointments():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    connection = create_connection()
    if connection:
        try:
            cur = connection.cursor(dictionary=True)
            # Fetch all appointments with patient, doctor, and billing details
            cur.execute("""
                SELECT a.A_ID, a.time, a.status, a.notes,
                       p.name AS patient_name, d.name AS doctor_name,
                       b.amount AS bill_amount, b.payment_status
                FROM Appointment a
                JOIN Patient p ON a.P_ID = p.P_ID
                JOIN doctors d ON a.D_ID = d.D_ID
                LEFT JOIN Bill b ON a.A_ID = b.B_ID
            """)
            appointments = cur.fetchall()
            cur.close()
            return render_template('admin_view_appointments.html', appointments=appointments)
        except Exception as e:
            flash(f"Error fetching appointments: {e}", 'danger')
        finally:
            connection.close()
    else:
        flash('Database connection failed.', 'danger')

    return redirect(url_for('admin_dashboard'))

    
    
# Admin update payment_status
from flask import request, flash, redirect, url_for

# Route to update payment status
@app.route('/admin/update_payment_status/<int:bill_id>', methods=['POST'])
def update_payment_status(bill_id):
    if not session.get('logged_in'):  # Ensure the admin is logged in
        return redirect(url_for('admin_login'))
    
    new_status = request.form.get('payment_status')  # Get the new status from the form
    connection = create_connection()
    if connection:
        try:
            cur = connection.cursor()
            # Update the payment status for the specified bill
            cur.execute("""
                UPDATE Bill
                SET payment_status = %s
                WHERE B_ID = %s
            """, (new_status, bill_id))
            connection.commit()
            cur.close()
            flash('Payment status updated successfully!', 'success')
        except Exception as e:
            flash(f"Error updating payment status: {e}", 'danger')
        finally:
            connection.close()
    else:
        flash('Database connection failed.', 'danger')

    return redirect(url_for('view_all_appointments'))  # Redirect back to the appointments page



    


# APPOINTMENTS

# Book an appointment
@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'user' not in session or session['user'].get('user_type') != 'patients':
        flash("You must be logged in as a patient to book an appointment.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        connection = create_connection()
        if not connection:
            flash('Database connection failed. Please try again.', 'danger')
            return redirect(url_for('patients_welcome'))

        try:
            patient_id = session['user']['P_ID']
            doctor_id = request.form['doctor_id']
            appointment_datetime = f"{request.form['appointment_date']} {request.form['appointment_time']}"
            notes = request.form.get('symptoms', '')

            # Debug log
            print("Booking Data:", {
                "time": appointment_datetime,
                "notes": notes,
                "P_ID": patient_id,
                "D_ID": doctor_id
            })

            # Insert the appointment into the database
            cur = connection.cursor()
            cur.execute("""
                INSERT INTO Appointment (time, notes, P_ID, D_ID, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (appointment_datetime, notes, patient_id, doctor_id, 'Scheduled'))
            connection.commit()
            cur.close()

            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('view_appointments'))

        except mysql.connector.Error as e:
            print(f"MySQL Error: {e}")
            if "Duplicate entry" in str(e):
                flash("This appointment already exists.", 'danger')
            else:
                flash(f"Database error: {e}", 'danger')
        finally:
            connection.close()

    # Handle the GET request to show the booking form
    connection = create_connection()
    if not connection:
        flash('Database connection failed. Please try again later.', 'danger')
        return redirect(url_for('patients_welcome'))

    try:
        cur = connection.cursor(dictionary=True)
        cur.execute("SELECT D_ID, name FROM doctors")
        doctors = cur.fetchall()
        cur.close()
    except Exception as e:
        flash(f"Error fetching doctors: {e}", 'danger')
        doctors = []
    finally:
        connection.close()

    return render_template('book_app.html', user=session['user'], doctors=doctors)




# View Appointments
@app.route('/view_appointments')
def view_appointments():
    if 'user' not in session or session['user']['user_type'] != 'patients':
        return redirect(url_for('index'))

    patient_id = session['user']['P_ID']
    connection = create_connection()
    appointments = []

    if connection:
        try:
            cur = connection.cursor(dictionary=True)
            # Fetch appointment details along with prescriptions and bills
            cur.execute("""
                SELECT 
                    a.A_ID AS appointment_id, 
                    a.time AS appointment_time, 
                    a.notes, 
                    a.status, 
                    d.name AS doctor_name, 
                    p.name AS prescription_name, 
                    p.dosage, 
                    p.instructions, 
                    b.amount AS bill_amount, 
                    b.payment_status AS bill_status
                FROM Appointment a
                JOIN doctors d ON a.D_ID = d.D_ID
                LEFT JOIN Prescription p ON a.A_ID = p.Pr_ID
                LEFT JOIN Bill b ON a.A_ID = b.B_ID
                WHERE a.P_ID = %s
            """, (patient_id,))
            appointments = cur.fetchall()
            cur.close()
        except Exception as e:
            flash(f"Error fetching appointments: {e}", 'danger')
        finally:
            connection.close()
    else:
        flash('Database connection failed.', 'danger')

    return render_template('view_app.html', appointments=appointments)




# Cancel an appointment
@app.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    if 'user' not in session or session['user']['user_type'] != 'patients':
        return redirect(url_for('index'))

    connection = create_connection()
    if connection:
        try:
            cur = connection.cursor()
            # Delete the appointment from the database
            cur.execute("DELETE FROM Appointment WHERE A_ID = %s", (appointment_id,))
            connection.commit()
            cur.close()
            flash('Appointment canceled successfully!', 'success')
        except Exception as e:
            flash(f"Error canceling appointment: {e}", 'danger')
        finally:
            connection.close()
    else:
        flash('Database connection failed.', 'danger')

    return redirect(url_for('view_appointments'))



# Main entry point
if __name__ == '__main__':
    app.run(debug=True)
