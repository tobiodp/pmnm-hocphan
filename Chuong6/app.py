from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, func

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)

app.config["SECRET_KEY"] = "A0Zr98j/3yX R~XHH!jmN]LWX/,?RT"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///calculator.db"
db.init_app(app)

class Student(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    mssv: Mapped[str] = mapped_column(String(10), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    gpa: Mapped[float] = mapped_column(default=0.0)

    def __repr__(self):
        return f"<Student {self.mssv} {self.name}>"

with app.app_context():
    db.create_all()

# Hàm thêm sinh viên y như cũ của bạn
@app.route('/themmau')
def add_sample():
    total = db.session.scalar(db.select(func.count(Student.id)))
    if total >= 1:
        return f"đã có {total} sinh viên"
    an = Student(mssv="B20DCCN001", name="Nguyễn Văn A", gpa=9.0)
    # chua ghi xuong db
    before = an.id 
    # đưa vào giỏ chờ ghi xuong db
    db.session.add(an)
    db.session.add_all([
        Student(mssv="B20DCCN002", name="Trần Văn B", gpa=8.0),
        Student(mssv="B20DCCN003", name="Lê Văn C", gpa=7.0),
        Student(mssv="B20DCCN004", name="Lê Văn d", gpa=5.0),
        Student(mssv="B20DCCN005", name="Lê Văn e", gpa=4.0),
        Student(mssv="B20DCCN006", name="Lê Văn f", gpa=3.0),
        Student(mssv="B20DCCN007", name="Lê Văn g", gpa=2.0),
        Student(mssv="B20DCCN008", name="Lê Văn h", gpa=1.0),   
    ])
    # ghi thật sự
    db.session.commit()
    after = an.id
    return f"thêm {after - (before or 0)} sinh viên"

# Hàm truy vấn sinh viên
TEXT = {"Content-Type": "text/plain; charset=utf-8"}

@app.get("/thu-truy-van")
def try_queries():
    if db.session.scalar(
        db.select(func.count(Student.id))
    ) == 0:
        return "Chưa có dữ liệu, hãy mở /themmau trước."

    lines = []

    # 1. Tìm sinh viên có ID = 3
    lines.append(
        f"1. get(3): {db.session.get(Student, 3)}"
    )

    # 2. Tìm sinh viên có ID = 99
    lines.append(
        f"2. get(99): {db.session.get(Student, 99)}"
    )

    # 3. Lấy tất cả sinh viên
    everyone = db.session.execute(
        db.select(Student)
    ).scalars().all()

    lines.append(
        f"3. Tất cả: {len(everyone)} sinh viên"
    )

    # 4. Lấy sinh viên GPA >= 8, giảm dần
    stmt = (
        db.select(Student)
        .where(Student.gpa >= 8)
        .order_by(Student.gpa.desc())
    )

    good = db.session.execute(stmt).scalars().all()

    lines.append(f"4. Điểm >= 8: {good}")

    # 5. Tìm sinh viên theo MSSV (B20DCCN002)
    binh = db.session.scalar(
        db.select(Student)
        .filter_by(mssv="B20DCCN002")
    )

    lines.append(
        f"5. MSSV B20DCCN002: {binh}"
    )

    # 6. Đếm sinh viên và tính GPA trung bình
    count = db.session.scalar(
        db.select(func.count(Student.id))
    )

    avg = db.session.scalar(
        db.select(func.avg(Student.gpa))
    )

    lines.append(
        f"6. Số SV: {count}, điểm TB: {avg:.2f}"
    )

    return "\n".join(lines), TEXT

# Hàm in ra 5 sinh viên
@app.route("/danhsach5")
@app.route("/5-sinh-vien")
def print_5_students():
    stmt = db.select(Student).limit(5)
    students = db.session.execute(stmt).scalars().all()

    if not students:
        return "Chưa có sinh viên nào trong CSDL, hãy mở /themmau trước."

    lines = ["--- DANH SÁCH 5 SINH VIÊN ---"]
    for sv in students:
        line = f"- ID: {sv.id} | MSSV: {sv.mssv} | Tên: {sv.name} | GPA: {sv.gpa}"
        lines.append(line)

    return "\n".join(lines), TEXT

# Trang chủ điều hướng
@app.get("/")
def home():
    return (
        "<h2>QUẢN LÝ SINH VIÊN</h2>"
        '<p><a href="/themmau">Thêm dữ liệu mẫu (/themmau)</a></p>'
        '<p><a href="/thu-truy-van">Truy vấn sinh viên (/thu-truy-van)</a></p>'
        '<p><a href="/danhsach5">In ra 5 sinh viên (/danhsach5)</a></p>'
    )

def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()
