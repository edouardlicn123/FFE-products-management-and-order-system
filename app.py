import os
import csv
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from io import StringIO
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_very_strong_secret_key_please_change_it'  # 生产环境务必修改
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== 酒店常用产品品类 ====================
CATEGORIES = [
    "床及床头板", "床垫", "床头柜", "衣柜", "电视柜", "书写桌/化妆台", "休闲椅/沙发椅",
    "沙发（单人/双人/三人）", "茶几/边几", "行李柜/行李架", "迷你吧柜", "全身镜/穿衣镜",
    "餐桌/餐椅", "会议桌/会议椅", "吧台/吧椅", "户外家具",
    "吸顶灯", "吊灯", "壁灯", "床头灯", "落地灯", "台灯", "镜前灯", "氛围灯/装饰灯", "户外灯具",
    "马桶", "面盆/洗手盆", "浴缸", "淋浴花洒", "浴室配件（毛巾架/置物架等）", "水龙头",
    "客房门", "卫生间门", "衣柜门", "阳台门", "防火门",
    "窗帘/纱帘", "地毯", "装饰画/挂画", "绿植/装饰植物", "保险箱", "其他"
]
# ============================================================

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录管理员账号'
login_manager.login_message_category = 'info'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT id, username FROM user WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return User(user['id'], user['username']) if user else None

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    with get_db_connection() as conn:
        with app.open_resource('schema.sql', mode='r') as f:
            conn.executescript(f.read())
        conn.commit()

        # 默认管理员（首次运行创建，密码 123456）
        admin = conn.execute('SELECT * FROM user WHERE username = "admin"').fetchone()
        if not admin:
            hashed = generate_password_hash('123456')
            conn.execute('INSERT INTO user (username, password) VALUES (?, ?)', ('admin', hashed))
            conn.commit()

# ====================== 路由 ======================

@app.route('/')
def index():
    category = request.args.get('category')
    conn = get_db_connection()
    query = 'SELECT * FROM product'
    params = []
    if category:
        query += ' WHERE category = ?'
        params.append(category)
    query += ' ORDER BY id DESC'
    products = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('products.html', products=products, selected_category=category, categories=CATEGORIES)

@app.route('/order')
def order_page():
    category = request.args.get('category')
    conn = get_db_connection()
    query = 'SELECT * FROM product'
    params = []
    if category:
        query += ' WHERE category = ?'
        params.append(category)
    query += ' ORDER BY id DESC'
    products = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('order.html', products=products, selected_category=category, categories=CATEGORIES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            login_user(User(user['id'], user['username']))
            return redirect(url_for('admin'))
        flash('用户名或密码错误', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已成功退出登录', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM product ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin.html', products=products)

@app.route('/admin/add', methods=['GET', 'POST'])
@app.route('/admin/edit/<int:pid>', methods=['GET', 'POST'])
@login_required
def edit_product(pid=None):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM product WHERE id = ?', (pid,)).fetchone() if pid else None

    if request.method == 'POST':
        model = request.form['model'].strip()
        category = request.form['category']
        description = request.form.get('description', '').strip()
        length = request.form.get('length', type=int) or None
        width = request.form.get('width', type=int) or None
        height = request.form.get('height', type=int) or None
        seat_height = request.form.get('seat_height', type=int) or None

        uploaded_files = request.files.getlist('images')
        existing_images = product['images'].split(',') if product and product['images'] else []
        existing_images = [img for img in existing_images if img]

        for file in uploaded_files:
            if file and allowed_file(file.filename):
                if len(existing_images) >= 10:
                    flash('图片数量已达上限（10张），后续图片被忽略', 'warning')
                    break
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                existing_images.append(filename)

        images_str = ','.join(existing_images[:10])

        try:
            if pid:
                conn.execute('''UPDATE product SET model=?, category=?, description=?, length=?, width=?, 
                                height=?, seat_height=?, images=? WHERE id=?''',
                             (model, category, description, length, width, height, seat_height, images_str, pid))
            else:
                conn.execute('''INSERT INTO product (model, category, description, length, width, height, seat_height, images)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                             (model, category, description, length, width, height, seat_height, images_str))
            conn.commit()
            flash('产品保存成功', 'success')
            return redirect(url_for('admin'))
        except sqlite3.IntegrityError:
            flash('型号已存在，请使用唯一型号', 'error')
        finally:
            conn.close()

    conn.close()
    return render_template('edit_product.html', product=product, categories=CATEGORIES)

@app.route('/admin/delete/<int:pid>')
@login_required
def delete_product(pid):
    conn = get_db_connection()
    conn.execute('DELETE FROM product WHERE id = ?', (pid,))
    conn.commit()
    conn.close()
    flash('产品已删除', 'info')
    return redirect(url_for('admin'))

# ==================== 修改密码 ====================
@app.route('/admin/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password1 = request.form['new_password1']
        new_password2 = request.form['new_password2']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM user WHERE id = ?', (current_user.id,)).fetchone()

        if not check_password_hash(user['password'], old_password):
            flash('当前密码错误', 'error')
        elif new_password1 != new_password2:
            flash('两次输入的新密码不一致', 'error')
        elif len(new_password1) < 6:
            flash('新密码至少6位', 'error')
        else:
            hashed = generate_password_hash(new_password1)
            conn.execute('UPDATE user SET password = ? WHERE id = ?', (hashed, current_user.id))
            conn.commit()
            conn.close()
            flash('密码修改成功，请重新登录', 'success')
            logout_user()
            return redirect(url_for('login'))

        conn.close()

    return render_template('change_password.html')

# ==================== 生成订单CSV ====================
@app.route('/generate_order', methods=['POST'])
def generate_order():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['品类', '型号', '长(mm)', '宽(mm)', '高(mm)', '座高(mm)', '数量', '补充说明', '图片链接（逗号分隔）'])
    
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM product').fetchall()
    product_dict = {p['id']: p for p in products}
    conn.close()
    
    base_url = request.url_root.rstrip('/')
    
    for key, qty in request.form.items():
        if key.startswith('qty_') and qty.isdigit() and int(qty) > 0:
            pid = int(key.split('_')[1])
            product = product_dict.get(pid)
            if product:
                supplement = request.form.get(f'supplement_{pid}', '').strip()
                image_urls = ''
                if product['images']:
                    image_urls = ','.join(f"{base_url}/static/uploads/{img}" for img in product['images'].split(',') if img)
                
                writer.writerow([
                    product['category'],
                    product['model'],
                    product['length'] or '',
                    product['width'] or '',
                    product['height'] or '',
                    product['seat_height'] or '',
                    qty,
                    supplement,
                    image_urls
                ])
    
    output.seek(0)
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='hotel_order.csv'
    )

if __name__ == '__main__':
    init_db()
    app.run(debug=True)