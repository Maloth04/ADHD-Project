# AI-Enhanced ADHD Behavior Monitoring System

A Smart System for Tracking ADHD Symptoms, Cognitive Performance, and Behavioral Trends.

**Overview**
- The AI-Enhanced ADHD Behavior Monitoring System is a desktop application that allows users to record their daily ADHD-related symptoms and habits.
The system analyzes this data, generates visual trend graphs, evaluates cognitive performance, and provides automatic suggestions.
Once enough data is collected, the system also uses a machine learning model to predict future cognitive scores.

- This project demonstrates how machine learning, data visualization, and behavioral analysis can be combined to support ADHD monitoring and self-management.

**Features**
1. Daily ADHD Symptom Entry

Users record daily values such as:

- Focus
- Hyperactivity
- Impulsivity
- Sleep hours
- Distractions
- Tasks completed
- Mood
- Notes
- Screen time (newly added)

2. Cognitive Score Calculation

The system calculates a weighted cognitive performance score for each entry.

3. Machine Learning Predictions

After at least 5 entries are stored, the ML model predicts:

- Next-day cognitive score
- Screen time impact trends
- Focus trend estimation

4. Visual Trend Analysis

The application displays multiple graphs:

- Focus trend
- Cognitive score trend
- Screen time vs cognitive score
- Mood distribution

5. Smart Suggestions

Based on recorded data, the system provides personalized insights such as:

- Improving sleep
- Reducing screen time
- Managing distractions
- Enhancing productivity habits

6. Data Storage

All entries are saved in a local SQLite database using SQLAlchemy ORM.

7. Report Export

Users can export:

- Excel reports
- PDF summaries

**Tech Stack**

Language: Python 3.x

Libraries:

- Tkinter
- Matplotlib
- Pandas
- SQLAlchemy
- Scikit-learn
- FPDF
- OpenPyXL
- TkCalendar
- Win10Toast

Database: SQLite

**Project Structure**

ADHD-Project/
│
├── app.py                 # Main Tkinter application  
├── storage_sql.py         # Database models and CRUD operations  
├── viz.py                 # Graph generation functions  
├── ml_predict.py          # Machine learning model and predictions  
├── report.py              # Excel and PDF export logic  
├── adhd_app.db            # SQLite database (auto generated)  
├── README.md              # Project documentation  
└── venv/                  # Virtual environment  

**Installation and Setup**

1. Activate Virtual Environment
-- venv\Scripts\activate

2. Install Required Packages
-- pip install -r requirements.txt

3. Run the Application
-- python app.py

**How the System Works**

Step 1: Data Entry

The user enters daily symptoms and lifestyle metrics.

Step 2: Data Storage

All information is saved in a structured SQLite database.

Step 3: Score Calculation

A cognitive score is computed using weighted inputs.

Step 4: Graph Visualization

The application generates visual charts showing performance trends across days.

Step 5: AI Prediction

Once sufficient data is available, the ML model predicts future cognitive performance.

**Machine Learning Model**

Algorithm: Linear Regression

Input Features:

- Focus
- Sleep
- Tasks completed
- Screen time

Output: Cognitive score prediction

The model automatically retrains when new data is added.

**Use Cases**

- ADHD monitoring
- Academic projects
- Behavioral research
- Data visualization and ML demonstration
- Mental health tracking systems

**Future Enhancements**

- Mobile app version
- Cloud data syncing
- Automated weekly reports
- Chat-based AI suggestions
- Voice-based emotional analysis
- Real-time notifications and reminders

**Conclusion**

The AI-Enhanced ADHD Monitoring System provides a structured way to record daily symptoms, analyze behavioral patterns, and receive insights based on machine learning.
It demonstrates a complete pipeline that combines data input, database storage, analytics, AI prediction, and reporting.
This system can be expanded further as a practical support tool for mental health tracking.
