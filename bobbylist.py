from flask import Flask, render_template, request
from flask_triangle import Triangle
from flask_mail import Mail, Message
import hashlib
from pymongo import MongoClient

app = Flask(__name__, static_path='/static')
Triangle(app)


app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME = 'noreply.bobbylist@gmail.com',
    MAIL_PASSWORD = 'BobbylistBobbylistnoreplynoreply'
)

mongo_client = MongoClient('localhost',27017)
bobbylistdb = mongo_client['bobbylist']



mail = Mail(app)

def send_mail(recipients_list, activation_link):
    msg = mail.send_message(
        'Your activation link',
        sender='noreply.bobbylist@gmail.com',
        recipients=recipients_list,
        body="Please click on this link http://127.0.0.1:5000/confirm/"+activation_link
    )
    return 'Mail sent'


@app.route('/')
def initiate_launch():
    return render_template("dashboard.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("index.html")
    if request.method == 'POST':
        login_email = request.form['login_email']
        login_password = request.form['login_password']
        return render_template("heyitsme.html")

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template("index.html")
    if request.method == 'POST':
        signup_email = request.form['signup_email']
        signup_password = request.form['signup_password']
        hashemail = hashlib.sha256(signup_email.encode('utf-8')).hexdigest()
        hashpwd = hashlib.sha256(signup_password.encode('utf-8')).hexdigest()
        verfication_hash_dict = {}
        verfication_hash_dict['email'] = signup_email
        verfication_hash_dict['hashemail'] = hashemail
        verfication_hash_dict['hashpwd'] = hashpwd
        verfication_hash_dict['checked'] = False
        recepients = []
        recepients.append(signup_email)
        send_mail(recepients, hashemail)
        if bobbylistdb.email_verification.find_one({"hashemail":hashemail},{"_id":0}) == None:
            bobbylistdb.email_verification.insert(verfication_hash_dict)
        else:
            return render_template("verification.html", again_signup=True)
        return render_template("verification.html", again_signup=False)

@app.route('/confirm/<verify_link>')
def verifylink(verify_link):
    user_verifilist = bobbylistdb.email_verification.find_one({"hashemail":verify_link},{"_id":0})
    if user_verifilist['checked'] == False:
        return render_template("heyitsme.html", user_email= user_verifilist['email'])
    else:
        user_db = bobbylistdb.users.find_one({"user_email":user_verifilist['email']},{"_id":0})
        return render_template("dashboard.html", newuser=False, user_details = user_db)

@app.route('/user_creation',  methods=['GET','POST'])
def create_user():
    if request.method == 'GET':
        return render_template("index.html")
    if request.method == 'POST':
        signup_dict = {}
        signup_dict['firstname_signup'] = request.form['firstnameinput']
        signup_dict['lastname_signup'] = request.form['lastnameinput']
        signup_dict['username_signup'] = request.form['usernameinput']
        signup_dict['email_signup'] = request.form['emailinput']
        user_verify_table_record = bobbylistdb.email_verification.find_one({"email":signup_dict['email_signup']},{"_id":0})
        signup_dict['hashpwd_signup'] = user_verify_table_record['hashpwd']
        signup_dict['checked_signup'] = user_verify_table_record['checked']
        bobbylistdb.users.insert(signup_dict)
        user_db = bobbylistdb.users.find_one({"user_email": signup_dict['email_signup']}, {"_id": 0})
        return render_template("dashboard.html", newuser=True, user_details = user_db)


if __name__ == '__main__':
    app.run()