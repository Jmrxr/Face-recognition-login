# Import libreries
from flask import Flask, render_template, redirect, session, request, flash
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
import secrets

# New instance flask
app = Flask(__name__)

# Setting database
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "whoami"
app.config["MYSQL_DB"] = "database"
app.config["SECRET_KEY"] = secrets.token_bytes(16)

# Connection database
cnx = mysql.connector.connect (
    host = app.config["MYSQL_HOST"],
    user = app.config["MYSQL_USER"],
    password = app.config["MYSQL_PASSWORD"],
    database = app.config["MYSQL_DB"],
    charset = "utf8mb4",
    collation = "utf8mb4_unicode_ci"
)

# Create table
cursor = cnx.cursor()
query = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    hash VARCHAR(255) NOT NULL
    )
"""
cursor.execute(query)
cnx.commit()

# Define routes
@app.route("/")
def index():
    return redirect("login")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Clear session existing
    session.clear()
    # Check if from existing
    if request.method == "POST":
        input_username = request.form.get("username")
        input_password = request.form.get("password")
        # Validate field input
        if not input_username:
            return render_template("login.html", messager=1)
        elif not input_password:
            return render_template("login.html", messager=2)
        # Create cursor to return dictionary
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s",(input_username,))
        user = cursor.fetchone()
        # Validate credencials user
        if user is None or not check_password_hash(user["hash"], input_password):
            return render_template("login.html", messager=3)
        session["user_id"] = user["id"]
        return redirect("/admin")
    return render_template("login.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get data user
        input_username = request.form.get("username")
        input_password = request.form.get("password")
        input_confirmation = request.form.get("confirmation")
        # Validate data user
        if not input_username:
            return render_template("register.html", messager=1)
        elif not input_password:
            return render_template("register.html", messager=2)
        elif not input_confirmation:
            return render_template("register.html", messager=4)
        elif input_password != input_confirmation:
            return render_template("register.html", messager=3)
       # Create cursor database
        cursor = cnx.cursor()
        cursor.execute("SELECT username FROM users WHERE username = %s", (input_username,))
        if cursor.fetchone():
            return render_template("register.html", messager=5)
        # Generate hashed password
        hash_password = generate_password_hash(input_password, method='pbkdf2:sha256', salt_length=8)
        cursor.execute('INSERT INTO users (username, hash) VALUES (%s, %s)', (input_username, hash_password))
        cnx.commit()
        new_user_id = cursor.lastrowid
        # Saving id user
        session["user_id"] = new_user_id
        flash(f"Usuario registrado como {input_username}")
        return redirect("/admin")
    return render_template("register.html")

# Inicialize web
if __name__ == "__main__":
    app.run(debug=True)