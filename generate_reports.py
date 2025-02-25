import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from sqlalchemy import create_engine
from reportlab.pdfgen import canvas

# Database connection
def get_data():
    engine = create_engine("postgresql://postgres:Sk123@localhost:5432/student_report_system")

    query = """
    SELECT students.id, students.name, subjects.name AS subject, marks.marks, marks.max_marks
    FROM marks
    JOIN students ON marks.student_id = students.id
    JOIN subjects ON marks.subject_id = subjects.id
    """
    df = pd.read_sql(query, engine)
    return df

# Performance analysis
def analyze_performance(df):
    df["percentage"] = (df["marks"] / df["max_marks"]) * 100
    df["status"] = np.where(df["percentage"] >= 40, "Pass", "Fail")
    return df

# Generate PDF report
def generate_pdf(student_name, df):
    folder = "reports"
    if not os.path.exists(folder):
        os.makedirs(folder)  # Create the folder if it doesn't exist
    
    pdf_path = os.path.join(folder, f"{student_name}_report.pdf")
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 800, f"Report for {student_name}")

    y_position = 780
    for _, row in df.iterrows():
        text = f"{row['subject']}: {row['marks']} / {row['max_marks']} ({row['percentage']:.2f}%)"
        c.drawString(100, y_position, text)
        y_position -= 20  # Move down for the next subject
    
    c.save()
    return pdf_path

# Streamlit Dashboard
def main():
    st.title("Student Performance Dashboard")

    df = get_data()
    df = analyze_performance(df)

    st.write("### Student Performance Data")
    st.dataframe(df)

    st.write("### Performance Visualization")
    student_list = df["name"].unique()
    student_name = st.selectbox("Select Student", student_list)
    
    student_df = df[df["name"] == student_name]
    
    if not student_df.empty:
        fig, ax = plt.subplots()
        ax.bar(student_df["subject"], student_df["percentage"], color="skyblue")
        ax.axhline(40, color="red", linestyle="--", label="Pass Mark (40%)")
        ax.set_xlabel("Subjects")
        ax.set_ylabel("Percentage")
        ax.set_title(f"{student_name}'s Performance")
        ax.legend()
        st.pyplot(fig)

        if st.button("Generate PDF Report"):
            pdf_path = generate_pdf(student_name, student_df)
            st.success(f"Report generated: {pdf_path}")
    else:
        st.warning("No data available for the selected student.")

if __name__ == "__main__":
    main()
