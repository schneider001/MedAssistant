from flask import Flask, request, redirect, url_for, render_template, jsonify
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

app = Flask(__name__)
app.static_folder = 'static'
#login_manager = LoginManager(app)

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
#@login_required
def main():
    patients = [
        "Иванов Иван Иванович",
        "Петров Петр Петрович",
        "Сидоров Сидор Сидорович",
        "Смирнов Алексей Андреевич",
        "Козлов Владимир Дмитриевич",
        "Морозов Олег Игоревич"
    ] #TODO Получить ФИО из БД

    symptoms = ['Высокая температура', 'Кашель', 'Насморк'] #TODO Получить из БД

    return render_template('index.html', patients=patients, symptoms=symptoms)


@app.route('/patients')
def patients():
    patients = [] #TODO Получить ФИО из БД
    return render_template('patients.html')

@app.route('/patient_card', methods=['POST'])
def patient_card():
    patientID = 0 #как то получается id пациента, потом доделаю
    #TODO Получить всю информацию о пациенте из БД, которая будет отображаться (возраст, и т.п., история запросов для этого пациента)
    return #Как то потом отобразится 


@app.route('/history')
def history():
    #TODO получить историю всех запросов для текущего авторизованного врача
    return render_template('history.html')


@app.route('/process_neural_network', methods=['POST'])
def process_neural_network():
    patientname = request.form['patientname']
    symptoms = request.form.getlist('symptoms')


if __name__ == "__main__":
    app.run(debug=True)
