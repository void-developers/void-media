from flask import Flask, request,jsonify, render_template, redirect, url_for, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "super-secret-key"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder of back.py
DB_name = os.path.join(BASE_DIR, "socialSQL.sqlite")
UPLOAD_FOLDER= "static/images"
ALLOWED_EXTENSIONS = {"png","jpg","jpeg","gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
     return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect(DB_name)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    create table if not exists users (id integer primary key autoincrement,
            name text not null,
                password text not null    )
                """)
    
    cur.execute("""
                create table if not exists profile (id integer not null unique,
                name text not null,
                imgpath text,
                description text,
                foreign key (id) references users(id))
                """)
    
    cur.execute("""
     create table if not exists posts(id integer primary key autoincrement,
                user_id integer not null,
                content text,
                created_at datetime default current_timestamp,
                foreign key(user_id) references users(id))
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
        defaultimg = "default-profile-picture-avatar-photo-placeholder-vector-illustration-default-profile-picture-avatar-photo-placeholder-vector-189495158.webp"
        defaultdesc = ""
        addname = data.get("addname")
        addpassword = data.get("addpassword")
        hashed_password = generate_password_hash(addpassword)
        cur = conn.cursor()
        cur.execute("insert into users (name,password) values (?,?)",(addname,hashed_password))
        user_id = cur.lastrowid
        cur.execute("insert into profile (id,name,imgpath,description) values (?,?,?,?)",(user_id,addname,defaultimg,defaultdesc))
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
              session["user_id"]=user["id"]
              return jsonify({"message":"login successfull"})
        else:
              return jsonify({"message":"invalid"})

@app.route("/profile")
def profile():
     user_id = session.get("user_id")
     if not user_id:
          return redirect(url_for("home"))
     conn = get_db_connection()
     cur = conn.cursor()
     cur.execute("""
        select users.name, profile.imgpath, profile.description from users
                 join profile on users.id = profile.id
                 where users.id = ?
                 """,(user_id,))
     user = cur.fetchone()  
     conn.close()
     return render_template("profile.html" ,user=user)

@app.route("/descupdate", methods = ["POST"])
def descupdate():
    user_id = session.get("user_id")
    if not user_id:
         return redirect(url_for("home"))
    data = request.get_json()
    if not data or "desc" not in data:
        return jsonify({"error": "no description provided"}), 400
    newdesc = data.get("desc")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("update profile set description = ? where id = ?",(newdesc,user_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "description updated"})

@app.route("/profileurl")
def profileurl():
     return render_template("profile.html")

@app.route("/editname", methods = ["POST"])
def editname():
     user_id = session.get("user_id")
     if not user_id:
          return redirect(url_for("home"))
     data = request.get_json()
     new_name = data.get("newname")
     conn = get_db_connection()
     cur = conn.cursor()
     cur.execute("update users set name = ? where id = ?",(new_name,user_id))
     conn.commit()
     conn.close()
     return jsonify ({"message": "updated successfully"})

@app.route("/uploadimg", methods = ["POST"])
def uploadimg():
     if "file" not in request.files:
          return jsonify({"error": "no file found"})
     file = request.files["file"]
     if file.filename == "":
          return jsonify({"error":"no uplaoded file"})
     if file and allowed_file(file.filename):
          filename = secure_filename(file.filename)
          file.save(os.path.join(app.config["UPLOAD_FOLDER"],filename))

          user_id = session.get("user_id")
          if not user_id:
               return jsonify({"message":"not logged in"})
          conn = get_db_connection()
          cur = conn.cursor()
          cur.execute("update profile set imgpath = ? where id = ?",(filename,user_id))
          conn.commit()
          conn.close()
          return jsonify({"message":"image updated"})
     return jsonify({"error":"file type not allowed"})

@app.route("/posts", methods=["POST"])
def posts():
     user_id = session.get("user_id")
     if not user_id:
          return redirect(url_for("home"))
     data = request.get_json()
     if not data or "content" not in data:
        return jsonify({"error": "no content"}), 400
     post = data.get("content")
     conn = get_db_connection()
     cur = conn.cursor()
     cur.execute("insert into posts (user_id,content) values (?,?)",(user_id,post))
     conn.commit()
     conn.close()
     return jsonify({"message":"posted successfully"})

@app.route("/showposts")
def showposts():
     user_id = session.get("user_id")
     if not user_id:
          return redirect(url_for("home"))
     conn = get_db_connection()
     cur = conn.cursor()
     cur.execute("select name from users where id = ?",(user_id,))
     user = cur.fetchone()
     username = user["name"]
     
     cur.execute("select users.name, posts.content, posts.created_at from posts join users on posts.user_id=users.id order by posts.created_at desc")
     posts = cur.fetchall()
     conn.close()
     return render_template("home.html", posts=posts , name=username)

if __name__== "__main__":
    init_db()
    app.run(host="0.0.0.0", port=6000 ,debug=True)
