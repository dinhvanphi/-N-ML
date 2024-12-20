from flask import Flask, request, render_template, redirect, url_for, flash, session
import pickle
import numpy as np
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Load model từ file .pkl
model = pickle.load(open('model.pkl', 'rb'))

# Hàm kiểm tra đăng nhập từ file data.txt
def check_user_from_txt(username, password):
    with open('data.txt', 'r') as file:
        users = file.readlines()
        for user in users:
            saved_username, saved_password = user.strip().split(' ')
            if saved_username == username and saved_password == password:
                return True
    return False

# Hàm kiểm tra xem tài khoản đã tồn tại chưa
def is_user_exists(username):
    with open('data.txt', 'r') as file:
        users = file.readlines()
        for user in users:
            saved_username, _ = user.strip().split(' ')
            if saved_username == username:
                return True
    return False

# Hàm thêm tài khoản mới vào file data.txt
def add_user_to_txt(username, password):
    with open('data.txt', 'a') as file:
        file.write(f'\n{username} {password}')

# Route trang chủ
@app.route('/')
def home():
    # Luôn chuyển hướng đến trang đăng nhập khi vào trang chủ
    return redirect(url_for('login_form'))

# Route form đăng nhập
@app.route('/login_form')
def login_form():
    # Hiển thị form đăng nhập
    return render_template('index.html', logged_in=False, show_register=False)

# Route đăng nhập
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if check_user_from_txt(username, password):
        session['username'] = username  # Lưu username vào session
        flash('Đăng nhập thành công!', 'success')
        return redirect(url_for('predict_form'))  # Chuyển hướng đến form dự đoán
    else:
        flash('Đăng nhập thất bại. Kiểm tra lại thông tin.', 'danger')
    return redirect(url_for('login_form'))

# Route form đăng ký
@app.route('/register_form')
def register_form():
    return render_template('index.html', show_register=True, logged_in=False)

# Route xử lý đăng ký
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    
    # Kiểm tra xem tài khoản đã tồn tại chưa
    if is_user_exists(username):
        flash('Tài khoản đã tồn tại. Vui lòng chọn tên người dùng khác.', 'danger')
        return redirect(url_for('register_form'))
    
    # Thêm người dùng mới vào file data.txt
    add_user_to_txt(username, password)
    
    flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
    return redirect(url_for('login_form'))

# Route form dự đoán
@app.route('/predict_form')
def predict_form():
    # Kiểm tra xem người dùng đã đăng nhập hay chưa
    if 'username' not in session:
        return redirect(url_for('login_form'))  # Chuyển hướng về trang đăng nhập nếu chưa đăng nhập
    return render_template('index.html', logged_in=True, show_register=False)

# Route dự đoán
@app.route('/predict', methods=['POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login_form'))  # Chuyển hướng về trang đăng nhập nếu chưa đăng nhập
    
    # Lấy thông tin đầu vào từ form
    input_features = [float(x) for x in request.form.values()]
    features = np.array([input_features])
    
    # Sử dụng predict_proba để trả về xác suất
    prediction_proba = model.predict_proba(features)
    
    # Xác suất đậu là lớp 1
    prob_pass = prediction_proba[0][1] * 100
    prob_fail = 100 - prob_pass

    result = f'Xác suất đậu: {prob_pass:.2f}%, Xác suất rớt: {prob_fail:.2f}%'
    
    return render_template('index.html', logged_in=True, prediction_text=f'Kết quả: {result}', show_register=False)


# Route đăng xuất
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Bạn đã đăng xuất thành công!', 'success')
    return redirect(url_for('login_form'))

if __name__ == "__main__":
    # Tạo file data.txt nếu chưa tồn tại
    if not os.path.exists('data.txt'):
        open('data.txt', 'w').close()

    app.run(debug=True, port=5001)




