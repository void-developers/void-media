from datetime import datetime
import email
import pathlib
import uuid
from xmlrpc import client
from bson import ObjectId
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
import cloudinary
import cloudinary.uploader
import json

from flask import Flask, request,jsonify, render_template, redirect, url_for, session
from pymongo import MongoClient
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import request, render_template


app = Flask(__name__)
app.secret_key = "super-secret-key"
UPLOAD_FOLDER= "static/images"
ALLOWED_EXTENSIONS = {"png","jpg","jpeg","gif", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

load_dotenv()
uri = os.getenv("MONGO_URI")
client = MongoClient(uri)
db = client['Void_media']

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

#delete from here if you want to test locally


GOOGLE_CLIENT_ID = "78105620575-9hmje8ja5vtn4bamf6gjkfqmljhbb0q2.apps.googleusercontent.com"
client_config = json.loads(os.environ.get("GOOGLE_CLIENT_SECRET"))
flow = Flow.from_client_config(client_config=client_config , scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"], redirect_uri="https://void-media-lynj.onrender.com/callback")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" 



# to here
# and replace with this
"""
GOOGLE_CLIENT_ID = "78105620575-9hmje8ja5vtn4bamf6gjkfqmljhbb0q2.apps.googleusercontent.com"
flow = Flow.from_client_secrets_file("client_secrets.json" , scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"], redirect_uri="https://void-media-lynj.onrender.com/callback")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
"""


def allowed_file(filename):
     return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS



@app.route("/")
def home():
    user_agent = request.user_agent.string.lower()

    if "mobile" in user_agent:
        session.clear()
        return render_template("sign-log-mobile.html")
    else:
        session.clear()
        return render_template("sign-log.html")





@app.route("/google-login")
def google_login():
     authorization_url, state = flow.authorization_url()
     session["state"] = state
     return redirect(authorization_url)

@app.route("/callback")
def callback():
     state = session["state"]
     flow.fetch_token(authorization_response=request.url)
     if not session["state"] == request.args.get("state"):
          return jsonify({"error": "state mismatch"}), 400
     credentials = flow.credentials
     request_adapter = grequests.Request()
     id_info = id_token.verify_oauth2_token(
     credentials._id_token,
     request_adapter,
     GOOGLE_CLIENT_ID
     )
     email = id_info.get("email")
     name = id_info.get("name")
     picture = "default-profile-picture-avatar-photo-placeholder-vector-illustration-default-profile-picture-avatar-photo-placeholder-vector-189495158.webp" 

    # ✅ Check if user exists
     user = db.users.find_one({"email": email})

     if not user:
        new_user = db.users.insert_one({
            "name": name,
            "email": email,
            "password": None,
            "imgpath": picture,
            "description": ""
        })
        session["user_id"] = str(new_user.inserted_id)
     else:
        session["user_id"] = str(user["_id"])

     return redirect(url_for("showposts"))


@app.route("/add", methods=["POST"])
def add_user():
        data = request.get_json()
        if not data:
             return jsonify({"error": "no JSON data"}), 400
        defaultimg = "default-profile-picture-avatar-photo-placeholder-vector-illustration-default-profile-picture-avatar-photo-placeholder-vector-189495158.webp"
        defaultdesc = ""
        addname = data.get("addname")
        addpassword = data.get("addpassword")
        hashed_password = generate_password_hash(addpassword)
        users = db.users.find_one({"name": addname})
        if users:
             return jsonify({"error": "username already exists"}), 400
        db.users.insert_one({"name": addname, "password": hashed_password, "imgpath": defaultimg, "description": defaultdesc})       
        return jsonify ({"message": "saved successfully"})
     
@app.route("/login", methods = ["POST"])
def login():
        data = request.get_json()
        if not data:
              return jsonify({"error": "no json data"})
        name = data.get("name")
        password = data.get("password")
        if not name or not password:
            return jsonify({"error": "name and password required"}), 400
        
        user = db.users.find_one({"name": name})
        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            return jsonify({"message":"login successfull"})
        else:
              return jsonify({"message":"invalid"})

@app.route("/profile")
def profile():
     user_id = session.get("user_id")
     if not user_id:
          return redirect(url_for("home"))
     user = db.users.find_one({"_id": ObjectId(user_id)})
     if not user:
          return redirect(url_for("home"))  # Redirect if user not found
     
     user_data = {
           "name" : user["name"],
           "imgpath": user["imgpath"],
           "description": user["description"]
     }

     return render_template("profile.html", user=user_data)

@app.route("/descupdate", methods = ["POST"])
def descupdate():
    user_id = session.get("user_id")
    if not user_id:
         return jsonify({"error": "Not logged in"}), 401
    data = request.get_json()
    if not data or "desc" not in data:
        return jsonify({"error": "no description provided"}), 400
    newdesc = data.get("desc")
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"description": newdesc}})
    return jsonify({"message": "description updated"})

@app.route("/editnamepage")
def editnamepage():
     user_id = session.get("user_id")
     if not user_id:
          return redirect(url_for("home"))
     user = db.users.find_one({"_id": ObjectId(user_id)})
     user_data = {
          "name": user["name"]
     }
     
     return render_template("editname.html", user=user_data)
     

@app.route("/editname", methods = ["POST"])
def editname():
     user_id = session.get("user_id")
     if not user_id:
          return redirect(url_for("home"))
     data = request.get_json()
     new_name = data.get("newname")
     db.users.update_one({"_id": ObjectId(user_id)},{"$set":{"name":new_name}})
     return jsonify ({"message": "updated successfully"})

@app.route("/uploadimg", methods=["POST"])
def uploadimg():
        if "file" not in request.files:
            return jsonify({"error": "no file found"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "no uploaded file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "file type not allowed"}), 400

        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "not logged in"}), 401

        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "user not found"}), 404

        # delete old image
        if user.get("public_id"):
            cloudinary.uploader.destroy(user["public_id"])

        # upload new image
        result = cloudinary.uploader.upload(file)
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "imgpath": result["secure_url"],
                "public_id": result["public_id"]
            }}
        )
        return jsonify({"message": "image updated"})

@app.route("/editimgpage")
def editimgpage():
     user_id = session.get("user_id")
     if not user_id:
          return redirect(url_for("home"))
     return render_template("editimage.html")

@app.route("/posts", methods=["POST"])
def posts():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "not logged in"}), 401

    data = request.get_json()
    if not data or "content" not in data:
        return jsonify({"error": "no content"}), 400

    post_content = data.get("content").strip()
    if not post_content:
        return jsonify({"error": "post cannot be empty"}), 400

    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "user not found"}), 404

        db.posts.insert_one({
            "user_id": ObjectId(user_id),
            "name": user["name"],
            "content": post_content,
            "created_at": datetime.now()
        })
        return jsonify({"message": "posted successfully"})
    except Exception as e:
        print("Error inserting post:", e)
        return jsonify({"error": "server error"}), 500

@app.route("/showposts")
def showposts():
     user_id = session.get("user_id")
     if not user_id:
          return redirect(url_for("home"))
     user = db.users.find_one({"_id": ObjectId(user_id)})
     username = user["name"]
     profile_pic = user.get("imgpath")
     
     posts_curser = db.posts.find().sort("created_at", -1).limit(10)
     posts = []

     for post in posts_curser:
       user = db.users.find_one({"_id": post.get("user_id")})
       post["poster_img"] = user.get("imgpath") if user else None
       posts.append(post)
     return render_template("home.html", posts=posts , name=username, profile_pic=profile_pic)

@app.route("/searchbar")
def searchbar():
     q = request.args.get("who","")
     user = db.users.find({"name": {"$regex": q, "$options": "i"}})
     users = []
     for u in user:
          users.append({"name": u["name"], "id": str(u["_id"])})
          
     return jsonify(users)

@app.route("/send_request", methods=["POST"])
def send_request():
     data = request.get_json()
     user_id = session.get("user_id")
     if not user_id:
          return redirect(url_for("home"))
     friend_id = data["friend_id"]
     sender = db.users.find_one({"_id": ObjectId(user_id)})
     db.friend_request.insert_one({"user_id":ObjectId(user_id),"friend_id": ObjectId(friend_id), "status": "pending", "created_at": datetime.datetime.utcnow()})
     db.notifications.insert_one({"user_id": ObjectId(friend_id), "message": f"you have friend request from {sender['name']}", "created_at": datetime.datetime.utcnow()})
     
     existing = db.friend_request.find_one({
    "user_id": ObjectId(user_id),
    "friend_id": ObjectId(friend_id),
    "status": "pending"
})
     if existing:
          return jsonify({"error": "Request already sent"}), 400
     return jsonify({"message":"request sent"})

@app.route("/accept_request", methods=["POST"])
def accept_request():
     data = request.get_json()
     user_id = session.get("user_id")
     friend_id = data["friend_id"]
     if not user_id:
          return redirect(url_for("home"))
     req = db.friend_request.find_one({"user_id": ObjectId(friend_id), "friend_id": ObjectId(user_id), "status": "pending"})
     if not req:
          return jsonify({"error": "no pending request found"}), 404
     db.friends.insert_one({"user1": ObjectId(user_id), "user2": ObjectId(friend_id)})
     db.friend_request.update_one({"_id": req["_id"]}, {"$set": {"status": "accepted"}})
     db.notifications.insert_one({"user_id": ObjectId(friend_id), "message": f"your friend request to {user_id} has been accepted", "created_at": datetime.datetime.utcnow()})
     return jsonify({"message":"request accepted"})

@app.route("/show_friends")
def show_friends():
     user_id = session.get("user_id")
     if not user_id:
          return redirect(url_for("home"))
     req = db.friends.find({"$or": [{"user1": ObjectId(user_id)}, {"user2": ObjectId(user_id)}]})
     friends = []
     for f in req:
           friend_id = f["user2"] if f["user1"] == ObjectId(user_id) else f["user1"]
           friend_user = db.users.find_one({"_id" : friend_id})
           if friend_user:
                 friends.append({"name" : friend_user["name"]})
     return render_template("friends.html", friends=friends)

@app.route("/show_notification")
def show_notifications():
     user_id = session.get("user_id")
     if not user_id:
          return redirect(url_for("home"))
     notifications = db.notifications.find({"user_id": ObjectId(user_id)}).sort("created_at", -1)
     return render_template("home.html", notifications = notifications)

@app.route("/messages", methods = ["POST"])
def messages():
     user_id = session.get("user_id")
     if not user_id:
          return redirect("home")
     data = request.get_json()
     content = data.get("content")
     receiver_id = data.get("receiver_id")
     if not receiver_id or not content:
        return jsonify({"error": "missing data"}), 400
     user = db.users.find_one({"_id": ObjectId(user_id)})  # Get sender info
     db.messages.insert_one({
     "sender_id": ObjectId(user_id),
     "receiver_id" : ObjectId(receiver_id),
     "sender_name": user["name"],   
     "imgpath": user["imgpath"],    
     "content": content,
     "created_at": datetime.datetime.utcnow()
     })     
     return jsonify({"message":"message sent"})

@app.route("/chat/<friend_id>")
def chat(friend_id):
     user_id = session.get("user_id")
     if not user_id:
          return redirect(url_for("home"))
     req = db.messages.find({"$or" : [{"sender_id": ObjectId(user_id), "receiver_id" : ObjectId(friend_id)}, 
                                        {"sender_id" : ObjectId(friend_id), "receiver_id": ObjectId(user_id)}]}).sort("created_at", 1)
     messages = []
     for msg in req:
          messages.append({
          "content": msg["content"],
          "sender_name": msg["sender_name"],  
          "imgpath": msg["imgpath"],        
          "created_at": msg["created_at"],
          "is_me": msg["sender_id"] == ObjectId(user_id)
     })
     return render_template("chat.html", messages = messages , friend_id=friend_id)
     
@app.route("/unfriend/<int:friend_id>", methods = ["POST"])
def unfriend(friend_id):
     user_id = session.get("user_id")
     if not user_id:
          return redirect(url_for("home"))
     db.friends.delete_one({"$or" : [{"user1": ObjectId(user_id), "user2": ObjectId(friend_id)}, {"user1": ObjectId(friend_id), "user2": ObjectId(user_id)}]})
     return jsonify({"message":"unfriended successfully"})

@app.route("/deletenotif/<int:notification_id>", methods = ["POST"])
def deletenotif(notification_id):
     user_id = session.get("user_id")
     if not user_id:
          return redirect(url_for("home"))
     db.notifications.delete_one({"_id" : ObjectId(notification_id), "user_id": ObjectId(user_id)})
     return jsonify({"message":"deleted successfully"})

     

if __name__== "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
