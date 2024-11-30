# Patient Records Management System

## 📚 Overview
The **Patient Records Management System** is a robust web-based application designed for hospitals and healthcare providers to streamline the management of patient records, appointments, prescriptions, and billing. Built using **Python Flask**, the system ensures efficient coordination between administrators, doctors, and patients in a secure and user-friendly environment.

## 🚀 Features
### **For Patients**
- **Dashboard**: View personal details and upcoming appointments.
- **Appointment Management**: Book, view, and cancel appointments seamlessly.
- **Prescription History**: Access prescriptions provided by doctors.
- **Billing Information**: View bills and payment status.

### **For Doctors**
- **Doctor's Dashboard**: Manage appointments and view assigned patients.
- **Prescription Management**: Add and view prescriptions for patient records.
- **Billing System**: Generate and update patient bills.
- **Patient Details**: Access detailed patient information to deliver better care.

### **For Administrators**
- **Admin Dashboard**: Oversee doctors, patients, and appointments.
- **User Management**:
  - View and manage patient records.
  - Add, edit, or delete doctor profiles.
- **Appointment Overview**: Monitor all appointments and payment statuses.
- **Secure Login**: Role-based access for patients, doctors, and admins.

## 🛠️ Technology Stack
- **Frontend**: HTML, CSS, Bootstrap
- **Backend**: Python (Flask Framework)
- **Database**: SQLite (Easily replaceable with MySQL or PostgreSQL)
- **Libraries Used**:
  - `Flask`: For creating the web application.
  - `Jinja2`: For dynamic HTML templating.
  - `Werkzeug`: For password hashing and authentication.
  - `Bootstrap`: For responsive and modern UI designs.

## 🔑 Key Functionalities
- **Authentication System**:
  - Separate login portals for patients, doctors, and admins.
  - Encrypted passwords for secure user authentication.
- **Responsive Design**:
  - Optimized for all devices, ensuring a seamless user experience on mobile, tablet, and desktop.
- **CRUD Operations**:
  - Perform Create, Read, Update, Delete operations for patient and doctor records.
- **Dynamic Dashboards**:
  - Personalized interfaces based on user roles.

## 📋 Project Structure
```plaintext
├── app.py                  # Main application logic
├── hosp.sql
├── templates/              # HTML files for all pages
│   ├── login.html
│   ├── dashboard.html
│   ├── patients_welcome.html
│   ├── doctors_welcome.html
│   ├── admin_dashboard.html
│   └── ...

---

## 💻 Installation and Usage
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/patient-records-management.git
   cd patient-records-management
2. **Run the file**:
   ```bash
   python app.py
3. **Access the Application**:
   Open your browser and navigate to http://127.0.0.1:5000/.

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature/bug fix.
3. Submit a pull request.
