from flask import Flask, render_template, request

app = Flask(__name__)
git
def tinh_bmi():
    cao_str = request.form.get('cao', '')
    nang_str = request.form.get('nang', '')
    
    result = None
    err_cao = None
    err_nang = None
    err_general = None
    color_class = None

    if request.method == 'POST':
        # Kiểm tra để trống cả hai ô
        if not cao_str.strip() and not nang_str.strip():
            err_general = "Lỗi cả hai ô"
        else:
            # Kiểm tra ô chiều cao
            try:
                cao = float(cao_str.replace(',', '.'))
            except ValueError:
                err_cao = "Lỗi ô chiều cao: Vui lòng nhập một số."
            else:
                if cao < 50 or cao > 250:
                    err_cao = "Giá trị phải từ 50 đến 250. (nhập mét thay vì cm)"

            # Kiểm tra ô cân nặng
            try:
                nang = float(nang_str.replace(',', '.'))
            except ValueError:
                err_nang = "Lỗi ô cân nặng: Vui lòng nhập một số."
            else:
                if nang < 10 or nang > 300:
                    err_nang = "Lỗi ô cân nặng: Giá trị phải từ 10 đến 300."

            # Nếu không có lỗi, tiến hành tính toán BMI
            if not err_cao and not err_nang and not err_general:
                cao_m = cao / 100.0
                bmi = round(nang / (cao_m ** 2), 1)

                # Tính khoảng cân nặng lý tưởng (BMI từ 18.5 đến 22.9)
                min_cn = round(18.5 * (cao_m ** 2), 1)
                max_cn = round(22.9 * (cao_m ** 2), 1)

                # Phân loại chuẩn người Châu Á và màu sắc kết quả
                if bmi < 18.5:
                    phan_loai = "Thiếu cân"
                    color_class = "orange" # vàng
                elif bmi < 23:
                    phan_loai = "Bình thường"
                    color_class = "green" # xanh
                elif bmi < 25:
                    phan_loai = "Thừa cân"
                    color_class = "orange" # vàng
                else:
                    phan_loai = "Béo phì"
                    color_class = "red" # đỏ

                result = f"{bmi} - {phan_loai}; nên có {min_cn} - {max_cn} kg"

    return render_template('bai3.html', 
                           cao=cao_str, 
                           nang=nang_str, 
                           result=result, 
                           err_cao=err_cao, 
                           err_nang=err_nang, 
                           err_general=err_general,
                           color_class=color_class)

if __name__ == '__main__':
    app.run(debug=True)