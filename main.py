from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import uvicorn
from sklearn.linear_model import LinearRegression
from typing import List

app = FastAPI()

# Sample database (replace with PostgreSQL integration later)
students_db = {}

# Pydantic model for input
class StudentPerformance(BaseModel):
    student_id: str
    subject: str
    scores: List[int]
    attendance: float  # Percentage
    participation: float  # Engagement level (0-1 scale)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Function to detect learning gaps
def analyze_performance(scores: List[int]):
    if len(scores) < 2:
        return "Insufficient data"
    
    x = np.array(range(len(scores))).reshape(-1, 1)
    y = np.array(scores).reshape(-1, 1)
    model = LinearRegression().fit(x, y)
    trend = model.coef_[0][0]
    
    if trend < 0:
        return "Declining performance, needs attention"
    elif trend == 0:
        return "Stable, but no improvement"
    else:
        return "Improving performance"

# API to submit student data
@app.post("/submit_performance/")
def submit_performance(data: StudentPerformance):
    students_db[data.student_id] = data.dict()
    return {"message": "Student performance data saved successfully"}

# API to get student report
@app.get("/get_report/{student_id}")
def get_report(student_id: str):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student_data = students_db[student_id]
    learning_gap_analysis = analyze_performance(student_data['scores'])
    
    return {
        "student_id": student_id,
        "subject": student_data['subject'],
        "attendance": student_data['attendance'],
        "participation": student_data['participation'],
        "performance_trend": learning_gap_analysis
    }

# Run the server with: uvicorn filename:app --reload
