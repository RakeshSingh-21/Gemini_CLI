# 🛒 E-Commerce Web Application (FastAPI + MySQL + AI Agents)

A full-stack E-Commerce web application built using **FastAPI**, **MySQL**, **Jinja2 templates**, and integrated with **AI-powered agents (LLM)** for smart product recommendations, admin analytics, and customer support.

---

## 🚀 Features

### 👤 User Features

* User Registration & Login (JWT Cookie Auth)
* Browse Products
* Add to Cart
* Checkout & Orders
* View Order History
* AI Assistant (Product Recommendation + Support)

---

### 👨‍💼 Admin Features

* Admin Dashboard
* Add / Edit / Delete Products
* View Orders
* AI Admin Assistant

  * Total Products
  * Total Customers
  * Total Orders
  * Total Sales
  * Low Stock Products (<5)

---

### 🤖 AI Agent Features

* Product Recommendation (based on query like "mobiles under 40000")
* Cart Assistance
* Order Tracking
* Admin Analytics
* Product Description Generator (LLM)

---

## 🧠 Tech Stack

| Layer    | Technology                              |
| -------- | --------------------------------------- |
| Backend  | FastAPI                                 |
| Database | MySQL + SQLAlchemy                      |
| Frontend | HTML, CSS, Jinja2                       |
| Auth     | JWT (Cookie-based)                      |
| AI       | Local LLM (llama.cpp / Gemini optional) |

---

## 📁 Project Structure

```
ecommerce_project/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│
│   ├── routes/
│   │   ├── api.py
│   │   ├── pages.py
│   │   └── agent_routes.py
│
│   ├── agents/
│   │   ├── llm_client.py
│   │   ├── ecommerce_agent.py
│   │   ├── recommendation_agent.py
│   │   ├── support_agent.py
│   │   └── admin_agent.py
│
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── cart.html
│   │   ├── orders.html
│   │   ├── add_product.html
│   │   ├── edit_product.html
│   │   ├── agent_chat.html
│   │   └── admin_agent.html
│
│   └── static/
│       ├── css/
│       └── js/
│
└── requirements.txt
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Project

```bash
git clone <your-repo>
cd ecommerce_project
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv myenv
myenv\Scripts\activate   # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Setup MySQL Database

Create DB:

```sql
CREATE DATABASE ecommerce_db;
```

Update `database.py`:

```python
DATABASE_URL = "mysql+pymysql://root:password@localhost/ecommerce_db"
```

---

### 5️⃣ Run Server

```bash
uvicorn main:app --reload
```

---

### 6️⃣ Open Browser

```
http://127.0.0.1:8000
```

---

## 🔐 Authentication

* First registered user → **Admin**
* Others → **Customer**
* JWT stored in HTTP-only cookies

---

## 🤖 AI Agent Endpoints

### Chat Assistant

```
POST /api/agent/chat
```

### Admin AI

```
POST /api/agent/admin
```

### Generate Product Description

```
POST /api/agent/generate-description
```

---

## 🧪 Sample Queries

### Customer AI

* "Show mobiles under 40000"
* "What is in my cart?"
* "Track my order"

### Admin AI

* "Total users"
* "Low stock products"
* "Total sales"

---

## 🛠️ Key Improvements Implemented

* Fixed Jinja template errors
* Fixed SQLAlchemy issues
* Implemented role-based access (Admin/Customer)
* Added AI Agents (LLM + DB hybrid)
* Improved product recommendation logic
* Added edit/add product pages (no modal)

---

## ⚠️ Known Issues

* Recommendation is keyword-based (can upgrade to LLM intent)
* Basic UI (can improve with React or Tailwind UI)
* No payment gateway integration yet

---

## 🚀 Future Enhancements

* LLM-based intent detection
* Smart search filters (price extraction)
* Payment integration (Stripe/Razorpay)
* Real-time notifications
* Product reviews & ratings
* Image upload instead of URL

---


