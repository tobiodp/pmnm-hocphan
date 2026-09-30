from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

books = [
    {
        "id": 1,
        "title": "Lập trình Python",
        "author": "Nguyễn Văn A",
        "year": 2024,
        "category": "Lập trình",
        "available": True
    },
    {
        "id": 2,
        "title": "Lập trình Java",
        "author": "Trần Văn B",
        "year": 2023,
        "category": "Lập trình",
        "available": True
    },
    {
        "id": 3,
        "title": "Cơ sở dữ liệu",
        "author": "Lê Văn C",
        "year": 2022,
        "category": "Cơ sở dữ liệu",
        "available": False
    },
    {
        "id": 4,
        "title": "Mạng máy tính",
        "author": "Phạm Văn D",
        "year": 2021,
        "category": "Mạng máy tính",
        "available": True
    }
]


@app.route("/")
def index():
    total_books = len(books)

    available_books = 0
    for book in books:
        if book["available"]:
            available_books += 1

    return render_template(
        "index.html",
        total_books=total_books,
        available_books=available_books
    )


@app.route("/books")
def book_list():
    category = request.args.get("category")

    if category:
        filtered_books = []

        for book in books:
            if book["category"] == category:
                filtered_books.append(book)
    else:
        filtered_books = books

    categories = []

    for book in books:
        if book["category"] not in categories:
            categories.append(book["category"])

    return render_template(
        "books.html",
        books=filtered_books,
        categories=categories,
        selected_category=category
    )


@app.route("/books/<int:book_id>")
def book_detail(book_id):
    for book in books:
        if book["id"] == book_id:
            return render_template(
                "book_detail.html",
                book=book
            )

    return render_template(
        "404.html",
        message="Không có sách với ID = " + str(book_id)
    ), 404


@app.route("/api/books")
def api_books():
    return jsonify(books)


@app.route("/api/books/<int:book_id>")
def api_book_detail(book_id):
    for book in books:
        if book["id"] == book_id:
            return jsonify(book)

    return jsonify({
        "error": "Không có sách với ID = " + str(book_id)
    }), 404


@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        "404.html",
        message="Trang bạn yêu cầu không tồn tại"
    ), 404


if __name__ == "__main__":
    app.run(debug=True)