from bson import ObjectId
from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

client = MongoClient("mongodb://localhost:27017/")
db = client["examen-recu"]


miapp = Flask(__name__)
miapp.secret_key="nano"

login_manager = LoginManager()
login_manager.init_app(miapp)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

@login_manager.user_loader
def load_user(id):
    user_data = db.users.find_one({"_id": ObjectId(id)})
    if user_data:
        return User(str(user_data["_id"]), user_data["email"])
    return None



######################### HOME #####################################
@miapp.route("/")
def home():
    
    return render_template("home.html")

######################### LOGIN #####################################
@miapp.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        comprovar_mail = db.users.find_one({"email":email})
        if comprovar_mail and check_password_hash(comprovar_mail["password"],password):
            user = User(str(comprovar_mail["_id"]), comprovar_mail["email"])
            login_user(user)
            return redirect(url_for("perfil"))
    
    
    return render_template("login.html")

######################### REGISTER #####################################
@miapp.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        fullname = request.form["fullname"]
        comprovar_mail = db.users.find_one({"email":email})
        if comprovar_mail:
            return "Email ya en uso"
        if email and password and fullname:
            hashed_password = generate_password_hash(password)
            db.users.insert_one({"email":email, "password":hashed_password,"fullname":fullname})        
            return redirect(url_for("login"))

        
    return render_template("register.html")

######################### PERFIL #####################################
@miapp.route("/perfil", methods=["GET","POST"])
@login_required
def perfil():
    
    
    
    return render_template("perfil.html")

######################### TIENDA #####################################
@miapp.route("/tienda", methods=["GET","POST"])
@login_required
def tienda():
    
    articulos = db.articulos.find()

    return render_template("tienda.html",articulos=articulos)

######################### AÑADIR CARRITO #####################################
@miapp.route("/anyadir_carrito/<string:id>")
@login_required
def anyadir_carrito(id):
    
    articulo = db.articulos.find_one({"_id":ObjectId(id)})
  
    db.carrito.insert_one({"nombre":articulo["nombre"], "precio":articulo["precio"], "descripcion": articulo["descripcion"]})
    
    return redirect(url_for("tienda"))

######################### CARRITO #####################################
@miapp.route("/carrito", methods=["GET","POST"])
@login_required
def carrito():
    datos = db.carrito.find()
    
    
    return render_template("carrito.html",datos = datos)   

######################### DELETE #####################################
@miapp.route("/delete/<string:id>", methods=["GET","POST"])
@login_required     
def delete(id):
    
    db.carrito.delete_one({"_id":ObjectId(id)})
    return redirect(url_for("carrito"))

######################### tramite #####################################
@miapp.route("/tramite")
@login_required
def tramite():
    
    
    return render_template("tramite.html")

######################### pago #####################################
@miapp.route("/pago", methods=["GET","POST"])
@login_required
def pago():
    if request.method == "POST":
        nombre = request.form["nombre"]
        IBAN = request.form["IBAN"]
        ccv = request.form["ccv"]
        if nombre and IBAN and ccv:
            datos = db.targetas.find_one({"nombre":nombre, "IBAN":IBAN, "ccv":ccv})
            if datos:
                
                return "Exito compra"
            else:
                return "Fallo compra"
    
    return render_template("pago.html")


######################### TARGETA #####################################
@miapp.route("/targeta", methods=["GET","POST"])
@login_required
def targeta():
    targetas = db.targetas.find()
    if current_user.email != "admin@admin.com":
        return "No eres admin"
    else:
        if request.method == "POST":
            nombre = request.form["nombre"]
            IBAN = request.form["IBAN"]
            ccv = request.form["ccv"]
            if nombre and IBAN and ccv:
                db.targetas.insert_one({"nombre":nombre, "IBAN":IBAN, "ccv":ccv})
                print("targeta añadida correctamente")
            else:
                return "faltan datos"
    
    return render_template("targetas.html",targetas = targetas)

######################### LOGOUT #####################################
@miapp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

######################### ADMIN #####################################
@miapp.route("/admin", methods=["GET","POST"])
@login_required
def admin():
    if current_user.email != "admin@admin.com":
        return "No eres admin"
    else:
        users = db.users.find()
        articulos = db.articulos.find()
        return render_template("admin.html", datos=users, articulos=articulos)
    
######################### DELETE USER #####################################
@miapp.route("/user/<string:id>", methods=["GET","POST"])
@login_required     
def delete_user(id):
    if current_user.email != "admin@admin.com":
        return "No eres admin"
    else:
        db.users.delete_one({"_id":ObjectId(id)})
        return redirect(url_for("admin"))

######################### EDIT USER #####################################
@miapp.route("/edit/<string:id>", methods=["GET","POST"])
@login_required     
def edit_user(id):
    if current_user.email != "admin@admin.com":
        return "No eres admin"
    else:
    
        datos = db.users.find_one({"_id":ObjectId(id)})
        if request.method == "POST":
            email = request.form["email"]
            fullname = request.form["fullname"]
            if email and fullname:
                db.users.update_one({"_id":ObjectId(id)},{"$set":{"email":email, "fullname": fullname}})
                return redirect(url_for("admin"))
            
        
        return render_template("edit.html", datos=datos)
    
######################### AÑADIR ARTICULO #####################################
@miapp.route("/anyadir", methods=["GET","POST"])
@login_required     
def anyadir():
    if current_user.email != "admin@admin.com":
        return "No eres admin"
    else:
        if request.method == "POST":
            nombre = request.form["nombre"]
            precio = request.form["precio"]
            descripcion = request.form["descripcion"]
            if nombre and precio and descripcion:
                db.articulos.insert_one({"nombre":nombre, "precio": precio,"descripcion":descripcion})
                return redirect(url_for("admin"))
            
        
        return render_template("anyadir.html")
    
######################### EDIT ARTICULO #####################################
@miapp.route("/edit_articulo/<string:id>", methods=["GET","POST"])
@login_required     
def edit_articulo(id):
    if current_user.email != "admin@admin.com":
        return "No eres admin"
    else:
    
        datos = db.articulos.find_one({"_id":ObjectId(id)})
        if request.method == "POST":
            nombre = request.form["nombre"]
            precio = request.form["precio"]
            descripcion = request.form["descripcion"]
            if nombre and precio and descripcion:
                db.articulos.update_one({"_id":ObjectId(id)},{"$set":{"nombre":nombre, "precio": precio,"descripcion":descripcion}})
                return redirect(url_for("admin"))
            
        
        return render_template("edit_articulo.html", datos=datos)
    
######################### DELETE USER #####################################
@miapp.route("/articulo/<string:id>", methods=["GET","POST"])
@login_required     
def delete_articulo(id):
    if current_user.email != "admin@admin.com":
        return "No eres admin"
    else:
        db.articulos.delete_one({"_id":ObjectId(id)})
        return redirect(url_for("admin"))
    
######################### AÑADIR USER #####################################
@miapp.route("/anyadir_usuario", methods=["GET","POST"])
def register_admin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        fullname = request.form["fullname"]
        comprovar_mail = db.users.find_one({"email":email})
        if comprovar_mail:
            return "Email ya en uso"
        if email and password and fullname:
            hashed_password = generate_password_hash(password)
            db.users.insert_one({"email":email, "password":hashed_password,"fullname":fullname})        
            return redirect(url_for("admin"))

        
    return render_template("anyadir_usuario.html")

    
    
    
######################### 404 error #####################################
@miapp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    miapp.run(debug=True,host="0.0.0.0")