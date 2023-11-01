from flask import Flask, request, redirect, url_for, render_template, jsonify, send_from_directory
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
import time


app = Flask(__name__)
app.static_folder = 'static'
#login_manager = LoginManager(app)

@app.route('/static/js/<path:filename>')
def custom_static(filename):
    return send_from_directory('static/js', filename, mimetype='text/javascript')

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
        {"name": "Иванов Иван Иванович", "snils": "123-456-789 10" },
        {"name": "Петров Петр Петрович", "snils": "342-231-534 14" },
        {"name": "Сидоров Сидор Сидорович", "snils": "654-342-765 43" },
        {"name": "Смирнов Алексей Андреевич", "snils": "234-654-324 34" },
        {"name": "Козлов Владимир Дмитриевич", "snils": "432-321-654 43" },
        {"name": "Морозов Олег Игоревич", "snils": "432-765-234 32" }
    ] #TODO Получить ФИО из БД

    symptoms = ['Высокая температура', 'Кашель', 'Насморк'] #TODO Получить из БД

    return render_template('index.html', patients=patients, symptoms=symptoms)


@app.route('/logout')
def logout():


    return redirect(url_for("login"))


@app.route('/patients')
def patients():
    columns = ['id', 'name', 'snils']

    return render_template('patients.html', columns=columns)


@app.route('/history')
def history():
    columns = ['id', 'name', 'date', 'result']
    #TODO получить историю всех запросов для текущего авторизованного врача
    return render_template('history.html', columns=columns)


@app.route('/get_request_info', methods=['POST'])
def get_request_info():
    data = request.get_json()

    patient_id = data.get('id')
    patientname = data.get('name')
    snils = data.get('snils')
    symptoms = data.get('symptoms')

    time.sleep(1)
    symptoms = ["Кашель", "Высокая температура"]
    diagnosis = "Cancer"
    doctor_comments = [{"id": 1, "doctor": "Dr. Robert", "time": "10:30", "comment": "Hmm, This diagnosis looks cool", "editable": False}, #editable true, если это комментарий текущего доктора
                       {"id": 2, "doctor": "Dr. Johnson", "time": "11:15", "comment": "Really cool", "editable": False},
                       {"id": 3, "doctor": "Dr. Hudson", "time": "12:05", "comment": "Thanks", "editable": False},
                       {"id": 4, "doctor": "Dr. Mycac", "time": "12:06", "comment": "WTF", "editable": False},
                       {"id": 5, "doctor": "Dr. tEST", "time": "12:06", "comment": "LONG COMMENT LONG COMMENT LONG COMMENT LONG COMMENT LONG COMMENT LONG COMMENT LONG COMMENT LONG COMMENT LONG COMMENT LONG COMMENT", "editable": False}]
    
    response_data = {
        "patient_name": patientname,
        "doctor": "Dr. Smith", #Имя текущего доктора
        "symptoms": symptoms,
        "diagnosis": diagnosis,
        "doctor_comments": doctor_comments
    }
    
    return jsonify(response_data)


@app.route('/get_request_info_by_id', methods=['POST'])
def get_request_info_by_id():
    data = request.get_json()
    request_id = data.get('request_id')

    symptoms = ["Кашель", "Высокая температура"]
    diagnosis = "Cancer"
    doctor_comments = [{"id": 1, "doctor": "Dr. Robert", "time": "10:30", "comment": "Hmm, This diagnosis looks cool", "editable": False}, #editable true, если это комментарий текущего доктора
                       {"id": 2, "doctor": "Dr. Johnson", "time": "11:15", "comment": "Really cool", "editable": False},
                       {"id": 3, "doctor": "Dr. Hudson", "time": "12:05", "comment": "Thanks", "editable": False},
                       {"id": 4, "doctor": "Dr. Mycac", "time": "12:06", "comment": "WTF", "editable": False},
                       {"id": 5, "doctor": "Dr. tEST", "time": "12:06", "comment": "LONG COMMENT LONG COMMENT LONG COMMENT LONG COMMENT LONG COMMENT LONG COMMENT LONG COMMENT LONG COMMENT LONG COMMENT LONG COMMENT", "editable": False}]
    
    response_data = {
        "patient_name": "Иван Иванов Иванович",
        "doctor": "Dr. Smith", #Имя текущего доктора
        "symptoms": symptoms,
        "diagnosis": diagnosis,
        "doctor_comments": doctor_comments
    }
    
    return jsonify(response_data)


@app.route('/load_data_patients', methods=['GET'])
def load_data_patients():
    data = [[i, f'Name {i}', f'snils {i}'] for i in range(1, 101)]  # Пример какой-то таблицы
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

    time.sleep(2)

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

    data = [[i, f'Doctor Name {i}', f'Date {i}', f'Predicted Result {i}', f'Doctor Verdict {i}'] for i in range(1, 170)] #Пример какой то таблицы

    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    start = (page - 1) * per_page
    end = start + per_page

    return jsonify(data[start:end])


@app.route('/add_comment', methods=['GET'])
def add_comment():
    comment = request.args.get('comment')
    #TODO добавить комментарий в БД
    return jsonify({"id": 1, "doctor": "Dr. Smith", "time": "10:30", "comment": comment, "editable": True})


@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    #TODO удалить коммент из БД
    doctorName = "Dr. Smith"
    return jsonify(doctorName)


@app.route('/edit_comment/<int:comment_id>', methods=['POST'])
def edit_comment(comment_id):
    updated_comment = request.form.get('comment')
    #TODO изменить коммента в БД и после вернуть его
    return jsonify({"id": 1, "doctor": "Dr. Smith", "time": "10:30", "comment": updated_comment, "editable": True})


@app.route('/create_patient', methods=['POST'])
def create_patient():
    fullname = request.form['fullname']
    birthdate = request.form['birthdate']
    snils = request.form['snils']
    #TODO сохраняем в бд, возвращаем id из базы и полное имя
    return jsonify({'id': 100, 'name': fullname, 'snils': snils})


@app.route('/load_patients', methods=['GET'])
def load_patients():
    term = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 15
    start = (page - 1) * per_page
    end = start + per_page

    time.sleep(1)
    patients_in_db = [
        {"id": 1 ,"name": "Иванов Иван Иванович", "snils": "123-456-789 10" },
        {"id": 2 ,"name": "Петров Петр Петрович", "snils": "342-231-534 14" },
        {"id": 3 ,"name": "Сидоров Сидор Сидорович", "snils": "654-342-765 43" },
        {"id": 4 ,"name": "Смирнов Алексей Андреевич", "snils": "234-654-324 34" },
        {"id": 5 ,"name": "Козлов Владимир Дмитриевич", "snils": "432-321-654 43" },
        {"id": 6 ,"name": "Морозов Олег Игоревич", "snils": "432-765-234 32" }
    ] #TODO получать пациентов из БД

    filtered_patients = list(filter(lambda p: term in p["name"] or term in p["snils"], patients_in_db))
    patients = filtered_patients[start:end] #Нужно опять же из БД получить нужную страницу с пациентами

    return jsonify({'results': patients, 'pagination': {'more': end < len(filtered_patients)}}) #и при этом нужно как то понять, была ли это последняя страница


if __name__ == "__main__":
    app.run(debug=True)
