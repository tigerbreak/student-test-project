from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import random

app = FastAPI(title="学生管理系统")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全认证
security = HTTPBearer(auto_error=False)

# 内存数据库（用于演示）
students_db = []
current_id = 1

# Mock 数据 - 权限管理
roles_db = [
    {"id": 1, "name": "学生", "permissions": ["view_grades", "view_schedule", "view_balance"]},
    {"id": 2, "name": "教师", "permissions": ["view_grades", "edit_grades", "view_schedule", "manage_courses"]},
    {"id": 3, "name": "管理员", "permissions": ["*"]}
]
users_db = [
    {"id": 1, "username": "student1", "role_id": 1, "email": "student1@school.edu"},
    {"id": 2, "username": "teacher1", "role_id": 2, "email": "teacher1@school.edu"},
    {"id": 3, "username": "admin", "role_id": 3, "email": "admin@school.edu"}
]

# Mock 数据 - 课程表
courses_db = [
    {"id": 1, "name": "高等数学", "teacher": "张教授", "time": "周一 8:00-9:40", "location": "A101", "credits": 4},
    {"id": 2, "name": "大学英语", "teacher": "李老师", "time": "周二 10:00-11:40", "location": "B205", "credits": 3},
    {"id": 3, "name": "计算机基础", "teacher": "王博士", "time": "周三 14:00-15:40", "location": "C301", "credits": 3},
    {"id": 4, "name": "数据结构", "teacher": "赵教授", "time": "周四 8:00-9:40", "location": "A102", "credits": 4},
    {"id": 5, "name": "体育", "teacher": "孙教练", "time": "周五 16:00-17:40", "location": "操场", "credits": 2}
]

# Mock 数据 - 饭卡余额
card_balance_db = {
    "student1": {"balance": 156.50, "last_recharge": "2024-01-15", "status": "active"},
    "student2": {"balance": 89.20, "last_recharge": "2024-01-10", "status": "active"},
    "teacher1": {"balance": 234.80, "last_recharge": "2024-01-18", "status": "active"}
}

# Mock 数据 - 学校日志
school_logs_db = [
    {"id": 1, "type": "通知", "title": "春季学期开学通知", "content": "2024 年春季学期将于 2 月 26 日正式开学", "date": "2024-01-20", "priority": "high"},
    {"id": 2, "type": "活动", "title": "校园招聘会", "content": "将于 3 月 15 日在体育馆举行大型招聘会", "date": "2024-01-18", "priority": "medium"},
    {"id": 3, "type": "公告", "title": "图书馆开放时间调整", "content": "周末开放时间调整为 9:00-21:00", "date": "2024-01-15", "priority": "low"},
    {"id": 4, "type": "紧急", "title": "网络安全提醒", "content": "请注意防范钓鱼邮件，不要点击可疑链接", "date": "2024-01-22", "priority": "high"}
]

# Mock 数据 - 学校平面图
campus_map_db = {
    "buildings": [
        {"id": 1, "name": "教学楼 A", "type": "teaching", "coordinates": {"x": 100, "y": 100}, "description": "主要教学楼，包含 50 间教室"},
        {"id": 2, "name": "教学楼 B", "type": "teaching", "coordinates": {"x": 200, "y": 100}, "description": "理科教学楼，包含实验室"},
        {"id": 3, "name": "图书馆", "type": "library", "coordinates": {"x": 150, "y": 200}, "description": "藏书 100 万册，座位 2000 个"},
        {"id": 4, "name": "食堂", "type": "dining", "coordinates": {"x": 250, "y": 150}, "description": "三层食堂，提供各地美食"},
        {"id": 5, "name": "体育馆", "type": "sports", "coordinates": {"x": 100, "y": 300}, "description": "室内体育馆，含游泳池"},
        {"id": 6, "name": "宿舍区", "type": "dormitory", "coordinates": {"x": 300, "y": 250}, "description": "学生公寓，共 10 栋"},
        {"id": 7, "name": "行政楼", "type": "admin", "coordinates": {"x": 150, "y": 50}, "description": "学校行政办公地点"},
        {"id": 8, "name": "实验楼", "type": "lab", "coordinates": {"x": 250, "y": 300}, "description": "科研实验中心"}
    ],
    "facilities": [
        {"name": "篮球场", "count": 6},
        {"name": "足球场", "count": 2},
        {"name": "停车场", "count": 3},
        {"name": "自行车棚", "count": 5}
    ]
}

# Mock 数据 - 官网信息
website_info = {
    "news": [
        {"id": 1, "title": "我校在 2024 年全国大学生竞赛中荣获金奖", "date": "2024-01-25", "summary": "计算机学院团队在 AI 赛道表现出色..."},
        {"id": 2, "title": "学校与知名企业建立战略合作伙伴关系", "date": "2024-01-23", "summary": "将为学生提供实习和就业机会..."},
        {"id": 3, "title": "2024 年国际学术交流周即将开幕", "date": "2024-01-20", "summary": "来自 15 个国家的学者将参会..."}
    ],
    "departments": ["计算机学院", "工程学院", "商学院", "文学院", "理学院", "医学院"],
    "contact": {
        "address": "XX 省 XX 市大学路 1 号",
        "phone": "010-12345678",
        "email": "info@university.edu.cn"
    }
}

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

# 权限管理模型
class Role(BaseModel):
    id: int
    name: str
    permissions: List[str]

class User(BaseModel):
    id: int
    username: str
    role_id: int
    email: str

# 课程表模型
class Course(BaseModel):
    id: int
    name: str
    teacher: str
    time: str
    location: str
    credits: int

# 饭卡模型
class CardBalance(BaseModel):
    username: str
    balance: float
    last_recharge: str
    status: str

# 日志模型
class SchoolLog(BaseModel):
    id: int
    type: str
    title: str
    content: str
    date: str
    priority: str

# 平面图模型
class Building(BaseModel):
    id: int
    name: str
    type: str
    coordinates: dict
    description: str

class CampusMap(BaseModel):
    buildings: List[Building]
    facilities: List[dict]

# API 路由
@app.get("/")
def read_root():
    return {"message": "欢迎使用学生管理系统 API", "version": "2.0"}

# ==================== 学生管理 ====================
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

# ==================== 权限管理 ====================
@app.get("/api/roles", response_model=List[Role])
def get_roles():
    """获取所有角色"""
    return roles_db

@app.get("/api/users", response_model=List[User])
def get_users():
    """获取所有用户"""
    return users_db

@app.get("/api/users/{user_id}/permissions")
def get_user_permissions(user_id: int):
    """获取用户权限"""
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    role = next((r for r in roles_db if r["id"] == user["role_id"]), None)
    return {"user": user, "role": role, "permissions": role["permissions"] if role else []}

# ==================== 课程表 ====================
@app.get("/api/courses", response_model=List[Course])
def get_courses():
    """获取所有课程"""
    return courses_db

@app.get("/api/courses/{course_id}", response_model=Course)
def get_course(course_id: int):
    """获取单个课程"""
    for course in courses_db:
        if course["id"] == course_id:
            return course
    raise HTTPException(status_code=404, detail="课程不存在")

# ==================== 饭卡余额 ====================
@app.get("/api/card-balance", response_model=List[CardBalance])
def get_all_card_balance():
    """获取所有饭卡余额"""
    return [{"username": k, **v} for k, v in card_balance_db.items()]

@app.get("/api/card-balance/{username}", response_model=CardBalance)
def get_card_balance(username: str):
    """获取指定用户饭卡余额"""
    if username not in card_balance_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"username": username, **card_balance_db[username]}

@app.post("/api/card-balance/{username}/recharge")
def recharge_card(username: str, amount: float):
    """饭卡充值"""
    if username not in card_balance_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="充值金额必须大于 0")
    card_balance_db[username]["balance"] += amount
    card_balance_db[username]["last_recharge"] = datetime.now().strftime("%Y-%m-%d")
    return {"message": "充值成功", "new_balance": card_balance_db[username]["balance"]}

# ==================== 学校日志 ====================
@app.get("/api/school-logs", response_model=List[SchoolLog])
def get_school_logs(log_type: Optional[str] = None):
    """获取学校日志"""
    if log_type:
        return [log for log in school_logs_db if log["type"] == log_type]
    return school_logs_db

@app.get("/api/school-logs/{log_id}", response_model=SchoolLog)
def get_school_log(log_id: int):
    """获取单个日志"""
    for log in school_logs_db:
        if log["id"] == log_id:
            return log
    raise HTTPException(status_code=404, detail="日志不存在")

# ==================== 学校平面图 ====================
@app.get("/api/campus-map", response_model=CampusMap)
def get_campus_map():
    """获取学校平面图"""
    return campus_map_db

@app.get("/api/campus-map/buildings", response_model=List[Building])
def get_buildings(building_type: Optional[str] = None):
    """获取建筑物列表"""
    if building_type:
        return [b for b in campus_map_db["buildings"] if b["type"] == building_type]
    return campus_map_db["buildings"]

@app.get("/api/campus-map/facilities")
def get_facilities():
    """获取设施列表"""
    return campus_map_db["facilities"]

# ==================== 官网信息 ====================
@app.get("/api/website/news")
def get_website_news():
    """获取官网新闻"""
    return website_info["news"]

@app.get("/api/website/departments")
def get_departments():
    """获取院系列表"""
    return website_info["departments"]

@app.get("/api/website/contact")
def get_contact_info():
    """获取联系方式"""
    return website_info["contact"]

@app.get("/api/website")
def get_website_info():
    """获取官网所有信息"""
    return website_info

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
