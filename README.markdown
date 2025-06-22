# Student Performance Prediction & CGPA Calculator

## Overview
The **Student Performance Prediction & CGPA Calculator** is a web-based application developed by me to assist students in tracking their academic performance, predicting exam marks and attendance using machine learning, calculating CGPA goals, and comparing scores with peers. Built with Streamlit, SQL Server (DYPATU_StudentDB), Python, RandomForest models, and Plotly visualizations, this project supports multilingual functionality (English and Marathi).

- **Technologies**: Streamlit, SQL Server, Python, RandomForest, Plotly
- **Timeline**: June 2025 – Present
- **Developer**: Ruturaj (sole contributor)

## Features
- **Student Profile Management**: Add, edit, and delete personal details (full name, roll number) and semester grades, with a visual grade trend chart.
- **Exam Marks Prediction**: Predict exam marks and attendance based on study habits (e.g., study hours, commute time) using pre-trained RandomForest models.
- **CGPA Goal Calculation**: Input target CGPA and hypothetical grades for future semesters, with a comparison chart.
- **Score Comparison**: Compare your grades and predictions with class averages and top performers using interactive charts.
- **Multilingual Support**: Switch between English and Marathi for a personalized experience.

## Project Structure
- `app.py`: Main application code with Streamlit UI and database integration.
- `languages.py`: Dictionary containing text translations for English and Marathi.
- `models/`: Directory with pre-trained models (`exam_model.pkl`, `attendance_model.pkl`, `scaler_exam.pkl`).
- `database.sql`: SQL script to create the `DYPATU_StudentDB` schema.
- `generate_data.py`: Script to generate synthetic student data for testing.
- `train_models.py`: Script to train the RandomForest models with sample data.
- `test_app.py`: Unit tests for predictions and database operations.
- `requirements.txt`: List of Python dependencies.
- `.gitignore`: Excludes unnecessary files from Git.
- `README.md`: This documentation file.
- `images/`: Directory for local screenshots (optional, if hosted locally).

## Setup Instructions
### Prerequisites
- Python 3.9 or higher
- SQL Server 2019 or later with ODBC Driver 17
- Git (for version control)

### Installation Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/hriturajnarvekar27/Student-Performance-Prediction.git
   cd Student-Performance-Prediction
   ```
2. **Install Dependencies**:
   - Create a virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     ```
   - Install required packages:
     ```bash
     pip install -r requirements.txt
     ```
3. **Set Up Database**:
   - Install SQL Server and configure it with a local instance (e.g., `localhost`).
   - Create the `DYPATU_StudentDB` database:
     ```sql
     CREATE DATABASE DYPATU_StudentDB;
     ```
   - Run `database.sql` to set up tables:
     ```bash
     sqlcmd -S localhost -U student_app_user -P Student@2025! -d DYPATU_StudentDB -i database.sql
     ```
   - Update the connection string in `app.py` (in `get_db_connection()`) with your SQL Server credentials if different.
4. **Generate Sample Data** (Optional):
   - Run the data generation script:
     ```bash
     python generate_data.py
     ```
5. **Run the Application**:
   - Start the Streamlit app:
     ```bash
     streamlit run app.py
     ```
   - Access it at `http://localhost:8501`.

## Usage Guide
### Launching the App
- Open the app in your browser after running `streamlit run app.py`.
- Log in with a username and password (initially use "admin" and "Admin@2025!"—change this in the database after first login).

### Navigating Sections
1. **Student Profile**:
   - Enter your full name, roll number, and semester grades (0-10 scale).
   - Save or delete your profile to view a grade trend chart.
2. **Predict Exam Marks**:
   - Input previous percentage, past attendance, study hours, commute time, board exam marks, and tuition hours.
   - View predicted marks and attendance gauges, feature importance bar chart, and study hours impact line chart.
3. **Calculate CGPA**:
   - Set a target CGPA (0-10) and enter hypothetical grades for remaining semesters.
   - See a comparison bar chart of current, target, and projected CGPA.
4. **Compare Scores**:
   - View line and bar charts comparing your grades, class average, and top performer based on database data.

### Language Switching
- Use the sidebar dropdown to switch between English and Marathi.
- All text updates dynamically based on the selected language.

## Screenshots
1. **Student Profile Section**
   - ![Student Profile Screenshot](https://github.com/hriturajnarvekar27/Student-Performance-Prediction/blob/main/Screenshots/Screenshot%202025-06-22%20194750.png)
     - *Description*: Displays the profile form with fields for name, roll number, and semester grades, plus a green line chart showing grade trends.
2. **Predict Exam Marks Section**
   - ![Predict Exam Marks Screenshot](https://github.com/hriturajnarvekar27/Student-Performance-Prediction/blob/main/Screenshots/Screenshot%202025-06-22%20194927.png)
     - *Description*: Shows input fields, two gauges (marks and attendance), a feature importance bar chart, and a red line chart for study hours impact.
     - *Note*: Replace with the actual URL or filename of your screenshot for this section.
3. **Calculate CGPA Section**
   - ![Calculate CGPA Screenshot](https://github.com/hriturajnarvekar27/Student-Performance-Prediction/blob/main/Screenshots/Screenshot%202025-06-22%20195204.png)
     - *Description*: Includes a target CGPA input, hypothetical grade form, and a multi-colored bar chart comparing CGPA values.
     - *Note*: Replace with the actual URL or filename of your screenshot for this section.
4. **Compare Scores Section**
   - ![Compare Scores Screenshot](https://github.com/hriturajnarvekar27/Student-Performance-Prediction/blob/main/Screenshots/Screenshot%202025-06-22%20201708.png)
     - *Description*: Features a line chart for semester grades and bar charts for CGPA, predicted marks, and attendance comparisons.
     - *Note*: Replace with the actual URL or filename of your screenshot for this section.

*Note*: The provided URL (Screenshot 2025-06-22 194750.png) is used for the Student Profile section. Upload additional screenshots for the other sections to the `Screenshots/` directory on GitHub (e.g., `Screenshot 2025-06-22 194800.png`, `Screenshot 2025-06-22 194830.png`, `Screenshot 2025-06-22 194900.png`) and update the URLs accordingly. Ensure the filenames match the timestamps or rename them for clarity (e.g., `predict_exam_marks.png`).

## Testing
- Run tests with:
  ```bash
  pytest test_app.py
  ```
- Tests validate:
  - Prediction accuracy within expected ranges (0-100 for marks, 0-100 for attendance).
  - Database operations (insert, update, delete in `DYPATU_StudentDB`).
  - Language switching functionality.
- Check `app.log` for errors during testing.

## Troubleshooting
- **Database Connection Error**:
  - Ensure SQL Server is running and the connection string in `app.py` matches your setup.
  - Verify `student_app_user` and password (`Student@2025!`) are correct in SQL Server.
- **Module Not Found**:
  - Reinstall dependencies with `pip install -r requirements.txt`.
- **Model Loading Failure**:
  - Ensure `models/` contains `exam_model.pkl`, `attendance_model.pkl`, and `scaler_exam.pkl`. Regenerate with `train_models.py` if missing.
- **Streamlit Not Starting**:
  - Check port 8501 is free; use `streamlit run app.py --server.port 8502` if needed.

## Deployment
### Local Deployment
- Host on a local machine with SQL Server installed.
- Use `ngrok` for public access if needed:
  ```bash
  ngrok http 8501
  ```

### Cloud Deployment
- **Streamlit Community Cloud**:
  - Push to GitHub, connect to Streamlit Cloud.
  - Use Azure SQL Database for `DYPATU_StudentDB` with environment variables for credentials.
- **Requirements**:
  - Update `requirements.txt` for cloud compatibility (e.g., add `pyodbc` with proper drivers).

## Future Improvements
- Add user authentication with password reset.
- Expand language support (e.g., Hindi).
- Integrate real-time data from an educational API.
- Enhance UI with more interactive elements (e.g., sliders for predictions).

## License
[MIT License](LICENSE) (create a `LICENSE` file with MIT terms if not present).
