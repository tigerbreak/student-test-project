from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="学生管理系统")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 内存数据库（用于演示）
students_db = []
current_id = 1

# 数据模型
class Student(BaseModel):
    id: Optional[int] = None
    name: str
    age: int
    email: str
    major: str

class StudentCreate(BaseModel):
    name: str
    age: int
    email: str
    major: str

# API 路由
@app.get("/")
def read_root():
    return {"message": "欢迎使用学生管理系统 API"}

@app.get("/api/students", response_model=List[Student])
def get_students():
    """获取所有学生"""
    return students_db

@app.get("/api/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    """获取单个学生"""
    for student in students_db:
        if student["id"] == student_id:
            return student
    raise HTTPException(status_code=404, detail="学生不存在")

@app.post("/api/students", response_model=Student)
def create_student(student: StudentCreate):
    """创建新学生"""
    global current_id
    new_student = {
        "id": current_id,
        "name": student.name,
        "age": student.age,
        "email": student.email,
        "major": student.major
    }
    students_db.append(new_student)
    current_id += 1
    return new_student

@app.put("/api/students/{student_id}", response_model=Student)
def update_student(student_id: int, student: StudentCreate):
    """更新学生信息"""
    for i, s in enumerate(students_db):
        if s["id"] == student_id:
            students_db[i] = {
                "id": student_id,
                "name": student.name,
                "age": student.age,
                "email": student.email,
                "major": student.major
            }
            return students_db[i]
    raise HTTPException(status_code=404, detail="学生不存在")

@app.delete("/api/students/{student_id}")
def delete_student(student_id: int):
    """删除学生"""
    for i, s in enumerate(students_db):
        if s["id"] == student_id:
            students_db.pop(i)
            return {"message": "学生已删除"}
    raise HTTPException(status_code=404, detail="学生不存在")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
