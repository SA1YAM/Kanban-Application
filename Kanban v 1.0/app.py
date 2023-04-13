from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, url_for, redirect, request
from flask_login import login_user, LoginManager, login_required, UserMixin, logout_user, current_user 
from flask_bcrypt import Bcrypt
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///kanaban_database.sqlite3"
app.config['SECRET_KEY'] = 'thisisquiteasecretkey'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



app.app_context().push()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key = True, autoincrement = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    password = db.Column(db.String(), nullable = False)
    full_name = db.Column(db.String(20), nullable = False)
    email = db.Column(db.String(), unique = True, nullable = False)
    created_at = db.Column(db.DateTime(), nullable = False)
    lists = db.relationship('List', backref = 'user', cascade = "all, delete", lazy = True)
    
    
    
class List(db.Model):
    list_id = db.Column(db.Integer(), primary_key = True, autoincrement = True)
    name = db.Column(db.String(), nullable = False)
    description = db.Column(db.String(), nullable = False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    cards = db.relationship('Card', backref = 'list', cascade = "all, delete", lazy = True)

    
class Card(db.Model):
    card_id = db.Column(db.Integer(), primary_key = True, autoincrement = True)
    title = db.Column(db.String(), nullable = False)
    content = db.Column(db.String(), nullable = False)
    deadline = db.Column(db.DateTime(), nullable = False)
    completed_switch = db.Column(db.Boolean(), nullable = False)
    created_date = db.Column(db.DateTime(), nullable = False)
    last_updated = db.Column(db.DateTime(), nullable = False)
    completed_at = db.Column(db.DateTime())
    lists_id = db.Column(db.Integer(), db.ForeignKey('list.list_id'), nullable = False)
    
    
    



@app.route("/", methods = ["GET", "POST"])
def index():
    return render_template("login.html")
    
    
    
    
@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
        
    if request.method == "POST":
        fullname = request.form.get("full_name")
        Email = request.form.get("email")
        user_name = request.form.get("username")
        password = request.form.get("password")            
            
        
        user1 = User.query.filter_by(username = user_name).first()
        user2 = User.query.filter_by(email = Email).first()

        if user1 and user2:
            message = "User already registered, Please try again with a diffrent username and email"
            return render_template("error.html", error_message = message, link = 'register')
            
        
        if user1:
            message = "Username already registered, Please try again with a diffrent username"
            return render_template("error.html", error_message = message, link = 'register')

        elif user2:
            message = "email is already registerd, Please try again with a diffrent email"
            return render_template("error.html", error_message = message, link = 'register')

        elif " " in password:
            message = "Your password must not contain any spaces"
            return render_template("error.html", error_message = message, link = 'register')

        elif len(password) < 5:
            message = "Your password must be atleast 5 characters long "
            return render_template("error.html", error_message = message, link = 'register')
            
        else:
            hashed_password = bcrypt.generate_password_hash(password)
            new_user = User(username = user_name, password = hashed_password, full_name = fullname, email = Email, created_at = datetime.now())
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
            
            
        
        
        
@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
        
    if request.method == "POST":
        user_name = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username = user_name).first()
        
        if user :
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                if current_user.is_authenticated:
                    return redirect(url_for('dashboard'))

            else:
                message = "Authentication Failed. The password is incorrect, Please try again and provide the correct password"
                return render_template("error.html", error_message = message, link = 'login')

        else:
            message = "Authentication Failed. User does not exists, Please verify the username and try again, If you don't have an account Sign Up"
            return render_template("error.html", error_message = message, link = 'login')
            
                
                
                
               
               
@app.route("/dashboard", methods= ["GET", "POST"])
@login_required
def dashboard():

    if current_user.is_authenticated:
        l = current_user.lists
    
    if l == []:
        return render_template("old_dashboard.html")

    else:
        return render_template("dashboard.html", lists = l)
    
    
    
@app.route("/logout", methods = ["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))





@app.route("/dashboard/user_details", methods = ["GET", "POST"])
@login_required
def user_details():
    if current_user.is_authenticated:
        u = current_user

    return render_template("user_details.html", user = u )




@app.route("/dashboard/user_manual", methods = ["GET", "POST"])
@login_required
def user_manual():
    
    return render_template("user_manual.html")






@app.route("/dashboard/delete_account", methods = ["GET", "POST"])
@login_required
def delete_user():
    
    if request.method == "GET":
        return render_template("delete_account.html")


    if request.method == "POST":
        Email = request.form.get("email")
        user_name = request.form.get("username")
        Password = request.form.get("password")

        if current_user.is_authenticated and current_user.username == user_name:
            u1 = User.query.filter_by(username = user_name).first()
            

            if u1:
                if u1.email == Email:
                    if bcrypt.check_password_hash(u1.password, Password):
                        db.session.delete(u1)
                        db.session.commit()

                        logout_user()

                        return redirect(url_for('login'))
                    
                    else:
                        message = "Authentication Failed. Please provide valid credentials, Incorrect password. Please try again"
                        return render_template("error.html", error_message = message, link = 'delete_user')

                else:
                    message = "Authentication Failed. Please provide valid credentials, Incorrect username or email. Please try again"
                    return render_template("error.html", error_message = message, link = 'delete_user')

            else:
                message = "Authentication Failed. Please provide valid credentials, Incorrect username. Please try again"
                return render_template("error.html", error_message = message, link = 'delete_user')

        else:
            message = "Authentication Failed. Please provide valid credentials for this account. Please try again"
            return render_template("error.html", error_message = message, link = 'delete_user')
                
                
            

        
    
    
    
    
    
@app.route("/list/create", methods = ["GET", "POST"])
@login_required
def create_list():
    if request.method == "GET" :
        return render_template("create_list.html")




    if request.method == "POST" :
        l_name = request.form.get("name")
        desc = request.form.get("description")
        if current_user.is_authenticated:
            listss = current_user.lists
            
        l = List.query.filter_by(name = l_name).first()
            

        flag = True

        if len(l_name) > 20:
            message = "Your list name should be only of 20 characters at max."
            return render_template("error.html", error_message = message, link = 'create_list')

        for lis in listss:
            if lis.name == l_name:
                flag = False
        
        if (flag):
            if current_user.is_authenticated:
                l1 = List(name = l_name, description = desc, user_id = current_user.id)
                db.session.add(l1)
                db.session.commit()
                return redirect(url_for('dashboard'))
        
        else:
            message = "Some list from same name already exists from this account, Please try again and choose a diffrent name"
            return render_template("error.html", error_message = message, link = 'create_list')
    

@app.route("/list/<int:list_id>/edit", methods = ["GET", "POST"])
@login_required
def edit_list(list_id):
    listt = List.query.get(list_id)
    
    if request.method == "GET" :
        return render_template("edit_list.html", lister = listt)

    if request.method == "POST":
        list_name = request.form.get("name")
        flag = True
        
        for lists in current_user.lists:
            if lists.name == list_name and lists.list_id != listt.list_id:
                flag = False

        if len(list_name) > 20:
            message = "Your list name should be only of 20 characters at max."
            return render_template("error_arg.html", error_message = message, link_name = 'list', id_list = list_id)        

        if(flag):
            listt.name = list_name
            listt.description = request.form.get("description")
            db.session.commit()
            return redirect(url_for('dashboard'))

        else:
            message = "Another list from this name already exists from this account, Please choose a diffrent name in order to change it and try again"
            return render_template("error_arg.html", error_message = message, link_name = 'list', id_list = list_id)
            


@app.route("/list/<int:list_id>/delete", methods = ["GET", "POST"])
@login_required
def delete_list(list_id):
    listt = List.query.get(list_id)
    db.session.delete(listt)
    db.session.commit()

    return redirect(url_for('dashboard'))


@app.route("/card/create", methods = ["GET", "POST"])
@login_required
def create_card():
    if current_user.is_authenticated:
            listss = current_user.lists

        
    if request.method == "GET":
        if current_user.is_authenticated:
            listss = current_user.lists
            
        return render_template("create_card.html", lists = listss)

    if request.method == "POST":
        List_Id = int(request.form.get("list_name"))
        Title = request.form.get("title")
        Content = request.form.get("content")
        Deadline = datetime.strptime(request.form.get("deadline"), '%Y-%m-%d')
        Completed_switch = True
        Created_Date = datetime.now()
        

        if Deadline.date() < Created_Date.date():
            message = "Choose an appropriate deadline, deadline should be on or after this date. Please try again"
            return render_template("error.html", error_message = message, link = 'create_card')
        


        if request.form.get("completed_switch") is None:
            Completed_switch = False
            


        insert_list = List.query.get(List_Id)


        flag = True

        if len(Title) > 20:
            message = "Your card title should be only of 20 characters at max."
            return render_template("error.html", error_message = message, link = 'create_card')
            

        for cardd in insert_list.cards:
            if cardd.title == Title:
                flag = False
                break
            


        if (flag):
            c1 = Card(title = Title, content = Content, deadline = Deadline, created_date = Created_Date, last_updated = datetime.now(), completed_switch = Completed_switch, lists_id = List_Id)
            db.session.add(c1)
            db.session.commit()
            return redirect(url_for('dashboard'))

        else:
            message = "Choose a diffrent card name, the card from that name already exists in the list. Card name should not be same within a list"
            return render_template("error.html", error_message = message, link = 'create_card')
        


@app.route("/card/<int:card_id>/edit", methods = ["GET", "POST"])
@login_required
def edit_card(card_id):
    
    c = Card.query.get(card_id)
    listt = List.query.get(c.lists_id)
    
    if current_user.is_authenticated:
            listsss = current_user.lists


    listss = listsss.copy()
    listss.remove(listt)

            
    
    if request.method == "GET":
        return render_template("edit_card.html", card = c, lists = listss, lister = listt)

    if request.method == "POST":
        
        List_Id = int(request.form.get("list_name"))
        Title = request.form.get("title")
        Content = request.form.get("content")
        Deadline = datetime.strptime(request.form.get("deadline"), '%Y-%m-%d')
        Completed_Switch = True
        Last_Updated = datetime.now()



        if Deadline != c.deadline and Deadline.date() < Last_Updated.date():
            message = "Choose an appropriate deadline, In order to change deadline from previous one deadline should be on or after this date"
            return render_template("error_arg.html", error_message = message, link_name = 'card', id_list = card_id) 
        

        if request.form.get("completed_switch") is None:
            Completed_Switch = False
            


        insert_list = List.query.get(List_Id)
        
        flag = True


        for cardd in insert_list.cards:
            if cardd.title == Title and cardd.card_id != c.card_id:
                flag = False
                break

        if len(Title) > 20:
            message = "Your card title should be only of 20 characters at max."
            return render_template("error_arg.html", error_message = message, link_name = 'card', id_list = card_id)

        
        
        if (flag):
            c.title = Title
            c.content = Content
            c.deadline = Deadline
            c.completed_switch = Completed_Switch
            c.last_updated = Last_Updated
            c.lists_id = List_Id

            if Completed_Switch :
                c.completed_at = datetime.now()            
                    
            db.session.commit()

            return redirect(url_for('dashboard'))
            

        else:
            if List_Id != c.lists_id:
                message = "In order to move the card into a diffrent list please change the card title, the card from that title already exists in the choosen list. Card title should not be same within a list"
                return render_template("error_arg.html", error_message = message, link_name = 'card', id_list = card_id)


            else:
                message = "Choose a diffrent card title, the card from that name already exists in the list. Card title should not be same within a list"
                return render_template("error_arg.html", error_message = message, link_name = 'card', id_list = card_id) 

        
        



@app.route("/card/<int:card_id>/delete", methods = ["GET", "POST"])
@login_required
def delete_card(card_id):
    card = Card.query.get(card_id)
    db.session.delete(card)
    db.session.commit()

    return redirect(url_for('dashboard'))

            

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


@app.route("/dashboard/summary", methods = ["GET", "POST"])
@login_required
def summary():
    if current_user.is_authenticated:
            listss = current_user.lists

    current_time = datetime.now()

    list_dict = []

    for listt in listss:
        counter = 0

        x_c = []
        x_i = []
        x_d = []
        y_c = []
        y_i = []
        y_d = []
        labels = []
        color_c = []
        color_i = []
        color_d = []
        

        
        for card in listt.cards:
            
            if card.completed_switch :
                x_c.append(card.title)
                time_diff = abs(card.completed_at - card.created_date)
                y_c.append(round(time_diff.total_seconds()/60))
                labels.append(card.completed_at.strftime('%d-%b'))
                color_c.append("green")
                
                
                

            else:
                
                if card.deadline.date() >= current_time.date():
                    x_i.append(card.title)
                    time_diff = abs(current_time - card.created_date)
                    y_i.append(round(time_diff.total_seconds()/60))
                    color_i.append("orange")
                    
                   

                else:
                    x_d.append(card.title)
                    time_diff = abs(card.deadline - card.created_date)
                    y_d.append(round(time_diff.total_seconds()/60))
                    color_d.append("red")
                    
                    

        completed_tasks = len(x_c)
        inprogress_tasks = len(x_i)
        deadline_over_tasks = len(x_d)
        total_tasks = completed_tasks + inprogress_tasks + deadline_over_tasks
        
        if completed_tasks > 0:
            plt.bar(x_c, y_c, width = 0.4, color = color_c, label = "Completed")
        
        for i in range(len(x_c)):
            plt.text(i,y_c[i],labels[i], ha = 'center')


        if inprogress_tasks > 0:
            plt.bar(x_i, y_i, width = 0.4, color = color_i, label = "In-progress")


        if deadline_over_tasks > 0:
            plt.bar(x_d, y_d, width = 0.4, color = color_d, label = "Deadline Passed" )
            
        plt.title("Pictorial representation for status of tasks")
        plt.xlabel("Card Title")
        plt.ylabel("Time in Minutes")

        plt.margins(y =  0.2)


        plt.legend(loc='upper right')
        

        filename = str(listt.list_id)
        image_name = filename + ".png" 
        
        plt.savefig('static/' + filename)

        plt.clf()


        list_dict.append({"completed" : completed_tasks, "inprogress" : inprogress_tasks, "deadline" : deadline_over_tasks, "img_name" : image_name, "list_id": listt.list_id, "description" : listt.description, "name" : listt.name, "total_len" : total_tasks})


        
            
        
    return render_template("summary.html",lists = list_dict )
                    
                

            
            
            
            
    
if __name__ == "__main__" :
    app.run(debug = True)

    
