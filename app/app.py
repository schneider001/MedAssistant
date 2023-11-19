from flask import request, redirect, url_for, render_template, jsonify, send_from_directory
from flask_login import login_required, login_user, logout_user
import time

from init import *
from db_model import *

@login_manager.user_loader
def load_user(user_id):
    return Doctor.get_by_id(user_id)


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


@app.route('/', methods=['POST'])
def login_post():
    """
    Обрабатывает данные, отправленные при попытке входа.
    :param str username: Имя пользователя, отправленное из формы входа.
    :param str password: Пароль, отправленный из формы входа.
    :return: Перенаправляет пользователя на страницу 'main' в случае успешного входа, или на страницу 'login' при ошибке.
    """
    username = request.form['username']
    password = request.form['password']

    doctor = Doctor.get_by_username(username)
    authorized = doctor and check_password_hash(doctor.password_hash, password)
 
    if authorized:
        login_user(doctor)
        return redirect(url_for('main'))
    else:
        return redirect(url_for('login'))
    
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
    :return: HTML-шаблон главной страницы с симптомами.
    """
    symptoms = ['Высокая температура', 'Кашель', 'Насморк'] #TODO Получить из БД

    return render_template('index.html', symptoms=symptoms)





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


@app.route('/get_request_info', methods=['POST'])
def get_request_info():
    """
    Получает диагноз с помощью модели и возвращает информацию об этом запросе.
    :param str id: ID пациента.
    :param str name: Полное имя пациента.
    :param str snils: СНИЛС пациента.
    :param list symptoms: Список симптомов.
    :return: JSON-ответ с информацией для карточки запроса, включая имя пациента, имя доктора, симптомы, предсказанный диагноз, комментарии врачей.
    """
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
    """
    Получает возвращает информацию о запросе по его id из БД.
    :param str request_id: ID запроса.
    :return: JSON-ответ с информацией для карточки запроса, включая имя пациента, имя доктора, симптомы, предсказанный диагноз, комментарии врачей.
    """
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
    """
    Получает список пациентов для указанной страницы в пагинации с использованием поиска.
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :param str per_page: Количество пациентов на странице.
    :return: JSON-ответ со списком пациентов для указанной страницы, включая id пациента, имя, СНИЛС.
    """
    search_text = request.args.get('search', '').lower()
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))

    data = [[i, f'Name {i}', f'snils {i}'] for i in range(1, 101)]  # Пример какой-то таблицы

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


@app.route('/load_data_requests', methods=['GET'])
def load_data_requests():
    """
    Получает список запросов для текущего пользователя для указанной страницы в пагинации с использованием поиска.
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :param str per_page: Количество запросов на странице.
    :return: JSON-ответ со списком запросов для указанной страницы, включая id запроса, имя пациента, дату, предсказанный диагноз, информацию о комментариях докторов(Без комментариев/Прокомментирован).
    """
    search_text = request.args.get('search', '').lower()
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))

    data = [[i, f'Name {i}', f'Date {i}', f'Result {i}', 'Без комментариев'] for i in range(1, 156)] #Пример какой то таблицы
    
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

    time.sleep(2) # Эмуляция задержки ответа от сервера, для тестов

    return jsonify(paginated_data)


@app.route('/get_patient_info', methods=['GET'])
@login_required
def get_patient_info():
    """
    Получает информацию о пациенте по его id.
    :param str patient_id: ID пациента.
    :return: JSON-ответ с информацией о пациенте, включая его id, полное имя, дату рождения, текущий возраст, СНИЛС.
    """
    patient_id = request.args.get('patient_id')

    patient = Patient.get_by_id(patient_id)
    if patient:
        today = datetime.now()
        age = today.year - patient.born_date.year - \
            ((today.month, today.day) < (patient.born_date.month, patient.born_date.day))
        patient_data = {
            'id': patient.id, #TODO Сделать невидимым во фронте
            'name': patient.name,
            'birthDate': patient.born_date.strftime("%Y-%m-%d"),
            'age': age, 
            'snils': patient.insurance_certificate,
            'sex' : patient.sex, #Не используется пока
        }

    return jsonify(patient_data)


@app.route('/load_patient_history', methods=['GET'])
def load_patient_history():
    """
    Получает список запросов для пациента по id пациента для указанной странице в пагинации.
    :param str patient_id: ID пациента.
    :param str page: Номер страницы.
    :param str per_page: Количество запросов на странице.
    :return: JSON-ответ со списком запросов для указанной страницы, которые включают id запроса, имя доктора, предсказанный диагноз, информацию о комментариях докторов(Без комментариев/Прокомментирован).
    """
    patient_id = int(request.args.get('search'))
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))

    data = [[i, f'Doctor Name {i}', f'Date {i}', f'Predicted Result {i}', f'Без комментариев'] for i in range(1, 170)] #Пример какой то таблицы

    start = (page - 1) * per_page
    end = start + per_page

    return jsonify(data[start:end])


@app.route('/add_comment', methods=['GET'])
def add_comment():
    """
    Добавляет новый комментарий для указанного запроса в БД.
    :param str request_id: ID запроса.
    :param str comment: Текст комментария.
    :return: JSON-ответ с информацией о комментарии, включая id комментария, имя доктора, время, текст комментария, является ли текущий пользователь автором.
    """
    request_id = request.args.get('request_id')
    comment = request.args.get('comment')

    #TODO добавить комментарий в БД
    return jsonify({"id": 1, "doctor": "Dr. Smith", "time": "10:30", "comment": comment, "editable": True})


@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    """
    Удаляет комментарий по его id.
    :param int comment_id: ID комментария.
    :return: JSON-ответ с именем текущего пользователя.
    """
    #TODO удалить коммент из БД
    doctorName = "Dr. Smith"
    return jsonify(doctorName)


@app.route('/edit_comment/<int:comment_id>', methods=['POST'])
def edit_comment(comment_id):
    """
    Изменяет комментарий по его id.
    :param int comment_id: ID комментария.
    :param str comment: Текст комментария.
    :return: JSON-ответ с информацией о комментарии, включая id комментария, имя доктора, время, текст комментария, является ли текущий пользователь автором.
    """
    updated_comment = request.form.get('comment')

    #TODO изменить коммента в БД и после вернуть его
    return jsonify({"id": 1, "doctor": "Dr. Smith", "time": "10:30", "comment": updated_comment, "editable": True})


@app.route('/create_patient', methods=['POST'])
def create_patient():
    """
    Создает нового пациента.
    :param str fullname: Имя пациента.
    :param str birthdate: Дата рождения.
    :param str snils: СНИЛС пациента.
    :param image image: Изображение пациента.
    :return: JSON-ответ с информацией о пациенте, включая id пациента, имя пациента, СНИЛС.
    """
    fullname = request.form['fullname']
    birthdate = request.form['birthdate']
    snils = request.form['snils']
    image = request.files.get('image') #может быть null

    if image:
        image.save('./static/patient_images/imagename.jpg')

    #TODO сохраняем в бд, возвращаем id из базы и полное имя со СНИЛСом
    return jsonify({'id': 100, 'name': fullname, 'snils': snils})


@app.route('/load_patients', methods=['GET'])
def load_patients():
    """
    :param str search: Фильтр.
    :param str page: Номер страницы.
    :return: JSON-ответ со списком пациентов для указанной страницы, включая id пациента, имя, СНИЛС; также переменную more, указывающая о конце пагинации.
    """
    #TODO сейчас есть похожая функция для таблицы, но в этой появляется обязательная переменная more, в будущем планирую убрать старую функцию без more и переиспользовать эту
    term = request.args.get('search', '')
    page = int(request.args.get('page', 1))

    per_page = 2 #небольшое значение для визуализации загрузки
    count = Patient.count_all_search(term)[0][0]
    start = (page - 1) * per_page
    end = (start + per_page) if (start + per_page) < count else count

    time.sleep(1)
    
    patients = Patient.find_all_search_lazyload(term, start, end)
    patients = [{'id': patient[0], 'name': patient[1], 'snils':patient[2]} for patient in patients]
    return jsonify({'results': patients, 'pagination': {'more': end < count}}) #и при этом нужно как то понять, была ли это последняя страница


if __name__ == "__main__":
    app.run(debug=True)
