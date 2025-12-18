# 酒店FFE产品管理及订单生成系统

  - 一个轻量级、深色主题（Discord 风格）的酒店常用产品展示与订单生成系统。
  - 专为酒店家具、灯具、洁具、门等品类设计，支持管理员后台管理、访客浏览、品类筛选、多图展示、订单 CSV 导出。
  - 由Grok生成，Python + Flask实现，使用SQLite 数据库以简化操作。
  
## 功能特点

- **访客功能**（无需登录）
  - 产品列表展示（支持多张图片、尺寸、描述）
  - 按品类筛选（家具、灯具、洁具、门、其他 30+ 酒店常见品类）
  - 生成订单页面：选择数量、补充说明，一键导出 CSV（包含品类、型号、尺寸、图片链接等）

- **管理员功能**（需登录）
  - 添加/编辑/删除产品
  - 支持上传最多 10 张图片（追加模式）
  - 品类精确选择
  - 修改管理员密码
  - 默认账号：`admin` / `123456`（首次运行自动创建，**请立即修改密码**）

## 项目结构

hotel_product_app/
├── app.py                  # 主程序
├── schema.sql              # 数据库结构
├── database.db             # 运行后自动生成（无需手动创建）
├── static/
│   ├── uploads/            # 上传的图片存放目录（需手动修改权限）
│   └── css/
│       └── style.css       # Discord 风格 CSS
└── templates/              # HTML 模板
    ├── login.html
    ├── products.html
    ├── order.html
    ├── admin.html
    ├── edit_product.html
    └── change_password.html


## 安装与运行

### 1. 环境准备

推荐使用 Python 3.9 或更高版本。
# 创建并激活虚拟环境（强烈推荐）
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

### 2. 安装依赖
pip install flask flask-login werkzeug

### 3. 运行项目
python app.py

首次运行会自动：
  - 创建 database.db
  - 根据 schema.sql 初始化表结构
  - 创建默认管理员账号：用户名 admin，密码 123456

打开浏览器访问：http://127.0.0.1:5000

### 4.  使用流程 
  - 用admin / 123456 登录（路径：/login）
  - 进入后台添加产品（支持多图上传、选择品类）
  - 访客可在首页浏览、筛选品类
  - 点击“生成订单”选择数量 → 下载 CSV

## 可能存在的问题及解决方法

### 图片不显示
确保 static/uploads/ 目录存在且有写权限。上传后刷新页面即可。
### No module named 'flask'
未激活虚拟环境或未安装依赖。请确认已执行 pip install 并激活 venv。
### 型号重复报错
型号字段唯一约束正常行为，请使用不同型号。
### 首次运行未创建管理员账号
删除 database.db 文件后重新运行 python app.py。
### 其他文件编码问题
所有 .py、.html、.sql 文件均应为 UTF-8 编码。




