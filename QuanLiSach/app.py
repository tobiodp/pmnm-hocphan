from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Integer, ForeignKey, func

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SECRET_KEY"] = "bookstore-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///book_management.db"
db.init_app(app)

# ==========================================
# ĐỊNH NGHĨA CÁC MODEL CƠ SỞ DỮ LIỆU
# ==========================================

# 1. Model Danh mục Sách (Categories)
class Category(db.Model):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    books: Mapped[list["Book"]] = relationship(back_populates="category", cascade="all, delete-orphan")

# 2. Model Sách (Books)
class Book(db.Model):
    __tablename__ = 'books'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category: Mapped["Category"] = relationship(back_populates="books")

# Tự động tạo bảng SQLite khi khởi chạy lần đầu
with app.app_context():
    db.create_all()


# ==========================================
# CÁC ROUTE XỬ LÝ ỨNG DỤNG
# ==========================================

# 1. Trang Dashboard tổng hợp
@app.route("/")
def dashboard():
    total_categories = db.session.scalar(db.select(func.count(Category.id))) or 0  
    total_books = db.session.scalar(db.select(func.count(Book.id))) or 0
    total_stock = db.session.scalar(db.select(func.sum(Book.stock))) or 0

    stats = db.session.execute(
        db.select(Category.name, func.count(Book.id), func.coalesce(func.sum(Book.stock), 0))
        .outerjoin(Book, Category.id == Book.category_id)
        .group_by(Category.id, Category.name)
    ).all()

    return render_template("dashboard.html", 
                           total_categories=total_categories, 
                           total_books=total_books, 
                           total_stock=total_stock, 
                           stats=stats)


# 2. Quản lý Danh mục Sách (Thêm, Xem, Sửa, Xóa)
@app.route("/categories", methods=["GET"], endpoint="manage_categories_get")
def manage_categories_get():
    categories = db.session.execute(db.select(Category)).scalars().all()
    return render_template("categories.html", categories=categories, edit_category=None)

@app.route("/categories", methods=["POST"], endpoint="manage_categories_post")
def manage_categories_post():
    name = request.form.get("name")
    desc = request.form.get("description")
    if name:
        db.session.add(Category(name=name, description=desc))
        db.session.commit()
    return redirect(url_for("manage_categories_get"))

@app.route("/categories/edit/<int:id>", methods=["GET"], endpoint="edit_category_get")
def edit_category_get(id):
    category_to_edit = db.session.get(Category, id)
    if not category_to_edit:
        return redirect(url_for("manage_categories_get"))
        
    categories = db.session.execute(db.select(Category)).scalars().all()
    return render_template("categories.html", categories=categories, edit_category=category_to_edit)

@app.route("/categories/edit/<int:id>", methods=["POST"], endpoint="edit_category_post")
def edit_category_post(id):
    category = db.session.get(Category, id)
    if category:
        category.name = request.form.get("name")
        category.description = request.form.get("description")
        db.session.commit()
    return redirect(url_for("manage_categories_get"))

@app.route("/categories/delete/<int:id>", endpoint="delete_category")
def delete_category(id):
    cat = db.session.get(Category, id)
    if cat:
        db.session.delete(cat)
        db.session.commit()
    return redirect(url_for("manage_categories_get"))


# 3. Quản lý Sách theo danh mục, Lọc, Thêm, Sửa, Xóa
@app.route("/books", methods=["GET"], endpoint="manage_books")
def manage_books_get():
    cat_filter = request.args.get("category_id", type=int)
    
    stmt = db.select(Book)
    if cat_filter:
        stmt = stmt.where(Book.category_id == cat_filter)
    
    books = db.session.execute(stmt).scalars().all()
    categories = db.session.execute(db.select(Category)).scalars().all()
    
    return render_template("books.html", books=books, categories=categories, cat_filter=cat_filter, edit_book=None)

@app.route("/books", methods=["POST"], endpoint="add_book")
def manage_books_post():
    title = request.form.get("title")
    author = request.form.get("author")
    price = float(request.form.get("price") or 0)
    stock = int(request.form.get("stock") or 0)
    category_id = int(request.form.get("category_id"))
    
    db.session.add(Book(title=title, author=author, price=price, stock=stock, category_id=category_id))
    db.session.commit()
    
    return redirect(url_for("manage_books", category_id=category_id))

@app.route("/books/edit/<int:id>", methods=["GET"], endpoint="edit_book_get")
def edit_book_get(id):
    book = db.session.get(Book, id)
    if not book:
        return redirect(url_for("manage_books"))
        
    books = db.session.execute(db.select(Book)).scalars().all()
    categories = db.session.execute(db.select(Category)).scalars().all()
    
    return render_template("books.html", books=books, categories=categories, edit_book=book, cat_filter=None)

@app.route("/books/edit/<int:id>", methods=["POST"], endpoint="edit_book_post")
def edit_book_post(id):
    book = db.session.get(Book, id)
    if book:
        book.title = request.form.get("title")
        book.author = request.form.get("author")
        book.price = float(request.form.get("price") or 0)
        book.stock = int(request.form.get("stock") or 0)
        book.category_id = int(request.form.get("category_id"))
        
        db.session.commit()
        
    return redirect(url_for("manage_books", category_id=book.category_id if book else None))

@app.route("/books/delete/<int:id>", endpoint="delete_book")
def delete_book(id):
    book = db.session.get(Book, id)
    cat_id = book.category_id if book else None
    if book:
        db.session.delete(book)
        db.session.commit()
    return redirect(url_for("manage_books", category_id=cat_id))


# 4. Route nạp dữ liệu mẫu mở rộng (6 danh mục & hơn 30 đầu sách)
@app.route("/themmau")
def add_sample():
    if db.session.scalar(db.select(func.count(Category.id))) > 0:
        return '<script>alert("Đã có dữ liệu sẵn trong hệ thống!"); window.location.href="/";</script>'
    
    c1 = Category(name="Lập trình & Công nghệ", description="Sách chuyên ngành về các ngôn ngữ lập trình, cấu trúc dữ liệu và phát triển phần mềm.")
    c2 = Category(name="Khoa học viễn tưởng", description="Sách tiểu thuyết, giả tưởng và khám phá vũ trụ tương lai.")
    c3 = Category(name="Kỹ năng sống & Phát triển bản thân", description="Sách hướng dẫn quản lý thời gian, tư duy và kỹ năng mềm.")
    c4 = Category(name="Kinh tế & Quản trị kinh doanh", description="Sách về khởi nghiệp, tài chính cá nhân và quản trị doanh nghiệp.")
    c5 = Category(name="Sách Ngoại ngữ & IELTS", description="Tài liệu học tiếng Anh, từ vựng, ngữ pháp và luyện thi chứng chỉ quốc tế.")
    c6 = Category(name="Lịch sử & Văn hóa", description="Sách nghiên cứu lịch sử thế giới, Việt Nam và các nền văn hóa nhân loại.")
    
    db.session.add_all([c1, c2, c3, c4, c5, c6])
    db.session.commit()
    
    db.session.add_all([
        # Danh mục 1
        Book(title="Clean Code: A Handbook of Agile Software Craftsmanship", author="Robert C. Martin", price=350000, stock=15, category_id=c1.id),
        Book(title="Design Patterns: Elements of Reusable Object-Oriented Software", author="Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides", price=420000, stock=8, category_id=c1.id),
        Book(title="Spring Boot in Action", author="Craig Walls", price=310000, stock=12, category_id=c1.id),
        Book(title="Head First Java", author="Kathy Sierra, Bert Bates", price=290000, stock=20, category_id=c1.id),
        Book(title="Python Crash Course", author="Eric Matthes", price=320000, stock=25, category_id=c1.id),
        Book(title="The Pragmatic Programmer", author="Andrew Hunt, David Thomas", price=380000, stock=10, category_id=c1.id),
        Book(title="Database System Concepts", author="Abraham Silberschatz", price=450000, stock=6, category_id=c1.id),
        Book(title="Refactoring: Improving the Design of Existing Code", author="Martin Fowler", price=390000, stock=9, category_id=c1.id),

        # Danh mục 2
        Book(title="Dune", author="Frank Herbert", price=180000, stock=25, category_id=c2.id),
        Book(title="The Three-Body Problem", author="Cixin Liu", price=210000, stock=14, category_id=c2.id),
        Book(title="Interstellar: The Complete Screenplay", author="Jonathan Nolan, Christopher Nolan", price=195000, stock=10, category_id=c2.id),
        Book(title="Neuromancer", author="William Gibson", price=160000, stock=18, category_id=c2.id),
        Book(title="Foundation", author="Isaac Asimov", price=175000, stock=22, category_id=c2.id),
        Book(title="Project Hail Mary", author="Andy Weir", price=230000, stock=16, category_id=c2.id),

        # Danh mục 3
        Book(title="Đắc Nhân Tâm", author="Dale Carnegie", price=88000, stock=50, category_id=c3.id),
        Book(title="Nhà Giả Kim", author="Paulo Coelho", price=79000, stock=40, category_id=c3.id),
        Book(title="Thói quen nguyên tử (Atomic Habits)", author="James Clear", price=135000, stock=35, category_id=c3.id),
        Book(title="Tư duy nhanh và chậm", author="Daniel Kahneman", price=165000, stock=20, category_id=c3.id),
        Book(title="Sức mạnh của thói quen", author="Charles Duhigg", price=115000, stock=28, category_id=c3.id),
        Book(title="Đời thay đổi khi chúng ta thay đổi", author="Andrew Matthews", price=75000, stock=60, category_id=c3.id),

        # Danh mục 4
        Book(title="Nhà đầu tư thông minh", author="Benjamin Graham", price=250000, stock=18, category_id=c4.id),
        Book(title="Cha giàu cha nghèo", author="Robert T. Kiyosaki", price=110000, stock=45, category_id=c4.id),
        Book(title="100 Tuyệt chiêu đàm phán", author="Brian Tracy", price=95000, stock=30, category_id=c4.id),
        Book(title="Từ tốt đến vĩ đại", author="Jim Collins", price=210000, stock=12, category_id=c4.id),
        Book(title="Làm giàu từ chứng khoán", author="William J. O'Neil", price=280000, stock=15, category_id=c4.id),
        Book(title="Chiến lược đại dương xanh", author="W. Chan Kim, Renée Mauborgne", price=190000, stock=22, category_id=c4.id),

        # Danh mục 5
        Book(title="Cambridge IELTS 18 Academic", author="Cambridge University Press", price=150000, stock=50, category_id=c5.id),
        Book(title="English Grammar in Use", author="Raymond Murphy", price=185000, stock=40, category_id=c5.id),
        Book(title="Tactics for Listening: Developing", author="Jack C. Richards", price=120000, stock=30, category_id=c5.id),
        Book(title="IELTS Writing Recent Actual Tests", author="Mat Clark", price=140000, stock=25, category_id=c5.id),

        # Danh mục 6
        Book(title="Sapiens: Lược sử loài người", author="Yuval Noah Harari", price=215000, stock=30, category_id=c6.id),
        Book(title="Lược sử thời gian", author="Stephen Hawking", price=160000, stock=20, category_id=c6.id),
        Book(title="Đại Việt Sử Ký Toàn Thư", author="Ngô Sĩ Liên", price=450000, stock=8, category_id=c6.id),
        Book(title="Văn hóa ẩm thực Việt Nam", author="Nhiều tác giả", price=130000, stock=15, category_id=c6.id),
    ])
    
    db.session.commit()
    
    return '<script>alert("Nạp dữ liệu mẫu mở rộng thành công!"); window.location.href="/";</script>'

if __name__ == '__main__':
    app.run(debug=True)