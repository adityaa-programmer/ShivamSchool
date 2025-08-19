import streamlit as st
import pandas as pd
import json
from datetime import datetime
import re

# ============================================================================
# FIREBASE CONFIGURATION SECTION
# ============================================================================
# TODO: Install required packages first:
# pip install firebase-admin

import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase (Add your configuration here)
@st.cache_resource
def initialize_firebase():
    """Initialize Firebase connection"""
    try:

        # TODO: Replace with your Firebase credentials
        # Method 1: Using service account key file
        # cred = credentials.Certificate("serviceAccountKey.json")
        
        # Method 2: Using service account key from Streamlit secrets
        # Add your Firebase config to .streamlit/secrets.toml:
        # [firebase]
        # type = "service_account"
        # project_id = "your-project-id"
        # private_key_id = "your-private-key-id"
        # private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
        # client_email = "your-client-email"
        # client_id = "your-client-id"
        # auth_uri = "https://accounts.google.com/o/oauth2/auth"
        # token_uri = "https://oauth2.googleapis.com/token"
        
        if not firebase_admin._apps:
            # Uncomment and configure one of the methods below:
            
            # Method 1: From file
            cred = credentials.Certificate("serviceAccountKey.json")
            # firebase_admin.initialize_app(cred)
            
            # Method 2: From Streamlit secrets
            # cred = credentials.Certificate({
            #     "type": st.secrets["firebase"]["type"],
            #     "project_id": st.secrets["firebase"]["project_id"],
            #     "private_key_id": st.secrets["firebase"]["private_key_id"],
            #     "private_key": st.secrets["firebase"]["private_key"],
            #     "client_email": st.secrets["firebase"]["client_email"],
            #     "client_id": st.secrets["firebase"]["client_id"],
            #     "auth_uri": st.secrets["firebase"]["auth_uri"],
            #     "token_uri": st.secrets["firebase"]["token_uri"],
            # })
            
            firebase_admin.initialize_app(cred)
            # pass  # Remove this when you add your credentials
        
        return firestore.client()
    except Exception as e:
        st.error(f"Firebase initialization error: {str(e)}")
        return None

# Initialize Firestore client
db = initialize_firebase()

# Firebase helper functions
def add_student_to_firebase(student_data):
    """Add student to Firebase Firestore"""
    try:
        if db:
            doc_ref = db.collection('students').document()
            student_data['id'] = doc_ref.id
            doc_ref.set(student_data)
            return True, doc_ref.id
        return False, "Database not initialized"
    except Exception as e:
        return False, str(e)

def get_all_students_from_firebase():
    """Fetch all students from Firebase"""
    try:
        if db:
            students = []
            docs = db.collection('students').stream()
            for doc in docs:
                student_data = doc.to_dict()
                student_data['id'] = doc.id
                students.append(student_data)
            return students
        return []
    except Exception as e:
        st.error(f"Error fetching students: {str(e)}")
        return []

def update_student_in_firebase(student_id, updated_data):
    """Update student in Firebase"""
    try:
        if db:
            db.collection('students').document(student_id).update(updated_data)
            return True, "Student updated successfully"
        return False, "Database not initialized"
    except Exception as e:
        return False, str(e)

def delete_student_from_firebase(student_id):
    """Delete student from Firebase"""
    try:
        if db:
            db.collection('students').document(student_id).delete()
            return True, "Student deleted successfully"
        return False, "Database not initialized"
    except Exception as e:
        return False, str(e)

def search_students_in_firebase(field, value):
    """Search students in Firebase by field"""
    try:
        if db:
            students = []
            if field == "name":
                # For name search, we'll get all and filter (Firestore limitations)
                docs = db.collection('students').stream()
                for doc in docs:
                    data = doc.to_dict()
                    if value.lower() in data.get('name', '').lower():
                        data['id'] = doc.id
                        students.append(data)
            else:
                # For exact matches
                docs = db.collection('students').where(field, '==', value).stream()
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    students.append(data)
            return students
        return []
    except Exception as e:
        st.error(f"Error searching students: {str(e)}")
        return []

# ============================================================================
# END FIREBASE SECTION
# ============================================================================

# Page configuration
st.set_page_config(
    page_title="Student Management System - Shivam Public School",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark modern styling with icons
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
    
    /* Global Dark Theme */
    .stApp {
        background-color: #0a0e27;
        color: #ffffff;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0a0e27;
        color: #ffffff;
    }
    
    /* Beautiful Header */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #581c87 100%);
        padding: 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 25px 50px rgba(30, 58, 138, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="80" r="1.5" fill="rgba(255,255,255,0.1)"/></svg>');
        pointer-events: none;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 3.5rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .main-header h2 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 500;
        opacity: 0.9;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    /* School Info Box */
    .school-info {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid #475569;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .school-info h2 {
        color: #60a5fa;
        margin-bottom: 0.5rem;
        font-size: 2rem;
        font-weight: 700;
    }
    
    .school-info p {
        color: #cbd5e1;
        font-size: 1.1rem;
        margin: 0;
    }
    
    /* Login Container */
    .login-container {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        max-width: 500px;
        margin: 2rem auto;
        border: 1px solid #475569;
    }
    
    /* Dark Cards */
    .metric-card {
        background: linear-gradient(135deg, #059669 0%, #0d9488 100%);
        padding: 2.5rem;
        border-radius: 15px;
        text-align: center;
        color: #ffffff;
        font-weight: 600;
        box-shadow: 0 15px 35px rgba(5, 150, 105, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        transform: scale(0);
        transition: transform 0.5s ease;
    }
    
    .metric-card:hover::before {
        transform: scale(1);
    }
    
    .metric-card h3 {
        font-size: 2rem;
        margin: 0;
        position: relative;
        z-index: 1;
    }
    
    .metric-card p {
        position: relative;
        z-index: 1;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    .student-card {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border: 1px solid #6b7280;
        color: #ffffff;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .student-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }
    
    .student-card h4 {
        color: #60a5fa;
        margin-bottom: 1rem;
        font-size: 1.4rem;
        font-weight: 600;
    }
    
    .student-card p {
        margin: 0.5rem 0;
        color: #e5e7eb;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #111827;
    }
    
    .css-1v0mbdj {
        background: linear-gradient(180deg, #1f2937 0%, #374151 100%);
        border-radius: 15px;
        margin: 1rem;
        padding: 1rem;
        border: 1px solid #4b5563;
    }
    
    /* Enhanced Button Styling with Icons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 35px rgba(59, 130, 246, 0.5);
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Input Fields Dark Theme */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #4b5563;
        background-color: #374151;
        color: #ffffff;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 0.2rem rgba(59, 130, 246, 0.25);
        background-color: #4b5563;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #9ca3af;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #4b5563;
        background-color: #374151;
        color: #ffffff;
        font-size: 1rem;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6;
        background-color: #4b5563;
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: #9ca3af;
    }
    
    .stSelectbox > div > div {
        border-radius: 12px;
        border: 2px solid #4b5563;
        background-color: #374151;
        color: #ffffff;
    }
    
    .stSelectbox > div > div > div {
        background-color: #374151;
        color: #ffffff;
    }
    
    /* Labels */
    .stTextInput > label, .stTextArea > label, .stSelectbox > label {
        color: #e5e7eb !important;
        font-weight: 500;
        font-size: 1rem;
    }
    
    /* Role Badges */
    .role-badge {
        display: inline-block;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        margin-top: 1rem;
        position: relative;
        z-index: 1;
    }
    
    .management-badge {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 25px rgba(245, 158, 11, 0.3);
    }
    
    .principal-badge {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
    }
    
    /* Table Styling Dark */
    .stDataFrame {
        background-color: #1f2937;
        border-radius: 15px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        border: 1px solid #374151;
    }
    
    .stDataFrame table {
        background-color: #1f2937;
        color: #ffffff;
    }
    
    .stDataFrame th {
        background-color: #374151 !important;
        color: #ffffff !important;
        border-color: #4b5563 !important;
    }
    
    .stDataFrame td {
        background-color: #1f2937 !important;
        color: #e5e7eb !important;
        border-color: #4b5563 !important;
    }
    
    /* Success/Error Messages Dark */
    .stSuccess {
        background-color: #064e3b;
        color: #6ee7b7;
        border: 2px solid #059669;
        border-radius: 10px;
    }
    
    .stError {
        background-color: #7f1d1d;
        color: #fca5a5;
        border: 2px solid #dc2626;
        border-radius: 10px;
    }
    
    .stWarning {
        background-color: #78350f;
        color: #fcd34d;
        border: 2px solid #d97706;
        border-radius: 10px;
    }
    
    .stInfo {
        background-color: #1e3a8a;
        color: #93c5fd;
        border: 2px solid #2563eb;
        border-radius: 10px;
    }
    
    /* Footer Styling Dark */
    .footer {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        padding: 2.5rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 3rem;
        border: 1px solid #4b5563;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    }
    
    .footer-content {
        color: #e5e7eb;
        font-size: 1rem;
        font-weight: 500;
    }
    
    .footer-highlight {
        color: #60a5fa;
        font-weight: 700;
    }
    
    /* Section Headers Dark */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* Page Background Dark */
    .main .block-container {
        padding-top: 2rem;
        background-color: #111827;
        border-radius: 15px;
        margin: 1rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        border: 1px solid #1f2937;
    }
    
    /* Sidebar Dark */
    .css-1lcbmhc, .css-1v0mbdj {
        background-color: #1f2937 !important;
        color: #ffffff !important;
    }
    
    /* Sidebar text */
    .css-1v0mbdj p, .css-1v0mbdj h1, .css-1v0mbdj h2, .css-1v0mbdj h3 {
        color: #ffffff !important;
    }
    
    /* Navigation Icons */
    .nav-icon {
        margin-right: 0.5rem;
        font-size: 1.1rem;
    }
    
    /* Operation Card Icons */
    .operation-card {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 1px solid #6b7280;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .operation-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    
    .operation-icon {
        font-size: 1.5rem;
        margin-right: 1rem;
        color: #60a5fa;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for form clearing
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'clear_form' not in st.session_state:
    st.session_state.clear_form = False

# Updated User credentials
USERS = {
    "Harshu": {"password": "harshu@123", "role": "Management"},
    "Shivam": {"password": "shivam@123", "role": "Principal"}
}

def validate_mobile_number(mobile):
    """Validate mobile number format"""
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, str(mobile)) is not None

def validate_student_data(name, class_name, roll_no, address, mobile1, mobile2, student_id=None):
    """Validate all student data"""
    errors = []
    
    if not name.strip():
        errors.append("Name is required")
    if not class_name.strip():
        errors.append("Class is required")
    if not roll_no.strip():
        errors.append("Roll number is required")
    if not address.strip():
        errors.append("Address is required")
    if not mobile1.strip():
        errors.append("Mobile number 1 is required")
    if not mobile2.strip():
        errors.append("Mobile number 2 is required")
    
    if mobile1.strip() and not validate_mobile_number(mobile1):
        errors.append("Mobile number 1 must be a valid 10-digit Indian mobile number")
    if mobile2.strip() and not validate_mobile_number(mobile2):
        errors.append("Mobile number 2 must be a valid 10-digit Indian mobile number")
    
    if mobile1.strip() and mobile2.strip() and mobile1 == mobile2:
        errors.append("Both mobile numbers must be different")
    
    # Check for duplicate roll number in Firebase
    if roll_no.strip() and db:
        try:
            existing_students = db.collection('students').where('roll_no', '==', roll_no.strip()).stream()
            for doc in existing_students:
                if student_id is None or doc.id != student_id:
                    errors.append("Roll number already exists")
                    break
        except Exception as e:
            st.error(f"Error checking duplicate roll number: {str(e)}")
    
    return errors

def add_footer():
    """Add footer to all pages"""
    st.markdown("""
    <div class="footer">
        <div class="footer-content">
            <p><i class="fas fa-graduation-cap"></i> <strong>Shivam Public School</strong> - Student Management System</p>
            <p><i class="fas fa-laptop-code"></i> Developers <span class="footer-highlight">Aditya</span> & <span class="footer-highlight">Aditi</span></p>
            <p><i class="fas fa-envelope"></i> For technical support, contact the development team</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def login_page():
    """Display login page"""
    st.markdown("""
    <div class="main-header">
        <h1><i class="fas fa-graduation-cap"></i> Student Management System</h1>
        <h2><i class="fas fa-school"></i> Shivam Public School</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="school-info">
            <h2><i class="fas fa-building"></i> Shivam Public School</h2>
            <p><i class="fas fa-users-cog"></i> Student Management Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="login-container">
        """, unsafe_allow_html=True)
        
        st.markdown("### <i class='fas fa-lock'></i> Login")
        st.markdown("---")
        
        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
        
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("🚀 Login", use_container_width=True):
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user_role = USERS[username]["role"]
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Add footer to login page
    add_footer()

def main_dashboard():
    """Main dashboard after login"""
    # Header with school name and role badge
    role_class = "management-badge" if st.session_state.user_role == "Management" else "principal-badge"
    role_icon = "fas fa-user-tie" if st.session_state.user_role == "Management" else "fas fa-user-graduate"
    
    st.markdown(f"""
    <div class="main-header">
        <h1><i class="fas fa-graduation-cap"></i> Student Management System</h1>
        <h2><i class="fas fa-school"></i> Shivam Public School</h2>
        <div class="role-badge {role_class}">
            <i class="{role_icon}"></i> {st.session_state.user_role} Access
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### <i class='fas fa-bars'></i> Navigation")
        st.markdown("**<i class='fas fa-school'></i> Shivam Public School**")
        st.markdown("---")
        
        # Show different options based on role
        if st.session_state.user_role == "Principal":
            options = [
                ("➕ Add Students", "Add Students"),
                ("🔍 Search", "Search"), 
                ("👥 View All", "View All"),
                ("✏️ Update", "Update"),
                ("🗑️ Delete", "Delete")
            ]
        else:  # Management
            options = [
                ("➕ Add Students", "Add Students"),
                ("🔍 Search", "Search"),
                ("👥 View All", "View All")
            ]
        
        operation = st.selectbox(
            "Choose Operation",
            [opt[1] for opt in options],
            format_func=lambda x: next(opt[0] for opt in options if opt[1] == x),
            index=0
        )
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.rerun()
    
    # Display total students count from Firebase
    students_data = get_all_students_from_firebase()
    total_students = len(students_data)
    st.markdown(f"""
    <div class="metric-card">
        <h3><i class="fas fa-users"></i> Total Students: {total_students}</h3>
        <p><i class="fas fa-database"></i> Shivam Public School Database</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content based on selected operation
    if operation == "Add Students":
        add_student_form()
    elif operation == "Search":
        search_students()
    elif operation == "View All":
        view_all_students()
    elif operation == "Update":
        update_student()
    elif operation == "Delete":
        delete_student()
    
    # Add footer to all pages
    add_footer()

def add_student_form():
    """Form to add new student"""
    st.markdown("### <i class='fas fa-user-plus'></i> Add New Student")
    st.markdown("**<i class='fas fa-school'></i> Shivam Public School - Student Registration**")
    st.markdown("---")
    
    # Clear form fields if form was just submitted
    if st.session_state.clear_form:
        st.session_state.clear_form = False
        st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("👤 Student Name*", 
                           placeholder="Enter full name", 
                           key="name_input")
        class_name = st.text_input("🏫 Class*", 
                                 placeholder="e.g., 10th A", 
                                 key="class_input")
        roll_no = st.text_input("🎯 Roll Number*", 
                              placeholder="e.g., 2024001", 
                              key="roll_input")
    
    with col2:
        address = st.text_area("📍 Address*", 
                             placeholder="Enter complete address", 
                             key="address_input")
        mobile1 = st.text_input("📱 Mobile Number 1*", 
                              placeholder="Enter 10-digit mobile number", 
                              key="mobile1_input")
        mobile2 = st.text_input("📱 Mobile Number 2*", 
                              placeholder="Enter different 10-digit mobile number", 
                              key="mobile2_input")
    
    if st.button("✅ Add Student", use_container_width=True):
        errors = validate_student_data(name, class_name, roll_no, address, mobile1, mobile2)
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            new_student = {
                "name": name.strip(),
                "class": class_name.strip(),
                "roll_no": roll_no.strip(),
                "address": address.strip(),
                "mobile1": mobile1.strip(),
                "mobile2": mobile2.strip(),
                "added_by": st.session_state.user_role,
                "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to Firebase
            success, result = add_student_to_firebase(new_student)
            if success:
                st.success("🎉 Student added successfully to Shivam Public School database!")
                st.balloons()
                # Clear form by triggering a rerun
                st.session_state.clear_form = True
                # Clear the input values from session state
                for key in ['name_input', 'class_input', 'roll_input', 'address_input', 'mobile1_input', 'mobile2_input']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
            else:
                st.error(f"❌ Error adding student: {result}")

def search_students():
    """Search students functionality"""
    st.markdown("### <i class='fas fa-search'></i> Search Students")
    st.markdown("**<i class='fas fa-school'></i> Shivam Public School - Student Search**")
    st.markdown("---")
    
    search_options = [
        ("👤 Name", "Name"),
        ("🏫 Class", "Class"), 
        ("🎯 Roll Number", "Roll Number")
    ]
    
    search_type = st.selectbox(
        "Search By", 
        [opt[1] for opt in search_options],
        format_func=lambda x: next(opt[0] for opt in search_options if opt[1] == x)
    )
    
    search_query = st.text_input(f"Enter {search_type}", placeholder=f"Type {search_type.lower()} to search...")
    
    if search_query:
        # Map search types to Firebase fields
        field_map = {
            "Name": "name",
            "Class": "class",
            "Roll Number": "roll_no"
        }
        
        field = field_map[search_type]
        results = search_students_in_firebase(field, search_query)
        
        if results:
            st.success(f"✅ Found {len(results)} student(s) in Shivam Public School database")
            display_students_table(results)
        else:
            st.warning("⚠️ No students found matching your search criteria")

def view_all_students():
    """Display all students in a clean table format"""
    st.markdown("### <i class='fas fa-users'></i> All Students")
    st.markdown("**<i class='fas fa-school'></i> Shivam Public School - Complete Student Database**")
    st.markdown("---")
    
    # Fetch all students from Firebase
    students_data = get_all_students_from_firebase()
    
    if not students_data:
        st.info("📝 No students added yet to Shivam Public School database.")
        return
    
    # Sort options
    sort_options = [
        ("👤 Name", "Name"),
        ("🏫 Class", "Class"),
        ("🎯 Roll Number", "Roll Number"),
        ("📅 Date Added", "Date Added")
    ]
    
    sort_by = st.selectbox(
        "Sort By", 
        [opt[1] for opt in sort_options],
        format_func=lambda x: next(opt[0] for opt in sort_options if opt[1] == x)
    )
    
    sorted_students = students_data.copy()
    if sort_by == "Name":
        sorted_students.sort(key=lambda x: x.get("name", ""))
    elif sort_by == "Class":
        sorted_students.sort(key=lambda x: x.get("class", ""))
    elif sort_by == "Roll Number":
        sorted_students.sort(key=lambda x: x.get("roll_no", ""))
    elif sort_by == "Date Added":
        sorted_students.sort(key=lambda x: x.get("date_added", ""), reverse=True)
    
    # Display students in table format
    display_students_table(sorted_students)

def display_students_table(students):
    """Display students in a clean table format"""
    if not students:
        st.info("No students to display")
        return
    
    # Create DataFrame for better table display
    table_data = []
    for student in students:
        table_data.append({
            "Name": student.get('name', 'N/A'),
            "Class": student.get('class', 'N/A'),
            "Roll No": student.get('roll_no', 'N/A'),
            "Address": student.get('address', 'N/A'),
            "Mobile 1": student.get('mobile1', 'N/A'),
            "Mobile 2": student.get('mobile2', 'N/A'),
            "Added By": student.get('added_by', 'N/A'),
            "Date Added": student.get('date_added', 'N/A')
        })
    
    df = pd.DataFrame(table_data)
    
    # Display as a styled table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Name": st.column_config.TextColumn("👤 Name", width="medium"),
            "Class": st.column_config.TextColumn("🏫 Class", width="small"),
            "Roll No": st.column_config.TextColumn("🎯 Roll No", width="small"),
            "Address": st.column_config.TextColumn("📍 Address", width="large"),
            "Mobile 1": st.column_config.TextColumn("📱 Mobile 1", width="medium"),
            "Mobile 2": st.column_config.TextColumn("📱 Mobile 2", width="medium"),
            "Added By": st.column_config.TextColumn("➕ Added By", width="small"),
            "Date Added": st.column_config.TextColumn("📅 Date Added", width="medium")
        }
    )
    
    # Export to CSV option
    if st.button("📥 Export to CSV"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="📋 Download Shivam Public School Students Data",
            data=csv,
            file_name=f"shivam_public_school_students_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def display_student_card(student):
    """Display student information in a card format"""
    st.markdown(f"""
    <div class="student-card">
        <h4><i class="fas fa-user"></i> {student.get('name', 'N/A')}</h4>
        <p><strong><i class="fas fa-school"></i> Class:</strong> {student.get('class', 'N/A')}</p>
        <p><strong><i class="fas fa-hashtag"></i> Roll No:</strong> {student.get('roll_no', 'N/A')}</p>
        <p><strong><i class="fas fa-map-marker-alt"></i> Address:</strong> {student.get('address', 'N/A')}</p>
        <p><strong><i class="fas fa-mobile-alt"></i> Mobile 1:</strong> {student.get('mobile1', 'N/A')}</p>
        <p><strong><i class="fas fa-mobile-alt"></i> Mobile 2:</strong> {student.get('mobile2', 'N/A')}</p>
        <p><strong><i class="fas fa-user-plus"></i> Added by:</strong> {student.get('added_by', 'N/A')}</p>
        <p><strong><i class="fas fa-calendar-alt"></i> Date Added:</strong> {student.get('date_added', 'N/A')}</p>
        <p><strong><i class="fas fa-building"></i> School:</strong> Shivam Public School</p>
    </div>
    """, unsafe_allow_html=True)

def update_student():
    """Update student information (Principal only)"""
    st.markdown("### <i class='fas fa-edit'></i> Update Student")
    st.markdown("**<i class='fas fa-school'></i> Shivam Public School - Student Information Update**")
    st.markdown("---")
    
    # Fetch all students from Firebase
    students_data = get_all_students_from_firebase()
    
    if not students_data:
        st.info("📝 No students to update in Shivam Public School database.")
        return
    
    # Select student to update
    student_options = [f"{s.get('name', 'Unknown')} (Roll: {s.get('roll_no', 'N/A')})" for s in students_data]
    selected_option = st.selectbox("🔍 Select Student to Update", student_options)
    
    if selected_option:
        selected_index = student_options.index(selected_option)
        student = students_data[selected_index]
        
        st.markdown("#### <i class='fas fa-info-circle'></i> Current Information:")
        display_student_card(student)
        
        st.markdown("#### <i class='fas fa-edit'></i> Update Information:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("👤 Student Name*", value=student.get('name', ''))
            new_class = st.text_input("🏫 Class*", value=student.get('class', ''))
            new_roll_no = st.text_input("🎯 Roll Number*", value=student.get('roll_no', ''))
        
        with col2:
            new_address = st.text_area("📍 Address*", value=student.get('address', ''))
            new_mobile1 = st.text_input("📱 Mobile Number 1*", value=student.get('mobile1', ''))
            new_mobile2 = st.text_input("📱 Mobile Number 2*", value=student.get('mobile2', ''))
        
        if st.button("💾 Update Student", use_container_width=True):
            errors = validate_student_data(new_name, new_class, new_roll_no, new_address, new_mobile1, new_mobile2, student['id'])
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                updated_data = {
                    "name": new_name.strip(),
                    "class": new_class.strip(),
                    "roll_no": new_roll_no.strip(),
                    "address": new_address.strip(),
                    "mobile1": new_mobile1.strip(),
                    "mobile2": new_mobile2.strip(),
                }
                
                success, message = update_student_in_firebase(student['id'], updated_data)
                if success:
                    st.success("✅ Student updated successfully in Shivam Public School database!")
                    st.rerun()
                else:
                    st.error(f"❌ Error updating student: {message}")

def delete_student():
    """Delete student (Principal only)"""
    st.markdown("### <i class='fas fa-trash-alt'></i> Delete Student")
    st.markdown("**<i class='fas fa-school'></i> Shivam Public School - Student Removal**")
    st.markdown("---")
    
    # Fetch all students from Firebase
    students_data = get_all_students_from_firebase()
    
    if not students_data:
        st.info("📝 No students to delete from Shivam Public School database.")
        return
    
    # Select student to delete
    student_options = [f"{s.get('name', 'Unknown')} (Roll: {s.get('roll_no', 'N/A')})" for s in students_data]
    selected_option = st.selectbox("🔍 Select Student to Delete", student_options)
    
    if selected_option:
        selected_index = student_options.index(selected_option)
        student = students_data[selected_index]
        
        st.markdown("#### <i class='fas fa-exclamation-triangle'></i> Student to be deleted:")
        display_student_card(student)
        
        st.warning("⚠️ This action cannot be undone! The student will be permanently removed from Shivam Public School database.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🗑️ Confirm Delete", use_container_width=True):
                success, message = delete_student_from_firebase(student['id'])
                if success:
                    st.success("✅ Student deleted successfully from Shivam Public School database!")
                    st.rerun()
                else:
                    st.error(f"❌ Error deleting student: {message}")

# Main app logic
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()