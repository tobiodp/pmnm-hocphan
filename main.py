from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    a = request.form.get('a')
    b = request.form.get('b')

    if a == None or a == '':
        a = 0
    else:
        a = float(a)

    if b == None or b == '':
        b = 1
    else:
        b = float(b)

    if b == 0:
        chia = "Không thể chia cho 0"
    else:
        chia = a / b

    ketQua = {
        'a': a,
        'b': b,
        'cong': a + b,
        'tru': a - b,
        'nhan': a * b,
        'chia': chia
    }
    return render_template(
        'math.html',
        ketQua=ketQua
    )


if __name__ == '__main__':
    app.run(debug=True)