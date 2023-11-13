from flask import request, redirect, url_for, render_template, jsonify, send_from_directory
from flask_login import login_required, login_user, logout_user, current_user
from flask_socketio import emit, join_room, leave_room, disconnect, rooms
import functools
import time
import os
import random

from init import *
from db_model import *


@login_manager.user_loader
def load_user(user_id):
    return Doctor.get_by_id(user_id)


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


connected_users = {}


@socketio.on('connect')
@authenticated_only
def handle_connect():
    user_id = current_user.id
    if user_id not in connected_users:
        connected_users[user_id] = set()
    connected_users[user_id].add(request.sid)
    emit('connected')


@socketio.on('disconnect')
@authenticated_only
def handle_disconnect():
    user_id = current_user.id
    if user_id in connected_users and request.sid in connected_users[user_id]:
        connected_users[user_id].remove(request.sid)


@socketio.on('join_room')
@authenticated_only
def handle_join_room(data):
    room_id = data['room_id']
    join_room(room_id)


@socketio.on('leave_room')
@authenticated_only
def handle_leave_room(data):
    room_id = data['room_id']
    leave_room(room_id)


@app.route('/static/js/<path:filename>')
def custom_static(filename):
    return send_from_directory('static/js', filename, mimetype='text/javascript')


@app.route("/")
def login():
    """
    Отображает страницу входа.
    :return: HTML-шаблон страницы входа.
    """
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login_post():
    """
    Обрабатывает данные, отправленные при попытке входа.
    :param str username: Имя пользователя, отправленное из формы входа.
    :param str password: Пароль, отправленный из формы входа.
    :return: Возвращает результат аутентификации.
    """
    username = request.form['username']
    password = request.form['password']

    doctor = Doctor.get_by_username(username)
    authorized = doctor and check_password_hash(doctor.password_hash, password)
 
    if authorized:
        login_user(doctor)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})
    
    
@app.route("/logout")
@login_required
def logout():
    """
    Обрабатывает выход из аккаунта
    :return: Перенаправляет на страницу входа в аккаунт.
    """
    logout_user()
    return redirect(url_for('login'))


@app.route('/main')
@login_required
def main():
    """
    Отображает главную страницу с данными о пациентах и симптомах.
    :return: HTML-шаблон главной страницы.
    """
    return render_template('index.html')


@app.route('/patients')
@login_required
def patients():
    """
    Отображает страницу с пациентами.
    :return: HTML-шаблон страницы с пациентами.
    """
    return render_template('patients.html')


@app.route('/history')
@login_required
def history():
    """
    Отображает страницу с историей запросов.
    :return: HTML-шаблон страницы с историей запросов.
    """
    return render_template('history.html')

#---------------------------------------DONE-1--------------------------------------------
@app.route('/get_request_info', methods=['POST'])
@login_required
def get_request_info():
    """
    Получает диагноз с помощью модели и возвращает информацию об этом запросе.
    :param str id: ID пациента.
    :param str name: Полное имя пациента.
    :param str oms: Полис ОМС пациента.
    :param list symptoms: Список симптомов.
    :return: JSON-ответ с информацией для карточки запроса, включая id запроса, имя пациента, имя доктора, симптомы, предсказанный диагноз, комментарии врачей.
    """
    data = request.get_json()

    patient_id = data.get('id')
    patient_name = data.get('name')
    snils = data.get('snils')
    symptom_ids = data.get('symptoms')
    
    symptoms = [Symptom.get_by_id(id) for id in symptom_ids]
    
    request_id = Request.add(current_user.id, 
                             patient_id, 
                             [symptom.id for symptom in symptoms], #symptom_ids
                             ML_MODEL_VERSION)

    disease_name = get_disease([symptom.name for symptom in symptoms])
    
    disease = Disease(None, None, None)
    
    if disease_name:
        status = 'READY'
        disease = Disease.get_by_name(disease_name)
    else:
        status = 'ERROR'
    
    Request.update_status(request_id, status, disease.id)
    doctor_comments = []
    
    response_data = {
        "id": request_id,
        "patient_name": patient_name,
        "doctor": current_user.name, 
        "symptoms": [symptom.ru_name for symptom in symptoms],
        "diagnosis": disease.ru_name,
        "doctor_comments": doctor_comments
    }
    
    return jsonify(response_data)

#------------------------------------------DONE-2----------------------------------------
@app.route('/get_request_info_by_id', methods=['POST'])
@login_required
def get_request_info_by_id():
    """
    Получает возвращает информацию о запросе по его id из БД.
    :param str request_id: ID запроса.
    :return: JSON-ответ с информацией для карточки запроса, включая id запроса имя пациента, имя доктора, симптомы, предсказанный диагноз, комментарии врачей.
    """
    data = request.get_json()

    request_id = data.get('request_id')

    symptoms = Request.get_symptom_ru_names(request_id)
    diagnosis_ru_name = Request.get_disease_ru_name(request_id)
    comments_values = Comment.get_comments_by_request_id(request_id, current_user.id)
    doctor_comments = [{"id": 1,
                        "doctor": comment_values[0], 
                        "time": comment_values[1], 
                        "comment": comment_values[2], 
                        "editable": comment_values[3]} for comment_values in comments_values]

    response_data = {
        "id": request_id,
        "patient_name": Patient.get_name_by_request_id(request_id),
        "doctor": current_user.name, 
        "symptoms": symptoms,
        "diagnosis": diagnosis_ru_name,
        "doctor_comments": doctor_comments
    }
    
    return jsonify(response_data)


@app.route('/load_data_patients', methods=['GET'])
@login_required
def load_data_patients():
    """
    Получает список пациентов для указанной страницы в пагинации с использованием поиска.
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком пациентов для указанной страницы, включая id пациента, имя, Полис ОМС.
    """
    search_text = request.args.get('search', '').lower()
    page = int(request.args.get('page'))

    per_page = 15

    data = [[i, f'Name {i}', f'oms {i}'] for i in range(1, 101)]

    if search_text == '':
        filtered_data = data
    else:
        filtered_data = [] #TODO тут нужно реализовать поиск по бд с учетом страницы, я тут фильтрую и отбираю нужные элементы из массива для примера, но в идеале, если это возможно, это надо сделать средствами SQL
        for row in data:
            row_text = ' '.join(map(str, row)).lower()
            if search_text in row_text:
                filtered_data.append(row)

    start = (page - 1) * per_page
    end = start + per_page

    paginated_data = filtered_data[start:end]

    return jsonify(paginated_data)

#----------------------------------DONE-3---------------------------------------------------
@app.route('/load_data_requests', methods=['GET'])
@login_required
def load_data_requests():
    """
    Получает список запросов для текущего полTODOьзователя для указанной страницы в пагинации с использованием поиска.
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком запросов для указанной страницы, включая id запроса, имя пациента, дату, предсказанный диагноз, информацию о комментариях докторов(Без комментариев/Прокомментирован).
    """
    search_text = request.args.get('search', '').lower()
    page = int(request.args.get('page'))

    per_page = 15

    return jsonify(Request.get_requests_page_by_doctor_id_contain_substr(current_user.id, page, per_page, search_text))


@app.route('/get_patient_info', methods=['GET'])
@login_required
def get_patient_info():
    """
    Получает информацию о пациенте по его id.
    :param str patient_id: ID пациента.
    :return: JSON-ответ с информацией о пациенте, включая его id, полное имя, дату рождения, текущий возраст, Полис ОМС, пол.
    """
    patient_id = request.args.get('patient_id')

    patient = Patient.get_by_id(patient_id)
    if not patient:
        error_message = {"error": "Ошибка", "message": "Пациента не существует."}
        response = jsonify(error_message)
        response.status_code = 400
        return response
    
    today = datetime.now()
    age = today.year - patient.born_date.year - \
        ((today.month, today.day) < (patient.born_date.month, patient.born_date.day))

    patient_data = {
        'id': patient.id,
        'name': patient.name,
        'birthDate': patient.born_date.strftime("%Y-%m-%d"),
        'age': age, 
        'oms': patient.insurance_certificate,
        'sex' : patient.sex,
    }

    photo_filename = f'./static/patient_images/{patient_id}.jpg'
    if os.path.exists(photo_filename):
        patient_data['photo_url'] = photo_filename

    return jsonify(patient_data)

#---------------------------------------TODO--------------------------------------------
@app.route('/load_patient_history', methods=['GET'])
@login_required
def load_patient_history():
    """
    Получает список запросов для пациента по id пациента для указанной странице в пагинации.
    :param str patient_id: ID пациента.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком запросов для указанной страницы, которые включают id запроса, имя доктора, предсказанный диагноз, информацию о комментариях докторов(Без комментариев/Прокомментирован).
    """
    patient_id = int(request.args.get('search'))
    page = int(request.args.get('page'))

    per_page = 15

    data = Request.get_requests_page_by_patient_id(patient_id, page, per_page)

    return jsonify(data)

#---------------------------------------TODO--------------------------------------------
@socketio.on('add_comment')
@authenticated_only
def add_comment(data):
    """
    Добавляет новый комментарий для указанного запроса в БД.
    :param str request_id: ID запроса.
    :param str comment: Текст комментария.
    :return: JSON-ответ с информацией о комментарии, включая id комментария, имя доктора, время, текст комментария, является ли текущий пользователь автором.
    """
    room_id = data['room_id']
    request_id = data['request_id']
    comment = data['comment']
    #TODO добавить комментарий в БД

    response = {"id": random.randint(1, 1000), "doctor": "Dr. Smith", "time": "10:30", "comment": comment}
    user_id = current_user.id
    if user_id in connected_users:
        for sid in connected_users[user_id]:
            emit('self_added_comment', response, to = sid)
        emit('added_comment', response, room = room_id, skip_sid = list(connected_users[user_id]))

#---------------------------------------TODO--------------------------------------------
@socketio.on('delete_comment')
@authenticated_only
def delete_comment(data):
    """
    Удаляет комментарий по его id.
    :param int comment_id: ID комментария.
    :return: JSON-ответ с id комментария и именем текущего пользователя.
    """
    room_id = data['room_id']
    comment_id = data['comment_id']

    #TODO удалить коммент из БД
    doctorName = "Dr. Smith"

    response = {"id": comment_id, "doctor": doctorName}
    emit('deleted_comment', response, room = room_id)

#---------------------------------------TODO--------------------------------------------
@socketio.on('edit_comment')
@authenticated_only
def edit_comment(data):
    """
    Изменяет комментарий по его id.
    :param int comment_id: ID комментария.
    :param str comment: Текст комментария.
    :return: JSON-ответ с информацией о комментарии, включая id комментария, имя доктора, время, текст комментария, является ли текущий пользователь автором.
    """
    room_id = data['room_id']
    comment_id = data['comment_id']
    updated_comment = data['comment']

    #TODO изменить коммента в БД и после вернуть его
    response = {"id": comment_id, "doctor": "Dr. Smith", "time": "10:30", "comment": updated_comment}
    user_id = current_user.id
    if user_id in connected_users:
        for sid in connected_users[user_id]:
            emit('self_edited_comment', response, to = sid)
        emit('edited_comment', response, room = room_id, skip_sid = list(connected_users[user_id]))    


@app.route('/create_patient', methods=['POST'])
@login_required
def create_patient():
    """
    Создает нового пациента.
    :param str fullname: Имя пациента.
    :param str birthdate: Дата рождения.
    :param str oms: Полис ОМС пациента.
    :param image image: Изображение пациента.
    :return: JSON-ответ с информацией о пациенте, включая id пациента, имя пациента, Полис ОМС.
    """
    fullname = request.form['fullname']
    birthdate = request.form['birthdate']
    oms = request.form['oms']
    sex = request.form['sex']
    image = request.files.get('image')

    Patient.insert_new_patient(fullname, oms, birthdate, sex)
    id = Patient.get_id_by_insurance_certificate(oms)

    if image:
        image.save(f'./static/patient_images/{id}.jpg')

    return jsonify({'id': id, 'name': fullname, 'oms': oms})


@app.route('/load_patients', methods=['GET'])
@login_required
def load_patients():
    """
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком пациентов для указанной страницы, включая id пациента, имя, полис ОМС; также переменную more, указывающая о конце пагинации.
    """
    #TODO сейчас есть похожая функция для таблицы, но в этой появляется обязательная переменная more, в будущем планирую убрать старую функцию без more и переиспользовать эту
    term = request.args.get('search', '')
    page = int(request.args.get('page', 1))

    per_page = 15
    start = (page - 1) * per_page
    end = start + per_page

    time.sleep(1)
    patients_in_db = [
        {"id": 1 ,"name": "Иванов Иван Иванович", "oms": "1234 4562 7894 5410" },
        {"id": 2 ,"name": "Петров Петр Петрович", "oms": "3424 2321 5334 1434" },
        {"id": 3 ,"name": "Сидоров Сидор Сидорович", "oms": "6534 3242 7665 3243" },
        {"id": 4 ,"name": "Смирнов Алексей Андреевич", "oms": "2324 6354 3324 2234" },
        {"id": 5 ,"name": "Козлов Владимир Дмитриевич", "oms": "4321 3321 6254 1243" },
        {"id": 6 ,"name": "Морозов Олег Игоревич", "oms": "4322 7165 1234 2332" }
    ] #TODO получать пациентов из БД

    filtered_patients = list(filter(lambda p: term in p["name"] or term in p["oms"], patients_in_db))
    patients = filtered_patients[start:end] #Нужно опять же из БД получить нужную страницу с пациентами

    return jsonify({'results': patients, 'pagination': {'more': end < len(filtered_patients)}}) #и при этом нужно как то понять, была ли это последняя страница


@app.route('/load_symptoms', methods=['GET'])
@login_required
def load_symptoms():
    """
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком симптомов для указанной страницы, включая id симптома, название, также переменную more, указывающая о конце пагинации.
    """
    filter = request.args.get('search', '')
    page = int(request.args.get('page', 1))

    per_page = 15
    
    symptoms = Symptom.get_page_by_filter(filter, page, per_page)
    symptoms = [{'id': item[0], 'name': item[1]} for item in symptoms]
    symptoms_count = Symptom.get_count_by_filter(filter)[0][0]
    more = page * per_page < symptoms_count

    return jsonify({'results': symptoms, 'pagination': {'more': more}})



if __name__ == "__main__":
    socketio.run(app, debug=True)
