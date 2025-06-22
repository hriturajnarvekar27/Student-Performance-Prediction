import streamlit as st
import pyodbc
import bcrypt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import numpy as np
import re
import logging
from cgpa_calculator import calculate_required_marks

# Database connection setup
def get_db_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=FRENZY\\SQLEXPRESS;"
        "DATABASE=DYPATU_StudentDB;"
        "Trusted_Connection=yes;"
    )
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Password hashing
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# Session state for user authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None

# Translations for bilingual support
translations = {
    "en": {
        "welcome_message": "Student Performance Prediction & CGPA Calculator!",
        "select_language": "Select Language",
        "select_feature": "Select Feature",
        "student_profile": "Student Profile",
        "predict_exam_marks": "Predict Exam Marks",
        "calculate_cgpa": "Calculate CGPA/Percentage Goal",
        "compare_scores": "Compare Scores",
        "logout": "Logout",
        "login": "Login",
        "signup": "Sign Up",
        "username": "Username",
        "email": "Email",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "previous_percentage": "Previous Percentage (50-95%)",
        "past_attendance": "Past Attendance (60-100%)",
        "study_hours": "Study Hours per Week (5-20)",
        "commute_time": "Commute Time per Day (0-2 hours)",
        "board_exam_marks": "Board Exam Marks (60-95%)",
        "tuition_hours": "Tuition Hours per Week (0-10)",
        "predict_button": "Predict",
        "target_exam_marks": "Target Exam Marks (%)",
        "target_attendance": "Target Attendance (%)",
        "predicted_marks": "Predicted Exam Marks: {:.1f}%",
        "predicted_attendance": "Predicted Attendance: {:.1f}%",
        "study_tips": "Study Tips",
        "tip_low_study_hours": "Consider increasing your study hours to at least 15 per week to improve your performance.",
        "tip_low_attendance": "Your attendance is below the required 75%. Attend more classes to avoid being barred from exams.",
        "tip_low_marks": "Your predicted marks are below the passing threshold of 40%. Focus on key subjects and seek help if needed.",
        "tip_high_commute": "Your commute time is high. Try to optimize your travel or study during commute to save time.",
        "explore_study_hours": "Explore Impact of Study Hours",
        "grading_scale": "Select Grading Scale",
        "cgpa": "CGPA (0-10)",
        "percentage": "Percentage (0-100%)",
        "credits_per_semester": "Credits per Semester",
        "semester_grades": "Enter your semester grades (SGPA or Percentage)",
        "target_cgpa": "Target Final CGPA/Percentage",
        "calculate_button": "Calculate",
        "required_average": "Required average for remaining semesters: {:.2f}",
        "all_semesters_completed": "All semesters are completed. No further calculation needed.",
        "what_if_analysis": "What-If Analysis",
        "hypothetical_grades": "Enter hypothetical grades for remaining semesters",
        "calculate_projected": "Calculate Projected CGPA/Percentage",
        "projected_cgpa": "Projected Final CGPA/Percentage: {:.2f}",
        "progress_toward_target": "Progress Toward Target",
        "semester_wise_progress": "Semester-Wise Progress",
        "performance_insight": "Performance Insight: {}",
        "improving": "Your performance is improving. Keep up the good work!",
        "declining": "Your performance is declining. Consider revising your study habits.",
        "inconsistent": "Your performance is inconsistent. Try to maintain a steady study routine.",
        "save_to_profile": "Save Grades to Profile",
        "class_average": "Class Average",
        "top_performer": "Top Performer",
        "your_scores": "Your Scores",
        "semester_grades_comparison": "Semester Grades Comparison",
        "cgpa_comparison": "Average CGPA Comparison",
        "predicted_marks_comparison": "Predicted Exam Marks Comparison",
        "predicted_attendance_comparison": "Predicted Attendance Comparison",
        "comparison_insights": "Comparison Insights",
        "below_class_average": "Your {metric} ({value:.2f}) is below the class average ({avg:.2f}). Consider focusing on {suggestion}.",
        "above_class_average": "Great job! Your {metric} ({value:.2f}) is above the class average ({avg:.2f}). Keep up the good work!",
        "below_top_performer": "Your {metric} ({value:.2f}) is below the top performer ({top:.2f}). Aim to improve by {suggestion}.",
    },
    "mr": {
        "welcome_message": "विद्यार्थी कामगिरी अंदाज आणि CGPA कॅल्क्युलेटर मध्ये आपले स्वागत आहे!",
        "select_language": "भाषा निवडा",
        "select_feature": "वैशिष्ट्य निवडा",
        "student_profile": "विद्यार्थी प्रोफाइल",
        "predict_exam_marks": "परीक्षा गुणांचा अंदाज",
        "calculate_cgpa": "CGPA/टक्केवारी ध्येयाची गणना",
        "compare_scores": "स्कोअरची तुलना करा",
        "logout": "लॉगआउट",
        "login": "लॉगिन",
        "signup": "साइन अप",
        "username": "वापरकर्तानाव",
        "email": "ईमेल",
        "password": "पासवर्ड",
        "confirm_password": "पासवर्डची पुष्टी करा",
        "previous_percentage": "मागील टक्केवारी (50-95%)",
        "past_attendance": "मागील उपस्थिती (60-100%)",
        "study_hours": "प्रति आठवडा अभ्यासाचे तास (5-20)",
        "commute_time": "प्रति दिन प्रवास वेळ (0-2 तास)",
        "board_exam_marks": "बोर्ड परीक्षा गुण (60-95%)",
        "tuition_hours": "प्रति आठवडा ट्यूशन तास (0-10)",
        "predict_button": "अंदाज करा",
        "target_exam_marks": "लक्ष्य परीक्षा गुण (%)",
        "target_attendance": "लक्ष्य उपस्थिती (%)",
        "predicted_marks": "अंदाजित परीक्षा गुण: {:.1f}%",
        "predicted_attendance": "अंदाजित उपस्थिती: {:.1f}%",
        "study_tips": "अभ्यास टिप्स",
        "tip_low_study_hours": "आपले अभ्यासाचे तास किमान 15 प्रति आठवडा वाढवण्याचा विचार करा.",
        "tip_low_attendance": "आपली उपस्थिती 75% पेक्षा कमी आहे. परीक्षेपासून वंचित राहू नये म्हणून जास्त वर्गांना उपस्थित रहा.",
        "tip_low_marks": "आपले अंदाजित गुण 40% पासिंग थ्रेशोल्डपेक्षा कमी आहेत. मुख्य विषयांवर लक्ष केंद्रित करा.",
        "tip_high_commute": "आपला प्रवास वेळ जास्त आहे. प्रवास ऑप्टिमाइझ करा किंवा प्रवासात अभ्यास करा.",
        "explore_study_hours": "अभ्यास तासांचा प्रभाव एक्सप्लोर करा",
        "grading_scale": "ग्रेडिंग स्केल निवडा",
        "cgpa": "CGPA (0-10)",
        "percentage": "टक्केवारी (0-100%)",
        "credits_per_semester": "प्रति सेमिस्टर क्रेडिट्स",
        "semester_grades": "आपले सेमिस्टर ग्रेड्स प्रविष्ट करा (SGPA किंवा टक्केवारी)",
        "target_cgpa": "लक्ष्य अंतिम CGPA/टक्केवारी",
        "calculate_button": "गणना करा",
        "required_average": "उर्वरित सेमिस्टरसाठी आवश्यक सरासरी: {:.2f}",
        "all_semesters_completed": "सर्व सेमिस्टर पूर्ण झाले आहेत. पुढील गणनेची आवश्यकता नाही.",
        "what_if_analysis": "व्हॉट-इफ विश्लेषण",
        "hypothetical_grades": "उर्वरित सेमिस्टरसाठी काल्पनिक ग्रेड्स प्रविष्ट करा",
        "calculate_projected": "प्रोजेक्टेड CGPA/टक्केवारी गणना करा",
        "projected_cgpa": "प्रोजेक्टेड अंतिम CGPA/टक्केवारी: {:.2f}",
        "progress_toward_target": "लक्ष्याकडे प्रगती",
        "semester_wise_progress": "सेमिस्टर-निहाय प्रगती",
        "performance_insight": "कामगिरी अंतर्दृष्टी: {}",
        "improving": "आपली कामगिरी सुधारत आहे. चांगले काम चालू ठेवा!",
        "declining": "आपली कामगिरी कमी होत आहे. अभ्यास सवयींचा पुनर्विचार करा.",
        "inconsistent": "आपली कामगिरी असंगत आहे. स्थिर अभ्यास रूटीन ठेवण्याचा प्रयत्न करा。",
        "save_to_profile": "ग्रेड्स प्रोफाइलमध्ये जतन करा",
        "class_average": "वर्ग सरासरी",
        "top_performer": "सर्वोत्तम कामगिरी करणारा",
        "your_scores": "तुमचे स्कोअर",
        "semester_grades_comparison": "सेमिस्टर ग्रेड्सची तुलना",
        "cgpa_comparison": "सरासरी CGPA ची तुलना",
        "predicted_marks_comparison": "अंदाजित परीक्षा गुणांची तुलना",
        "predicted_attendance_comparison": "अंदाजित उपस्थितीची तुलना",
        "comparison_insights": "तुलना अंतर्दृष्टी",
        "below_class_average": "तुमचे {metric} ({value:.2f}) वर्ग सरासरीपेक्षा ({avg:.2f}) कमी आहे. {suggestion} वर लक्ष केंद्रित करण्याचा विचार करा.",
        "above_class_average": "छान काम! तुमचे {metric} ({value:.2f}) वर्ग सरासरीपेक्षा ({avg:.2f}) जास्त आहे. चांगले काम चालू ठेवा!",
        "below_top_performer": "तुमचे {metric} ({value:.2f}) सर्वोत्तम कामगिरी करणाऱ्यापेक्षा ({top:.2f}) कमी आहे. {suggestion} करून सुधारणा करण्याचा प्रयत्न करा.",
    }
}

# Language selection
if 'language' not in st.session_state:
    st.session_state.language = 'en'

st.sidebar.title(translations[st.session_state.language]["select_language"])
language = st.sidebar.selectbox(
    translations[st.session_state.language]["select_language"],
    ["English", "Marathi"],
    index=0 if st.session_state.language == 'en' else 1
)
st.session_state.language = 'en' if language == "English" else 'mr'
lang = translations[st.session_state.language]

# Load models and scaler
try:
    exam_model = joblib.load('exam_model.pkl')
    attendance_model = joblib.load('attendance_model.pkl')
    scaler = joblib.load('scaler_exam.pkl')
except FileNotFoundError:
    st.error("Model or scaler files not found. Please ensure 'exam_model.pkl', 'attendance_model.pkl', and 'scaler_exam.pkl' are in the project directory.")
    st.stop()

# Prediction functions
def predict_exam_mark(previous_percentage, attendance, study_hours, commute_time, board_exam_marks, tuition_hours):
    # Define the feature names in the same order as during training
    feature_names = ['previous_percentage', 'attendance', 'study_hours', 'commute_time', 'board_exam_marks', 'tuition_hours']
    
    # Create a DataFrame with the input features
    features = pd.DataFrame(
        [[previous_percentage, attendance, study_hours, commute_time, board_exam_marks, tuition_hours]],
        columns=feature_names
    )
    
    # Scale the features
    features_scaled = scaler.transform(features)
    
    # Predict
    predicted_marks = exam_model.predict(features_scaled)[0]
    
    # Apply boosting logic
    if previous_percentage > 85 and attendance > 90:
        predicted_marks = min(predicted_marks * 1.1, 100)
    elif previous_percentage < 60 or attendance < 70:
        predicted_marks = max(predicted_marks * 0.9, 0)
    
    return predicted_marks

def predict_attendance(past_attendance, study_hours, commute_time):
    # Define the feature names in the same order as during training
    feature_names = ['past_attendance', 'study_hours', 'commute_time']
    
    # Create a DataFrame with the input features
    features = pd.DataFrame(
        [[past_attendance, study_hours, commute_time]],
        columns=feature_names
    )
    
    # Predict
    predicted_attendance = attendance_model.predict(features)[0]
    return max(0, min(predicted_attendance, 100))

# Signup function
def signup():
    st.subheader(lang["signup"])
    username = st.text_input(lang["username"], key="signup_username")
    email = st.text_input(lang["email"], key="signup_email")
    password = st.text_input(lang["password"], type="password", key="signup_password")
    confirm_password = st.text_input(lang["confirm_password"], type="password", key="signup_confirm_password")

    if st.button(lang["signup"]):
        if not username or not email or not password:
            st.error("Please fill in all fields.")
            return
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            st.error("Please enter a valid email address.")
            return
        if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[0-9]", password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            st.error("Password must be at least 8 characters long and include an uppercase letter, a number, and a special character.")
            return
        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        # Hash the password and proceed with signup
        hashed_password = hash_password(password)
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Users (username, password, email) VALUES (?, ?, ?)",
                    (username, hashed_password, email)
                )
                conn.commit()
                st.success("Signup successful! Please log in.")
            except pyodbc.IntegrityError:
                st.error("Username or email already exists.")
            except Exception as e:
                st.error(f"Error during signup: {e}")
            finally:
                conn.close()

# Login function
def login():
    st.subheader(lang["login"])
    username = st.text_input(lang["username"], key="login_username")
    password = st.text_input(lang["password"], type="password", key="login_password")

    if st.button(lang["login"]):
        if not username or not password:
            st.error("Please fill in all fields.")
            return

        # Verify user credentials
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, password FROM Users WHERE username = ?", (username,))
                user = cursor.fetchone()
                if user and verify_password(password, user[1]):
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            except Exception as e:
                st.error(f"Error during login: {e}")
            finally:
                conn.close()

# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.predictions_made = False
    st.session_state.predicted_marks = None
    st.session_state.predicted_attendance = None
    st.session_state.input_values = {}
    st.success("Logged out successfully!")
    st.rerun()

# Student profile management
def manage_student_profile():
    st.subheader(lang["student_profile"])
    
    # Custom CSS for styling the profile card
    st.markdown("""
        <style>
        .profile-header {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .profile-field {
            font-size: 16px;
            color: #34495e;
            margin: 5px 0;
        }
        .grade-box {
            background-color: #ecf0f1;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
        }
        .edit-button {
            background-color: #3498db;
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
        }
        .edit-button:hover {
            background-color: #2980b9;
        }
        .delete-button {
            background-color: #e74c3c;
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
        }
        .delete-button:hover {
            background-color: #c0392b;
        }
        </style>
    """, unsafe_allow_html=True)

    # Check if the user already has a profile
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM StudentProfiles WHERE user_id = ?", (st.session_state.user_id,))
    profile = cursor.fetchone()

    # Initialize session state for edit mode
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    if profile:
        # Calculate average CGPA and performance insights
        semester_grades = [min(max(float(profile[i+4]), 0.0), 10.0) for i in range(8)]  # Start at profile[4], clamp to [0.0, 10.0]
        completed_semesters = sum(1 for grade in semester_grades if grade > 0)
        average_cgpa = sum(semester_grades[:completed_semesters]) / completed_semesters if completed_semesters > 0 else 0
        highest_grade = max(semester_grades[:completed_semesters]) if completed_semesters > 0 else 0
        lowest_grade = min([g for g in semester_grades[:completed_semesters] if g > 0]) if completed_semesters > 0 else 0

        # Display profile in view mode
        if not st.session_state.edit_mode:
            st.markdown('<div class="profile-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="profile-header">{lang["student_profile"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="profile-field">Full Name: {profile[2]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="profile-field">Roll Number: {profile[3]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="profile-field">Semester Grades:</div>', unsafe_allow_html=True)
            
            # Display semester grades in a grid layout
            cols = st.columns(4)
            for i in range(8):
                with cols[i % 4]:
                    st.markdown(f'<div class="grade-box">Semester {i+1}: {semester_grades[i]}</div>', unsafe_allow_html=True)

            # Display average CGPA and insights
            st.markdown(f'<div class="profile-field">Average CGPA: {average_cgpa:.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="profile-field">Highest Semester Grade: {highest_grade:.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="profile-field">Lowest Semester Grade: {lowest_grade:.2f}</div>', unsafe_allow_html=True)

            # Performance trend
            if completed_semesters >= 2:
                differences = [semester_grades[i] - semester_grades[i-1] for i in range(1, completed_semesters)]
                avg_diff = sum(differences) / len(differences)
                if avg_diff > 0:
                    insight = lang["improving"]
                elif avg_diff < 0:
                    insight = lang["declining"]
                else:
                    insight = lang["inconsistent"]
                st.markdown(f'<div class="profile-field">Performance Trend: {insight}</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Progress toward a target CGPA (e.g., 8.0)
            target_cgpa = 8.0
            st.write("### Progress Toward Target CGPA (8.0)")
            progress = min(average_cgpa / target_cgpa, 1.0)
            st.progress(progress)
            st.write(f"Current CGPA: {average_cgpa:.2f} / Target CGPA: {target_cgpa}")

            # Semester-wise grade trend chart
            st.write("### Semester-Wise Grade Trend")
            df_grades = pd.DataFrame({
                "Semester": [f"Sem {i+1}" for i in range(8)],
                "Grade": semester_grades,
                "Type": ["Actual" if i < completed_semesters else "Not Completed" for i in range(8)]
            })
            fig_grades = px.line(df_grades, x="Semester", y="Grade", color="Type",
                                title="Semester-Wise Grade Trend", markers=True)
            st.plotly_chart(fig_grades)

            # Edit and Delete buttons
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Edit Profile", key="edit_profile"):
                    st.session_state.edit_mode = True
                    st.rerun()
            with col2:
                if st.button("Delete Profile", key="delete_profile"):
                    try:
                        cursor.execute("DELETE FROM StudentProfiles WHERE user_id = ?", (st.session_state.user_id,))
                        conn.commit()
                        st.success("Profile deleted successfully!")
                        st.session_state.edit_mode = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting profile: {e}")

        # Edit mode
        else:
            st.write("### Edit Your Profile")
            full_name = st.text_input("Full Name", value=profile[2])
            roll_number = st.text_input("Roll Number", value=profile[3])
            semester_grades = []
            st.write("Semester Grades:")
            cols = st.columns(4)
            for i in range(8):
                with cols[i % 4]:
                    grade = st.number_input(f"Semester {i+1} Grade", min_value=0.0, max_value=10.0, value=min(max(float(profile[i+4]), 0.0), 10.0), step=0.1)
                    semester_grades.append(grade)

            # Save and Cancel buttons
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Save Changes"):
                    try:
                        cursor.execute(
                            """
                            UPDATE StudentProfiles
                            SET full_name = ?, roll_number = ?, 
                                semester_1 = ?, semester_2 = ?, semester_3 = ?, semester_4 = ?,
                                semester_5 = ?, semester_6 = ?, semester_7 = ?, semester_8 = ?,
                                updated_at = GETDATE()
                            WHERE user_id = ?
                            """,
                            (full_name, roll_number, *semester_grades, st.session_state.user_id)
                        )
                        conn.commit()
                        st.success("Profile updated successfully!")
                        st.session_state.edit_mode = False
                        st.rerun()
                    except pyodbc.IntegrityError:
                        st.error("Roll number already exists.")
                    except Exception as e:
                        st.error(f"Error updating profile: {e}")
            with col2:
                if st.button("Cancel"):
                    st.session_state.edit_mode = False
                    st.rerun()

    else:
        # Create a new profile
        st.write("### Create Your Profile")
        full_name = st.text_input("Full Name")
        roll_number = st.text_input("Roll Number")
        semester_grades = []
        st.write("Semester Grades:")
        cols = st.columns(4)
        for i in range(8):
            with cols[i % 4]:
                grade = st.number_input(f"Semester {i+1} Grade", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
                semester_grades.append(grade)
        
        if st.button("Save Profile"):
            if not full_name or not roll_number:
                st.error("Please fill in all required fields.")
                return
            
            try:
                cursor.execute(
                    """
                    INSERT INTO StudentProfiles (user_id, full_name, roll_number, semester_1, semester_2,
                        semester_3, semester_4, semester_5, semester_6, semester_7, semester_8)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (st.session_state.user_id, full_name, roll_number, *semester_grades)
                )
                conn.commit()
                st.success("Profile created successfully!")
                st.rerun()
            except pyodbc.IntegrityError:
                                st.error("Roll number already exists.")
            except Exception as e:
                st.error(f"Error creating profile: {e}")
    
    conn.close()

# Predict Exam Marks feature
def predict_exam_marks():
    st.subheader(lang["predict_exam_marks"])
    
    # Cache the computation of the study hours chart
    @st.cache_data
    def compute_study_hours_chart(previous_percentage, past_attendance, commute_time, board_exam_marks, tuition_hours):
        hours_range = np.linspace(5, 20, 50)
        marks_range = [predict_exam_mark(previous_percentage, past_attendance, h, commute_time, board_exam_marks, tuition_hours) for h in hours_range]
        return hours_range, marks_range

    # Initialize session state variables
    if 'predictions_made' not in st.session_state:
        st.session_state.predictions_made = False
    if 'predicted_marks' not in st.session_state:
        st.session_state.predicted_marks = None
    if 'predicted_attendance' not in st.session_state:
        st.session_state.predicted_attendance = None
    if 'input_values' not in st.session_state:
        st.session_state.input_values = {}

    # Use a form to group inputs and reduce page refreshes
    with st.form(key="prediction_form"):
        previous_percentage = st.number_input(lang["previous_percentage"], min_value=50.0, max_value=95.0, value=75.0, step=0.1)
        past_attendance = st.number_input(lang["past_attendance"], min_value=60.0, max_value=100.0, value=85.0, step=0.1)
        study_hours = st.number_input(lang["study_hours"], min_value=5.0, max_value=20.0, value=10.0, step=0.1)
        commute_time = st.number_input(lang["commute_time"], min_value=0.0, max_value=2.0, value=0.5, step=0.1)
        board_exam_marks = st.number_input(lang["board_exam_marks"], min_value=60.0, max_value=95.0, value=80.0, step=0.1)
        tuition_hours = st.number_input(lang["tuition_hours"], min_value=0.0, max_value=10.0, value=5.0, step=0.1)
        submit_button = st.form_submit_button(lang["predict_button"])

    # Add a placeholder message
    if not st.session_state.predictions_made:
        st.info("Enter your details and click 'Predict' to see your predicted exam marks and attendance.")

    if submit_button:
        # Store input values in session state
        st.session_state.input_values = {
            'previous_percentage': previous_percentage,
            'past_attendance': past_attendance,
            'study_hours': study_hours,
            'commute_time': commute_time,
            'board_exam_marks': board_exam_marks,
            'tuition_hours': tuition_hours
        }

        # Predict exam marks and attendance
        predicted_marks = predict_exam_mark(
            previous_percentage, past_attendance, study_hours, commute_time, board_exam_marks, tuition_hours
        )
        predicted_attendance = predict_attendance(past_attendance, study_hours, commute_time)

        # Store predictions in session state
        st.session_state.predicted_marks = predicted_marks
        st.session_state.predicted_attendance = predicted_attendance
        st.session_state.predictions_made = True
        st.rerun()

    # Display predictions and related sections if predictions have been made
    if st.session_state.predictions_made:
        # Retrieve input values and predictions from session state
        previous_percentage = st.session_state.input_values['previous_percentage']
        past_attendance = st.session_state.input_values['past_attendance']
        study_hours = st.session_state.input_values['study_hours']
        commute_time = st.session_state.input_values['commute_time']
        board_exam_marks = st.session_state.input_values['board_exam_marks']
        tuition_hours = st.session_state.input_values['tuition_hours']
        predicted_marks = st.session_state.predicted_marks
        predicted_attendance = st.session_state.predicted_attendance

        # Display predictions
        st.write(lang["predicted_marks"].format(predicted_marks))
        st.write(lang["predicted_attendance"].format(predicted_attendance))

        # Gauge charts for predicted marks and attendance
        col1, col2 = st.columns(2)
        with col1:
            fig_marks = go.Figure(go.Indicator(
                mode="gauge+number",
                value=predicted_marks,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Predicted Exam Marks (%)"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 40], 'color': "red"},
                        {'range': [40, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': 40
                    }
                }
            ))
            st.plotly_chart(fig_marks, use_container_width=True)

        with col2:
            fig_attendance = go.Figure(go.Indicator(
                mode="gauge+number",
                value=predicted_attendance,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Predicted Attendance (%)"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 75], 'color': "red"},
                        {'range': [75, 85], 'color': "yellow"},
                        {'range': [85, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': 75
                    }
                }
            ))
            st.plotly_chart(fig_attendance, use_container_width=True)

        # Feature importance
        feature_importance = pd.DataFrame({
            'Feature': ['Previous Percentage', 'Attendance', 'Study Hours', 'Commute Time', 'Board Exam Marks', 'Tuition Hours'],
            'Importance': exam_model.feature_importances_
        })
        fig_importance = px.bar(feature_importance, x='Importance', y='Feature', title="Feature Importance for Exam Marks Prediction")
        st.plotly_chart(fig_importance)

        # Goal setting
        st.write("### Set Your Goals")
        target_marks = st.number_input(lang["target_exam_marks"], min_value=0.0, max_value=100.0, value=85.0, step=0.1)
        target_attendance = st.number_input(lang["target_attendance"], min_value=0.0, max_value=100.0, value=90.0, step=0.1)

        # Progress bars
        st.write("Progress Toward Goals")
        st.progress(min(predicted_marks / target_marks, 1.0) if target_marks > 0 else 0)
        st.write(f"Exam Marks: {predicted_marks:.1f}% / {target_marks}%")
        st.progress(min(predicted_attendance / target_attendance, 1.0) if target_attendance > 0 else 0)
        st.write(f"Attendance: {predicted_attendance:.1f}% / {target_attendance}%")

        # Study tips
        st.write("### " + lang["study_tips"])
        tips = []
        if study_hours < 15:
            tips.append(lang["tip_low_study_hours"])
        if predicted_attendance < 75:
            tips.append(lang["tip_low_attendance"])
        if predicted_marks < 40:
            tips.append(lang["tip_low_marks"])
        if commute_time > 1.5:
            tips.append(lang["tip_high_commute"])
        if not tips:
            tips.append("You're on the right track! Keep up the good work.")
        for tip in tips:
            st.write(f"- {tip}")

        # Explore impact of study hours
        st.write("### " + lang["explore_study_hours"])
        explore_hours = st.slider("Study Hours", min_value=5.0, max_value=20.0, value=study_hours, step=0.1)
        explore_marks = predict_exam_mark(previous_percentage, past_attendance, explore_hours, commute_time, board_exam_marks, tuition_hours)
        
        # Predicted marks vs study hours chart
        hours_range, marks_range = compute_study_hours_chart(previous_percentage, past_attendance, commute_time, board_exam_marks, tuition_hours)
        fig_study_hours = px.line(x=hours_range, y=marks_range, labels={'x': 'Study Hours per Week', 'y': 'Predicted Marks (%)'},
                                 title="Predicted Marks vs. Study Hours")
        fig_study_hours.add_scatter(x=[explore_hours], y=[explore_marks], mode='markers', marker=dict(size=15, color='red'), name='Current Prediction')
        st.plotly_chart(fig_study_hours)

        # Save predictions to profile
        if st.button("Save Predictions to Profile"):
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE StudentProfiles
                        SET predicted_exam_marks = ?, predicted_attendance = ?, updated_at = GETDATE()
                        WHERE user_id = ?
                        """,
                        (predicted_marks, predicted_attendance, st.session_state.user_id)
                    )
                    conn.commit()
                    st.success("Predictions saved to profile successfully!")
                    logging.info(f"User {st.session_state.user_id} saved predictions: marks={predicted_marks}, attendance={predicted_attendance}")
                except Exception as e:
                    logging.error(f"Error saving predictions to profile: {e}")
                    st.error(f"Error saving predictions to profile: {e}")
                finally:
                    conn.close()

        # Reset predictions
        if st.button("Reset Predictions"):
            st.session_state.predictions_made = False
            st.session_state.predicted_marks = None
            st.session_state.predicted_attendance = None
            st.session_state.input_values = {}
            st.rerun()

# Calculate CGPA/Percentage Goal feature
def calculate_cgpa():
    st.subheader(lang["calculate_cgpa"])
    
    # Grading scale selection
    grading_scale = st.selectbox(lang["grading_scale"], [lang["cgpa"], lang["percentage"]])
    is_cgpa = grading_scale == lang["cgpa"]
    max_value = 10.0 if is_cgpa else 100.0
    step = 0.1 if is_cgpa else 0.5

    # Credits per semester
    credits_per_semester = st.number_input(lang["credits_per_semester"], min_value=1, max_value=30, value=20)

    # Semester grades input
    st.write(lang["semester_grades"])
    semester_grades = []
    cols = st.columns(4)
    for i in range(8):
        with cols[i % 4]:
            grade = st.number_input(f"Semester {i+1}", min_value=0.0, max_value=max_value, value=0.0, step=step)
            semester_grades.append(grade)

    # Calculate completed semesters (moved outside the button block)
    completed_semesters = sum(1 for grade in semester_grades if grade > 0)

    # Target CGPA/Percentage
    target = st.number_input(lang["target_cgpa"], min_value=0.0, max_value=max_value, value=8.0 if is_cgpa else 80.0, step=step)

    if st.button(lang["calculate_button"]):
        if completed_semesters == 0:
            st.error("Please enter at least one semester grade.")
            return

        if completed_semesters == 8:
            st.write(lang["all_semesters_completed"])
            final_cgpa = sum(semester_grades) / 8
            st.write(f"Final {grading_scale}: {final_cgpa:.2f}")
        else:
            remaining_semesters = 8 - completed_semesters
            current_total = sum(grade * credits_per_semester for grade in semester_grades[:completed_semesters])
            required_total = target * 8 * credits_per_semester
            required_remaining = required_total - current_total
            required_avg = round(required_remaining / (remaining_semesters * credits_per_semester), 2) if remaining_semesters > 0 else 0

            # # Debug output
            # st.write(f"Debug: completed_semesters = {completed_semesters}, remaining_semesters = {remaining_semesters}")
            # st.write(f"Debug: current_total = {current_total}, required_total = {required_total}, required_remaining = {required_remaining}")
            # st.write(f"Debug: required_avg = {required_avg}, max_value = {max_value}")

            if required_avg > max_value:
                st.error(f"Target is not achievable. Required average ({required_avg:.2f}) exceeds maximum possible value ({max_value}).")
            elif required_avg < 0:
                st.success("You have already exceeded your target!")
            else:
                st.write(lang["required_average"].format(required_avg))

    # Progress toward target
    st.write("### " + lang["progress_toward_target"])
    current_avg = sum(semester_grades[:completed_semesters]) / completed_semesters if completed_semesters > 0 else 0
    progress = min(current_avg / target, 1.0) if target > 0 else 0  # Avoid division by zero
    st.progress(progress)
    st.write(f"Current {grading_scale}: {current_avg:.2f} / Target: {target}")

    # Semester-wise progress chart
    st.write("### " + lang["semester_wise_progress"])
    df_progress = pd.DataFrame({
        "Semester": [f"Sem {i+1}" for i in range(8)],
        grading_scale: semester_grades,
        "Type": ["Actual" if i < completed_semesters else "Not Completed" for i in range(8)]
    })
    fig_progress = px.line(df_progress, x="Semester", y=grading_scale, color="Type",
                          title="Semester-Wise Progress", markers=True)
    fig_progress.add_hline(y=target, line_dash="dash", line_color="red", annotation_text="Target")
    st.plotly_chart(fig_progress)

    # Performance insight
    if completed_semesters >= 2:
        differences = [semester_grades[i] - semester_grades[i-1] for i in range(1, completed_semesters)]
        avg_diff = sum(differences) / len(differences)
        if avg_diff > 0:
            insight = lang["improving"]
        elif avg_diff < 0:
            insight = lang["declining"]
        else:
            insight = lang["inconsistent"]
        st.write(lang["performance_insight"].format(insight))

    # What-if analysis
    st.write("### " + lang["what_if_analysis"])
    hypothetical_grades = []
    st.write(lang["hypothetical_grades"])
    cols = st.columns(4)
    for i in range(completed_semesters, 8):
        with cols[i % 4]:
            grade = st.number_input(f"Semester {i+1} (Hypothetical)", min_value=0.0, max_value=max_value, value=0.0, step=step)
            hypothetical_grades.append(grade)

    if st.button(lang["calculate_projected"]):
        all_grades = semester_grades[:completed_semesters] + hypothetical_grades
        projected_cgpa = sum(all_grades) / 8
        st.write(lang["projected_cgpa"].format(projected_cgpa))

    # Option to save grades to profile
    if st.button(lang["save_to_profile"]):
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    IF EXISTS (SELECT 1 FROM StudentProfiles WHERE user_id = ?)
                        UPDATE StudentProfiles
                        SET semester_1 = ?, semester_2 = ?, semester_3 = ?, semester_4 = ?,
                            semester_5 = ?, semester_6 = ?, semester_7 = ?, semester_8 = ?,
                            updated_at = GETDATE()
                        WHERE user_id = ?
                    ELSE
                        INSERT INTO StudentProfiles (user_id, full_name, roll_number, semester_1, semester_2,
                            semester_3, semester_4, semester_5, semester_6, semester_7, semester_8)
                        VALUES (?, 'Unknown', 'Unknown', ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (st.session_state.user_id, *semester_grades, st.session_state.user_id,
                     st.session_state.user_id, *semester_grades)
                )
                conn.commit()
                st.success("Grades saved to profile successfully!")
            except Exception as e:
                st.error(f"Error saving grades to profile: {e}")
            finally:
                conn.close()

def compare_scores():
    st.subheader(lang["compare_scores"])

    # Check if the user has a profile
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM StudentProfiles WHERE user_id = ?", (st.session_state.user_id,))
    user_profile = cursor.fetchone()

    if not user_profile:
        st.warning("Please create your student profile to compare scores.")
        conn.close()
        return

    # Get user's semester grades and average CGPA
    user_semester_grades = [min(max(float(user_profile[i+4]), 0.0), 10.0) for i in range(8)]
    user_completed_semesters = sum(1 for grade in user_semester_grades if grade > 0)
    user_average_cgpa = sum(user_semester_grades[:user_completed_semesters]) / user_completed_semesters if user_completed_semesters > 0 else 0

    # Get predicted marks and attendance from session state (if available)
    user_predicted_marks = st.session_state.get('predicted_marks', None)
    user_predicted_attendance = st.session_state.get('predicted_attendance', None)

    if user_predicted_marks is None or user_predicted_attendance is None:
        st.warning("Please use the 'Predict Exam Marks' feature to get your predicted marks and attendance for comparison.")
        conn.close()
        return

    # Fetch all student profiles to compute class averages and top performer
    cursor.execute("SELECT * FROM StudentProfiles")
    all_profiles = cursor.fetchall()

    if len(all_profiles) <= 1:
        st.warning("Not enough student profiles to compare. At least two profiles are needed.")
        conn.close()
        return

    # Compute predicted marks and attendance for comparison
    all_predicted_marks = [profile[13] for profile in all_profiles if profile[13] is not None]  # Assuming predicted_exam_marks is the 14th column (index 13)
    all_predicted_attendance = [profile[14] for profile in all_profiles if profile[14] is not None]  # Assuming predicted_attendance is the 15th column (index 14)

    class_avg_predicted_marks = sum(all_predicted_marks) / len(all_predicted_marks) if all_predicted_marks else 0
    top_predicted_marks = max(all_predicted_marks) if all_predicted_marks else 0

    class_avg_predicted_attendance = sum(all_predicted_attendance) / len(all_predicted_attendance) if all_predicted_attendance else 0
    top_predicted_attendance = max(all_predicted_attendance) if all_predicted_attendance else 0

    # Compute class averages and top performer for semester grades
    all_semester_grades = [[min(max(float(profile[i+4]), 0.0), 10.0) for i in range(8)] for profile in all_profiles]
    class_avg_semester_grades = []
    for sem in range(8):
        sem_grades = [grades[sem] for grades in all_semester_grades if grades[sem] > 0]
        class_avg_semester_grades.append(sum(sem_grades) / len(sem_grades) if sem_grades else 0)

    # Compute average CGPA for each student
    all_average_cgpas = []
    for grades in all_semester_grades:
        completed_semesters = sum(1 for grade in grades if grade > 0)
        avg_cgpa = sum(grades[:completed_semesters]) / completed_semesters if completed_semesters > 0 else 0
        all_average_cgpas.append(avg_cgpa)

    class_avg_cgpa = sum(all_average_cgpas) / len(all_average_cgpas) if all_average_cgpas else 0
    top_performer_cgpa = max(all_average_cgpas) if all_average_cgpas else 0

    # Top performer's semester grades
    top_performer_index = all_average_cgpas.index(top_performer_cgpa)
    top_performer_semester_grades = all_semester_grades[top_performer_index]

    # 1. Semester Grades Comparison (Line Chart)
    st.write("### " + lang["semester_grades_comparison"])
    df_comparison = pd.DataFrame({
        "Semester": [f"Sem {i+1}" for i in range(8)],
        lang["your_scores"]: user_semester_grades,
        lang["class_average"]: class_avg_semester_grades,
        lang["top_performer"]: top_performer_semester_grades
    })
    fig_grades = px.line(df_comparison, x="Semester", y=[lang["your_scores"], lang["class_average"], lang["top_performer"]],
                         title="Semester Grades Comparison", markers=True)
    st.plotly_chart(fig_grades)

    # 2. Average CGPA Comparison (Bar Chart)
    st.write("### " + lang["cgpa_comparison"])
    df_cgpa = pd.DataFrame({
        "Category": [lang["your_scores"], lang["class_average"], lang["top_performer"]],
        "Average CGPA": [user_average_cgpa, class_avg_cgpa, top_performer_cgpa]
    })
    fig_cgpa = px.bar(df_cgpa, x="Category", y="Average CGPA", title="Average CGPA Comparison", color="Category")
    st.plotly_chart(fig_cgpa)

    # 3. Predicted Exam Marks Comparison (Bar Chart)
    st.write("### " + lang["predicted_marks_comparison"])
    df_marks = pd.DataFrame({
        "Category": [lang["your_scores"], lang["class_average"], lang["top_performer"]],
        "Predicted Exam Marks (%)": [user_predicted_marks, class_avg_predicted_marks, top_predicted_marks]
    })
    fig_marks = px.bar(df_marks, x="Category", y="Predicted Exam Marks (%)", title="Predicted Exam Marks Comparison", color="Category")
    st.plotly_chart(fig_marks)

    # 4. Predicted Attendance Comparison (Bar Chart)
    st.write("### " + lang["predicted_attendance_comparison"])
    df_attendance = pd.DataFrame({
        "Category": [lang["your_scores"], lang["class_average"], lang["top_performer"]],
        "Predicted Attendance (%)": [user_predicted_attendance, class_avg_predicted_attendance, top_predicted_attendance]
    })
    fig_attendance = px.bar(df_attendance, x="Category", y="Predicted Attendance (%)", title="Predicted Attendance Comparison", color="Category")
    st.plotly_chart(fig_attendance)

    # 5. Comparison Insights
    st.write("### " + lang["comparison_insights"])
    insights = []

    # CGPA Insights
    if user_average_cgpa < class_avg_cgpa:
        insights.append(lang["below_class_average"].format(
            metric="Average CGPA", value=user_average_cgpa, avg=class_avg_cgpa, suggestion="improving your study habits"
        ))
    else:
        insights.append(lang["above_class_average"].format(
            metric="Average CGPA", value=user_average_cgpa, avg=class_avg_cgpa
        ))

    if user_average_cgpa < top_performer_cgpa:
        insights.append(lang["below_top_performer"].format(
            metric="Average CGPA", value=user_average_cgpa, top=top_performer_cgpa, suggestion="increasing your study hours or seeking help in weaker subjects"
        ))

    # Predicted Marks Insights
    if user_predicted_marks < class_avg_predicted_marks:
        insights.append(lang["below_class_average"].format(
            metric="Predicted Exam Marks", value=user_predicted_marks, avg=class_avg_predicted_marks, suggestion="improving your study habits"
        ))
    else:
        insights.append(lang["above_class_average"].format(
            metric="Predicted Exam Marks", value=user_predicted_marks, avg=class_avg_predicted_marks
        ))

    if user_predicted_marks < top_predicted_marks:
        insights.append(lang["below_top_performer"].format(
            metric="Predicted Exam Marks", value=user_predicted_marks, top=top_predicted_marks, suggestion="increasing your study hours"
        ))

    # Predicted Attendance Insights
    if user_predicted_attendance < class_avg_predicted_attendance:
        insights.append(lang["below_class_average"].format(
            metric="Predicted Attendance", value=user_predicted_attendance, avg=class_avg_predicted_attendance, suggestion="attending more classes"
        ))
    else:
        insights.append(lang["above_class_average"].format(
            metric="Predicted Attendance", value=user_predicted_attendance, avg=class_avg_predicted_attendance
        ))

    if user_predicted_attendance < top_predicted_attendance:
        insights.append(lang["below_top_performer"].format(
            metric="Predicted Attendance", value=user_predicted_attendance, top=top_predicted_attendance, suggestion="improving your attendance consistency"
        ))

    # Semester Grades Insights (find the weakest semester compared to class average)
    weakest_semester = None
    max_diff = 0
    for i in range(user_completed_semesters):
        diff = class_avg_semester_grades[i] - user_semester_grades[i]
        if diff > max_diff:
            max_diff = diff
            weakest_semester = i + 1

    if weakest_semester and max_diff > 0:
        insights.append(f"Your grade in Semester {weakest_semester} ({user_semester_grades[weakest_semester-1]:.2f}) is significantly below the class average ({class_avg_semester_grades[weakest_semester-1]:.2f}). Focus on improving in this semester.")

    # Display insights
    if insights:
        for insight in insights:
            st.write(f"- {insight}")
    else:
        st.write("No specific insights available at this time.")

    conn.close()

# Main app logic
def main_app():
    st.title(lang["welcome_message"])
    
    # Sidebar for feature selection
    feature = st.sidebar.selectbox(
        lang["select_feature"],
        [lang["student_profile"], lang["predict_exam_marks"], lang["calculate_cgpa"], lang["compare_scores"], lang["logout"]]
    )
    
    if feature == lang["student_profile"]:
        manage_student_profile()
    elif feature == lang["predict_exam_marks"]:
        predict_exam_marks()
    elif feature == lang["calculate_cgpa"]:
        calculate_cgpa()
    elif feature == lang["compare_scores"]:
        compare_scores()
    elif feature == lang["logout"]:
        logout()

# App entry point
def app():
    if not st.session_state.logged_in:
        action = st.sidebar.radio("Choose an action", [lang["login"], lang["signup"]])
        if action == lang["login"]:
            login()
        else:
            signup()
    else:
        main_app()

if __name__ == "__main__":
    app()