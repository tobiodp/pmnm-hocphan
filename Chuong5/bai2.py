from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/bai2', methods=['GET', 'POST'])
def tinh_diem():
    cc = request.form.get('cc', '')
    gk = request.form.get('gk', '')
    ck = request.form.get('ck', '')
    
    result = None
    is_error = False

    if request.method == 'POST':
        try:
            # Thay dấu phẩy thành dấu chấm để đổi sang số thực an toàn
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

if __name__ == '__main__':
    app.run(debug=True)