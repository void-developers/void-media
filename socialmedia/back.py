from flask import Flask, request,jsonify, render_template, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DB_name = "socialSQL.sqlite"

def get_db_connection():
    conn = sqlite3.connect(DB_name)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    create table if not exists users (id integer primary key autoincrement,
            name text not null,
                password text not null    )
                """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
     return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/add", methods=["POST"])
def add_user():
        conn = get_db_connection()
        data = request.get_json()
        if not data:
            return jsonify({"error": "no JSON data"}), 400

        addname = data.get("addname")
        addpassword = data.get("addpassword")
        hashed_password = generate_password_hash(addpassword)
        cur = conn.cursor()
        cur.execute("insert into users (name,password) values (?,?)",(addname,hashed_password))
        conn.commit()
        conn.close()
        return jsonify ({"message": "saved successfully"})
    
@app.route("/login", methods = ["POST"])
def login():
        conn = get_db_connection()
        data = request.get_json()
        if not data:
              return jsonify({"error": "no json data"})
        name = data.get("name")
        password = data.get("password")
        if not name or not password:
            return jsonify({"error": "name and password required"}), 400
        cur = conn.cursor()
        cur.execute("select * from users where name = ?",(name,))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password) :
              return jsonify({"message":"login successfull"})
        else:
              return jsonify({"message":"invalid"})

if __name__== "__main__":
    app.run(debug=True)
