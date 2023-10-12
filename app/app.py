from flask import Flask, request, redirect, url_for, render_template, jsonify
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
import time


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


@app.route('/process_request', methods=['POST'])
def process_request():
    patientname = request.form['patientname']
    symptoms = request.form.getlist('symptoms')
    time.sleep(5)
    diagnosis = "Some Diagnosis"
    doctor_comments = [{"doctor": "Dr. Smith", "time": "10:30 AM", "comment": "Comment 1"},
                      {"doctor": "Dr. Johnson", "time": "11:15 AM", "comment": "Comment 2"}]
    
    response_data = {
        "diagnosis": diagnosis,
        "doctor_comments": doctor_comments
    }
    
    return jsonify(response_data)


@app.route('/load_data_patients', methods=['GET'])
def load_data_patients():
    data = [[i, f'Name {i}'] for i in range(1, 101)]  # Пример какой-то таблицы
    search_text = request.args.get('search', '').lower()

    if search_text == '':
        filtered_data = data
    else:
        filtered_data = [] #TODO тут нужно реализовать поиск по бд с учетом страницы, я тут фильтрую и отбираю нужные элементы из массива для примера, но в идеале, если это возможно, это надо сделать средствами SQL
        for row in data:
            row_text = ' '.join(map(str, row)).lower()
            if search_text in row_text:
                filtered_data.append(row)

    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    start = (page - 1) * per_page
    end = start + per_page

    paginated_data = filtered_data[start:end]

    return jsonify(paginated_data)


@app.route('/load_data_requests', methods=['GET'])
def load_data_requests():
    data = [[i, f'Name {i}', f'Date {i}', f'Result {i}'] for i in range(1, 156)] #Пример какой то таблицы TODO нужен еще столбец с id пациента для запросов на сервер
    search_text = request.args.get('search', '').lower()

    if search_text == '':
        filtered_data = data
    else:
        filtered_data = [] #TODO тут нужно реализовать поиск по бд с учетом страницы, я тут фильтрую и отбираю нужные элементы из массива для примера, но в идеале, если это возможно, это надо сделать средствами SQL
        for row in data:
            row_text = ' '.join(map(str, row)).lower()
            if search_text in row_text:
                filtered_data.append(row)

    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    start = (page - 1) * per_page
    end = start + per_page

    paginated_data = filtered_data[start:end]

    time.sleep(2) # Эмуляция задержки ответа от сервера, для тестов

    return jsonify(paginated_data)


@app.route('/get_patient_info', methods=['GET'])
def get_patient_info():
    patient_id = request.args.get('patient_id')

    patient_data = { #TODO как то получаем информацию о пациенте из БД
        'id': patient_id,
        'name': 'Иванов Иван Иванович',
        'birthDate': '1990-05-15',
        'age': 33, #TODO вычислить возраст
        'snils': '480 953 512 08'
    }

    return jsonify(patient_data)


@app.route('/load_patient_history', methods=['GET'])
def load_patient_history():
    patient_id = int(request.args.get('search'))

    data = [[i, f'Doctor Name {i}', f'Date {i}', f'Predicted Result {i}', f'Doctor Verdict {i}'] for i in range(1, 17)] #Пример какой то таблицы

    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    start = (page - 1) * per_page
    end = start + per_page

    return jsonify(data[start:end])


if __name__ == "__main__":
    app.run(debug=True)
