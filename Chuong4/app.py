from math import ceil
from flask import Flask, abort, render_template, request

app = Flask(__name__)

SHOP = {
    "name": "My Shop",
    "address": "123 Main Street",
    "phone": "123-456-7890"
}

MENU = [
    {"id": 1, "name": "cà phê đen", "price": 20000, "avaiable": True},
    {"id": 2, "name": "cà phê sữa", "price": 1000, "avaiable": True},
    {"id": 3, "name": "cà phê muối", "price": 15000, "avaiable": False},
    {"id": 4, "name": "bạc xỉu", "price": 35000, "avaiable": True},
    {"id": 5, "name": "bánh bao", "price": 10000, "avaiable": False},
    {"id": 6, "name": "bánh chuoi", "price": 10000, "avaiable": True},
    {"id": 7, "name": "bánh beo", "price": 10000, "avaiable": False},
    {"id": 8, "name": "bánh dau xanh", "price": 10000, "avaiable": True}
]

# Bộ lọc định dạng tiền tệ VND
@app.template_filter('vnd')
def format_vnd(value):
    try:
        return f"{int(value):,}".replace(",", ".") + " đ"
    except (ValueError, TypeError):
        return value

@app.route('/menu')
def menu():
    page = request.args.get('page', 1, type=int)
    per_page = 3  # Mỗi trang 3 món
    total_items = len(MENU)
    pages = ceil(total_items / per_page) if total_items > 0 else 1

    # Nếu số trang yêu cầu nhỏ hơn 1 hoặc lớn hơn tổng số trang -> 404
    if page < 1 or (page > pages and total_items > 0):
        abort(404)

    # Cắt danh sách món theo trang hiện tại
    start = (page - 1) * per_page
    end = start + per_page
    current_items = MENU[start:end]

    return render_template(
        'menu.html',
        shop=SHOP,
        items=current_items,
        page=page,
        pages=pages
    )

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', shop=SHOP), 404

if __name__ == '__main__':
    app.run(debug=True)