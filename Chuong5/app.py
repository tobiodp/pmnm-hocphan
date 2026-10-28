from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/bai1', methods=['GET', 'POST'])
def calculator():
    a = request.form.get('a', '')
    b = request.form.get('b', '')
    op = request.form.get('op', '+')
    
    result = None
    err_a = None
    err_b = None
    err_general = None

    if request.method == 'POST':
        # Kiểm tra để trống cả hai ô
        if not a.strip() and not b.strip():
            err_general = "Lỗi cả hai ô"
        else:
            # Kiểm tra ô a
            try:
                num_a = float(a.replace(',', '.'))
            except ValueError:
                err_a = "Lỗi ô a: Vui lòng nhập một số"

            # Kiểm tra ô b
            try:
                num_b = float(b.replace(',', '.'))
            except ValueError:
                err_b = "Lỗi ô b: Vui lòng nhập một số"

            # Nếu không có lỗi định dạng, tiến hành tính toán
            if not err_a and not err_b:
                if op == '+':
                    ans = num_a + num_b
                    result = f"{a} + {b} = {ans:g}"
                elif op == '-':
                    ans = num_a - num_b
                    result = f"{a} - {b} = {ans:g}"
                elif op == '*':
                    ans = num_a * num_b
                    result = f"{a} * {b} = {ans:g}"
                elif op == '/':
                    if num_b == 0:
                        err_b = "Lỗi ô b: Không thể chia cho 0"
                    else:
                        ans = num_a / num_b
                        result = f"{a} / {b} = {ans:g}"
                else:
                    err_general = "Phép toán không hợp lệ"

    return render_template('calculator.html', 
                           a=a, b=b, op=op, 
                           result=result, 
                           err_a=err_a, 
                           err_b=err_b, 
                           err_general=err_general)

@app.route('/bai2', methods=['GET', 'POST'])
def bai2():
    cc = request.form.get('cc', '')
    gk = request.form.get('gk', '')
    ck = request.form.get('ck', '')
    
    result = None
    is_error = False

    if request.method == 'POST':
        try:
            # Đổi dấu phẩy sang dấu chấm để chuyển sang float an toàn
            v_cc = float(cc.replace(',', '.'))
            v_gk = float(gk.replace(',', '.'))
            v_ck = float(ck.replace(',', '.'))
            
            # Kiểm tra khoảng điểm hợp lệ từ 0 đến 10
            if not (0 <= v_cc <= 10 and 0 <= v_gk <= 10 and 0 <= v_ck <= 10):
                result = "Lỗi: Điểm các cột phải nằm trong khoảng từ 0 đến 10!"
                is_error = True
            else:
                # Tính điểm học phần (10% CC, 30% GK, 60% CK)
                dtk = v_cc * 0.1 + v_gk * 0.3 + v_ck * 0.6
                dtk_rounded = round(dtk, 1)

                # Xếp loại điểm chữ (Kiểm tra điểm liệt nếu CK < 1)
                if v_ck < 1:
                    diem_chu = "F (điểm thi dưới 1)"
                else:
                    if dtk_rounded >= 8.5: diem_chu = "A"
                    elif dtk_rounded >= 7.0: diem_chu = "B"
                    elif dtk_rounded >= 5.5: diem_chu = "C"
                    elif dtk_rounded >= 4.0: diem_chu = "D"
                    else: diem_chu = "F"

                result = f"{dtk_rounded} - {diem_chu}"
        except ValueError:
            result = "Lỗi: Vui lòng nhập số hợp lệ!"
            is_error = True

    return render_template('bai2.html', cc=cc, gk=gk, ck=ck, result=result, is_error=is_error)

@app.route('/bai3', methods=['GET', 'POST'])
def bai3():
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
                    color_class = "orange"
                elif bmi < 23:
                    phan_loai = "Bình thường"
                    color_class = "green"
                elif bmi < 25:
                    phan_loai = "Thừa cân"
                    color_class = "orange"
                else:
                    phan_loai = "Béo phì"
                    color_class = "red"

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