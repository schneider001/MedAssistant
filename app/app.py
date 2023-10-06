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
    columns = ['id', 'name']

    return render_template('patients.html', columns=columns)

@app.route('/patient_card', methods=['POST'])
def patient_card():
    patientID = 0 #как то получается id пациента, потом доделаю
    #TODO Получить всю информацию о пациенте из БД, которая будет отображаться (возраст, и т.п., история запросов для этого пациента)
    return #Как то потом отобразится 


@app.route('/history')
def history():
    columns = ['id', 'name', 'date', 'result']
    #TODO получить историю всех запросов для текущего авторизованного врача
    return render_template('history.html', columns=columns)


@app.route('/process_neural_network', methods=['POST'])
def process_neural_network():
    patientname = request.form['patientname']
    symptoms = request.form.getlist('symptoms')


@app.route('/load_data_patients', methods=['GET'])
def load_data_patients():
    data = [{'id': i, 'name': f'Name {i}'} for i in range(1, 101)] #Пример какой то таблицы

    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    start = (page - 1) * per_page
    end = start + per_page

    paginated_data = data[start:end]

    return jsonify(paginated_data)


@app.route('/load_data_requests', methods=['GET'])
def load_data_requests():
    data = [{'id': i, 'name': f'Name {i}', 'date': f'Date {i}', 'result': f'Result {i}'} for i in range(1, 156)] #Пример какой то таблицы

    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    start = (page - 1) * per_page
    end = start + per_page

    paginated_data = data[start:end]

    return jsonify(paginated_data)


if __name__ == "__main__":
    app.run(debug=True)
