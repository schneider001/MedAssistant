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
    try:
        user_id = current_user.id
        if user_id not in connected_users:
            connected_users[user_id] = set()
        connected_users[user_id].add(request.sid)
        emit('connected')
    except:
        emit('connect_error')


@socketio.on('disconnect')
@authenticated_only
def handle_disconnect():
    try:
        user_id = current_user.id
        if user_id in connected_users and request.sid in connected_users[user_id]:
            connected_users[user_id].remove(request.sid)
    except:
        emit('disconnect_error')


@socketio.on('join_room')
@authenticated_only
def handle_join_room(data):
    try:
        room_id = data['room_id']
        join_room(room_id)
    except:
        emit('join_room_error')


@socketio.on('leave_room')
@authenticated_only
def handle_leave_room(data):
    try:
        room_id = data['room_id']
        leave_room(room_id)
    except:
        emit('leave_room_error')


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
    oms = data.get('oms')
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
    
    response_data = ResponseData(
        id=request_id,
        patient_name=patient_name,
        doctor=current_user.name,
        symptoms=[symptom.ru_name for symptom in symptoms],
        diagnosis=disease.ru_name,
        doctor_comments=doctor_comments
    )
    
    return response_data.__dict__


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

    doctor_comments = [DoctorComment(id=comment_values[0],
                         doctor=comment_values[1], 
                         time=comment_values[2].strftime("%Y-%m-%d %H:%M:%S"),
                         comment=comment_values[3], 
                         editable=comment_values[4]) for comment_values in comments_values]

    response_data = ResponseData(
        id=request_id,
        patient_name=Patient.get_name_by_request_id(request_id),
        doctor=current_user.name, 
        symptoms=symptoms,
        diagnosis=diagnosis_ru_name,
        doctor_comments=doctor_comments
    )
    
    return response_data.__dict__


#----------------------------------DONE-3---------------------------------------------------
@app.route('/load_data_requests', methods=['GET'])
@login_required
def load_data_requests():
    """
    Получает список запросов для текущего пользователя для указанной страницы в пагинации с использованием поиска.
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком запросов для указанной страницы, включая id запроса, имя пациента, дату, предсказанный диагноз, информацию о комментариях докторов(Без комментариев/Прокомментирован).
    """
    term = request.args.get('search', '').lower()
    page = int(request.args.get('page', '1'))

    per_page = 100
    #limit = 25
    
    if (len(term) > 3):
        requests = Request.get_requests_page_by_doctor_id_contain_substr(current_user.id, per_page, term)
    else:
        requests = Request.get_requests_page_by_doctor_id(current_user.id, per_page)
        
    requests = [RequestData(id=request[0], name=request[1], date=request[2].strftime("%Y-%m-%d %H:%M:%S"), diagnosis=request[3], is_commented=request[4]) for request in requests]

    return jsonify({'results': [request.__dict__ for request in requests], 'pagination': {'more': False }})


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

    patient_data = PatientData(
        id=patient.id,
        name=patient.name,
        birthDate=patient.born_date.strftime("%Y-%m-%d"),
        age=age, 
        oms=patient.insurance_certificate,
        sex=patient.sex
    )

    photo_filename = f'./static/patient_images/{patient_id}.jpg'
    if os.path.exists(photo_filename):
        patient_data.photo_url = photo_filename

    return patient_data.__dict__

#---------------------------------------DONE-4-------------------------------------------
@app.route('/load_patient_history', methods=['GET'])
@login_required
def load_patient_history():
    """
    Получает список запросов для пациента по id пациента для указанной странице в пагинации.
    :param str patient_id: ID пациента.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком запросов для указанной страницы, которые включают id запроса, имя доктора, предсказанный диагноз, информацию о комментариях докторов(Без комментариев/Прокомментирован).
    """
    patient_id = request.args.get('search')
    if patient_id == '':
        return
    patient_id = int(patient_id)
    page = int(request.args.get('page', '1'))

    per_page = 100

    requests = Request.get_requests_page_by_patient_id(patient_id, per_page)
    requests = [RequestData(id=request[0], 
                            name=request[1], 
                            date=request[2].strftime("%Y-%m-%d %H:%M:%S"), 
                            diagnosis=request[3], 
                            is_commented=request[4]) for request in requests]

    return jsonify({'results': [request.__dict__ for request in requests], 'pagination': {'more': False}})


#---------------------------------------DONE-5-------------------------------------------
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
    comment_text = data['comment']
    
    user_id = current_user.id
    comment_id = Comment.add(user_id, request_id, comment_text)
    Request.update_is_commented(request_id, 1)
    comment = Comment.get_by_id(comment_id)
    if comment:
        response = CommentResponseData(id=comment.id, 
                               doctor=current_user.name, 
                               time=comment.date.strftime("%Y-%m-%d %H:%M:%S"), 
                               comment=comment_text)
    else:
        response = CommentResponseData()

    if user_id in connected_users:
        for sid in connected_users[user_id]:
            emit('self_added_comment', response.__dict__, to = sid)
        emit('added_comment', response.__dict__, room = room_id, skip_sid = list(connected_users[user_id]))

#---------------------------------------DONE-6-------------------------------------------
@socketio.on('delete_comment')
@authenticated_only
def delete_comment(data):
    """
    Удаляет комментарий по его id.
    :param int comment_id: ID комментария.
    :return: JSON-ответ с id комментария и именем текущего пользователя.
    """
    try:
        room_id = data['room_id']
        request_id = data['request_id']
        comment_id = data['comment_id']

        user_id = current_user.id
        if not Comment.validate_comment_author(comment_id, user_id):
            raise

        Comment.update_status_by_id('OLD', comment_id)
        is_commented = Comment.is_request_commented(request_id)
        #Request.update_is_commented(request_id, is_commented) #в бд на это есть триггер, можно убрать
        doctor_name = current_user.name

        response = CommentResponseData(id=comment_id, doctor=doctor_name)
        emit('deleted_comment', response.__dict__, room = room_id)
    except:
        emit('delete_comment_error')


#---------------------------------------TODO-7-------------------------------------------
@socketio.on('edit_comment')
@authenticated_only
def edit_comment(data):
    """
    Изменяет комментарий по его id.
    :param int comment_id: ID комментария.
    :param str comment: Текст комментария.
    :return: JSON-ответ с информацией о комментарии, включая id комментария, имя доктора, время, текст комментария, является ли текущий пользователь автором.
    """
    try:
        room_id = data['room_id']
        request_id = data['request_id']
        comment_id = data['comment_id']
        updated_comment_text = data['comment']

        user_id = current_user.id
        if not Comment.validate_comment_author(comment_id, user_id):
            raise

        Comment.update_status_by_id('OLD', comment_id)
        new_comment_id = Comment.add(user_id, request_id, updated_comment_text)

        comment = Comment.get_by_id(new_comment_id)
        if comment:
            response = CommentResponseData(id=comment.id, 
                                           old_id=comment_id, 
                                           doctor=current_user.name, 
                                           time=comment.date.strftime("%Y-%m-%d %H:%M:%S"), 
                                           comment=comment.comment)
        else:
            response = CommentResponseData()
        user_id = current_user.id
        if user_id in connected_users:
            for sid in connected_users[user_id]:
                emit('self_edited_comment', response.__dict__, to = sid)
            emit('edited_comment', response.__dict__, room = room_id, skip_sid = list(connected_users[user_id]))
    except:
        emit('edit_comment_error')

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
    birthdate = datetime.strptime(birthdate, '%d.%m.%Y')
    oms = request.form['oms']
    sex = request.form['sex']
    image = request.files.get('image')

    Patient.insert_new_patient(fullname, oms, birthdate, sex)
    id = Patient.get_id_by_insurance_certificate(oms)
    patient_data = PatientData(id=id, name=fullname, oms=oms)

    directory_path = './static/patient_images/'

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    if image:
        image.save(os.path.join(directory_path, f'{id}.jpg'))

    return patient_data.__dict__


@app.route('/load_patients', methods=['GET'])
@login_required
def load_patients():
    """
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком пациентов для указанной страницы, включая id пациента, имя, полис ОМС; также переменную more, указывающая о конце пагинации.
    """
    term = request.args.get('search', '')
    page = int(request.args.get('page', 1))


    per_page = 100
    limit = 20
    
    if (len(term) > 3):
        patients = Patient.find_all_search_lazyload(term, per_page)
    else:
        patients = Patient.find_all_id_name_insurance_certificate(per_page)
        
    patients = [PatientData(id=patient[0], name=patient[1], oms=patient[2]) for patient in patients]

    return jsonify({'results': [patient.__dict__ for patient in patients], 'pagination': {'more': False}})

@app.route('/load_symptoms', methods=['GET'])
@login_required
def load_symptoms():
    """
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком симптомов для указанной страницы, включая id симптома, название, также переменную more, указывающая о конце пагинации.
    """
    filter = request.args.get('search', '').lower()
    page = int(request.args.get('page', 1))

    per_page = 10

    symptoms = Symptom.find_all_symptoms()
    symptoms = [SymptomData(id=item[0], name=item[1].lower()) for item in symptoms]

    if filter != '':
        symptoms = [row for row in symptoms if filter in row.name]

    start = (page - 1) * per_page
    end = start + per_page
    filtered_data = symptoms[start:end]

    return jsonify({'results': [symptom.__dict__ for symptom in filtered_data], 'pagination': {'more': len(filtered_data) == per_page}})

if __name__ == "__main__":
    socketio.run(app, debug=True)
