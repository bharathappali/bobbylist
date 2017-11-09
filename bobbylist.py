from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def initiate_launch():
    return render_template("index.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("index.html")
    if request.method == 'POST':
        email = request.form['signup_email']
        password = request.form['signup_password']
        return render_template("home.html")

if __name__ == '__main__':
    app.run()