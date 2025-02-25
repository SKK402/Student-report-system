import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from sqlalchemy import create_engine
from reportlab.pdfgen import canvas
from io import BytesIO

# Database connection
def get_data():
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            st.error("DATABASE_URL environment variable is not set.")
            return pd.DataFrame()
        
        engine = create_engine(DATABASE_URL)
        query = """
        SELECT students.student_id, students.name, subjects.name AS subject, marks.marks, marks.max_marks 
        FROM marks 
        JOIN students ON marks.student_id = students.student_id 
        JOIN subjects ON marks.subject_id = subjects.id;
        """

        with engine.connect() as conn:
            df = pd.read_sql(query, conn)

        if df.empty:
            st.error("No student data found! Please check the database.")
            return pd.DataFrame()
        
        return df
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return pd.DataFrame()

# AI-based analysis
def analyze_data(df):
    if df.empty:
        return df
    
    df['percentage'] = (df['marks'] / df['max_marks']) * 100
    df['grade'] = pd.cut(df['percentage'], bins=[0, 40, 60, 80, 100],
                         labels=['F', 'C', 'B', 'A'])

    def generate_recommendation(row):
        if row['percentage'] >= 80:
            return "🚀 Excellent performance! Keep up the great work!"
        elif row['percentage'] >= 60:
            return "✅ Good work, but try to improve further."
        elif row['percentage'] >= 40:
            return "📌 Needs improvement. Focus on weak areas."
        else:
            return "⚠️ Critical! Requires immediate attention."

    df['recommendation'] = df.apply(generate_recommendation, axis=1)
    return df

# Generate PDF report
def generate_pdf(student_data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 800, "Student Performance Report")
    
    y_position = 780
    pdf.setFont("Helvetica", 12)
    
    for index, row in student_data.iterrows():
        pdf.drawString(50, y_position, f"{row['name']} - {row['subject']} - {row['percentage']:.2f}% ({row['grade']})")
        
        # Wrap recommendation text to prevent overlap
        words = row['recommendation'].split()
        wrapped_text = ""
        line_length = 0

        for word in words:
            if line_length + len(word) + 1 > 80:  # Adjust max length per line
                pdf.drawString(50, y_position - 20, wrapped_text)
                y_position -= 20
                wrapped_text = word
                line_length = len(word)
            else:
                wrapped_text += " " + word
                line_length += len(word) + 1

        pdf.drawString(50, y_position - 20, wrapped_text)
        y_position -= 40

        # Prevent text from going off the page
        if y_position < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y_position = 780

    pdf.save()
    buffer.seek(0)
    return buffer

# Streamlit Dashboard
def dashboard(df):
    st.title("📊 Student Performance Dashboard")

    if df.empty:
        st.warning("No data available. Please check the database.")
        return

    # Ensure dropdown gets all students
    student_list = df['name'].astype(str).unique().tolist()
    st.write(f"Total Students: {len(student_list)}")  # Debugging check

    student = st.selectbox("Select Student", student_list)
    student_data = df[df['name'] == student]

    # Subject-wise Percentage Bar Chart
    st.subheader(f"Performance of {student}")
    fig, ax = plt.subplots()
    sns.barplot(x='subject', y='percentage', data=student_data, ax=ax)
    ax.set_ylabel("Percentage (%)")
    ax.set_xlabel("Subjects")
    ax.set_title(f"Performance of {student}")
    plt.xticks(rotation=45)  # Rotate for better readability
    st.pyplot(fig)

    # Display Data Table
    st.subheader("📋 Student Report Data")
    st.write(student_data)

    # Generate Report Button with Download
    if st.button("📄 Generate PDF Report"):
        pdf_buffer = generate_pdf(student_data)
        st.download_button(
            label="📥 Download PDF",
            data=pdf_buffer,
            file_name=f"{student}_report.pdf",
            mime="application/pdf"
        )

# Main execution
df = get_data()
if not df.empty:
    df = analyze_data(df)
    dashboard(df)
