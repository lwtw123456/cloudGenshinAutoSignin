# MiHoYo 云·原神
一个更容易使用的本地版云·原神自动签到领奖小工具。

## 📌 项目简介


本项目由两部分组成：

- **Tampermonkey 油猴脚本**：在云·原神网页中捕获关键请求的完整 Header，并把它们发送到本地主机。
- **Python 程序**：运行本地 Flask 服务接收 Header；按设定时间每天执行一次“查看剩余时间 + 领取签到奖励”。

---

## 🚀 项目特性

- 自动捕获登录状态（无需手动抓包）  
- 每日定时自动签到  
- 登录失效自动提示并打开云·原神网页  
- 可指定非默认浏览器  
- 支持 pythonw 长期后台运行  
- 支持系统开机自启动  

---

## 📁 项目结构

    ├── main.py                                # Python 主程序
    ├── Capture Request Headers-1.0.user.js    # Tampermonkey 脚本
    ├── README.md                              # 项目文档
    ├── requirements.txt                       # 依赖列表
    └── LICENSE                                # 开源许可

---

## 📖 使用说明

## 1. 克隆仓库

``` bash
git clone https://github.com/lwtw123456/CloudGenshinAutoSignin.git
cd CloudGenshinAutoSignin
```

### 2. 安装依赖（Python 3.8+）

``` bash
pip install -r requirements.txt
```

### 3️. 安装油猴脚本

将油猴脚本安装到 **你用于访问云原神的浏览器** 中。

### 4. 启动 Python 服务

```bash
python main.py
```

#### 指定每日执行时间（默认 09:00）
```bash
python main.py --time 08:30
```

#### 指定浏览器路径
```bash
python main.py --browser "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

---

## ⚠ 非默认浏览器的重要说明（必看）

如果 **油猴脚本不是安装在系统默认浏览器中**，请注意：

- 程序在登录失效时会自动打开云原神网页  
- 默认会使用 **系统默认浏览器** 打开  
- 若该浏览器未安装油猴脚本，则登录信息无法被捕获  
- 自动登录与签到将无法继续

---

### ✅ 解决方案

#### 方案一（推荐）：启动时指定浏览器路径

```bash
python main.py --browser "你的浏览器路径"
```

#### 方案二：手动使用安装了油猴脚本的浏览器打开

```
https://ys.mihoyo.com/cloud/#/
```

完成登录即可。

---

## ⚙️ 后台运行方式

### 使用 pythonw（无窗口）

```bash
pythonw main.py --browser "你的浏览器路径" --time 07:00
```

---

### 设置 Windows 开机自启动

1. 新建 `start.bat`：
```bat
pythonw "C:\你的路径\main.py" --browser "你的浏览器路径" --time 07:00
```

2. 放入：
```
shell:startup
```

---

## 🧰 主要依赖

-   flask
-   schedule
-   requests

---


## 📄 开源协议

本项目基于 MIT License
开源，可自由用于个人或商业用途，但需保留版权声明。

---

## 🤝 贡献

欢迎 PR、Issue 或建议改进！

---

## ⭐ 支持本项目

如果你觉得这个项目对你有帮助，请给一个 Star ⭐！
