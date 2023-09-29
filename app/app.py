from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__)


@app.route("/")
def login():
    return render_template("login.html")


@app.route('/', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    #TODO
    authorized = True
 
    if authorized:
        return redirect(url_for('main'))
    else:
        return redirect(url_for('login'))


@app.route('/main')
def main():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
