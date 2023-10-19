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


@app.route('/logout')
def logout():


    return redirect(url_for("login"))


@app.route('/patients')
def patients():
    columns = ['id', 'name']

    return render_template('patients.html', columns=columns)


@app.route('/history')
def history():
    columns = ['id', 'name', 'date', 'result']
    #TODO получить историю всех запросов для текущего авторизованного врача
    return render_template('history.html', columns=columns)


@app.route('/get_request_info', methods=['POST'])
def get_request_info():
    patientname = request.form['patientname']
    symptoms = request.form.getlist('symptoms')
    time.sleep(1)
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


@app.route('/get_request_info_by_id', methods=['GET'])
def get_request_info_by_id():
    request_id = request.args.get('request_id')

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

    data = [[i, f'Doctor Name {i}', f'Date {i}', f'Predicted Result {i}', f'Doctor Verdict {i}'] for i in range(1, 17)] #Пример какой то таблицы

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


if __name__ == "__main__":
    app.run(debug=True)
