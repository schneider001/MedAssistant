import { escapeHtml, createElementFromHTML } from "./utils.js";

export function openRequestInfoModal(method, data) {
           
    const loadSection = document.getElementById('request-load-section');
    const dataSection = document.getElementById('request-data-section');

    loadSection.style.display = 'block';
    dataSection.style.display = 'none';

    $.ajax({
        url: method === 'GET' ? '/get_request_info_by_id' : '/get_request_info',
        method: method,
        data: data,
        success: function(response) {
            loadSection.style.display = 'none';
            dataSection.style.display = 'block';
            loadRequestInfoModal(response)
        },
        error: function(xhr, status, error) {
            console.error('Ошибка при получении информации о запросе: ' + error);
        }
    });

    $('#requestModal').modal('show');
}

function loadRequestInfoModal(response) {
    var requestInfoHtml = `<div class="container-fluid my-2 py-2">\
                            <div class="row d-flex justify-content-center">\
                              <div class="col-md-12 col-lg-10 col-xl-12">\
                                <div class="info-item">\
                                  <span class="info-label">Имя пациента:</span>\
                                  <span class="info-value" id="name">${escapeHtml(response.patient_name)}</span>\
                                </div>\
                                <div class="info-item">\
                                  <span class="info-label">Симптомы:</span>\
                                  <span class="info-value" id="name">${escapeHtml(response.symptoms.join(', '))}</span>\
                                </div>\
                                <div class="info-item">\
                                  <span class="info-label">Предсказанный диагноз:</span>\
                                  <span class="info-value" id="name">${escapeHtml(response.diagnosis)}</span>\
                                </div>\
                              </div>\
                            </div>\
                          </div>`;
    $('#request-data-section').html(requestInfoHtml);

    var commentsHtml = '<div class="container-fluid my-2 py-2">\
                          <div class="row d-flex justify-content-center">\
                            <div class="col-md-12 col-lg-10 col-xl-12">\
                              <div class="card">\
                                <div class="card-body p-4" style="color #bbb; background-color: #f7f6f6; overflow-y: auto; height: 35vh">\
                                  <h5 class="text-center mb-4 pb-2">Комментарии врачей</h4>\
                                  <div class="row">\
                                    <div class="col" id="comments-container">';
    response.doctor_comments.forEach(function(comment) {
        commentsHtml += generateCommentHtml(comment);
    });
    commentsHtml += '</div></div></div></div></div></div></div>';
    $('#request-data-section').append(commentsHtml);

    const hasEditableComment = response.doctor_comments.some(comment => comment.editable === true);
    if (!hasEditableComment) {
        createCommentInputBlock(response.doctor);
    }
}

function generateCommentHtml(comment) {
    return `<div class="card mb-3" ${escapeHtml(comment.editable) ? 'id="editable-comment"' : ''}>\
              <div class="card-body">\
                <div class="d-flex flex-start">\
                  <img class="rounded-circle shadow-1-strong me-3"\
                    src="/static/testPatientCardPhoto.jpg" alt="avatar" width="65"\
                    height="64" />\
                  <div class="flex-grow-1 flex-shrink-1">\
                    <div ${escapeHtml(comment.editable) ? 'id="editable-comment-content"' : ''}>\
                      <div class="d-flex justify-content-between align-items-center mb-3">\
                        <h6 class="text-primary fw-bold mb-0">${escapeHtml(comment.doctor)}\
                          <span class="text-dark ms-2">${escapeHtml(comment.comment)}</span>\
                        </h6>\
                        <p class="mb-0">${escapeHtml(comment.time)}</p>\
                      </div>\
                      ${escapeHtml(comment.editable) ? `\
                      <div class="d-flex justify-content-between align-items-center">\
                        <p class="small mb-0" style="color: #aaa;">\
                        <a href="#!" class="link-grey" onclick="deleteComment(${escapeHtml(comment.id)})">Удалить</a> •\
                        <a href="#!" class="link-grey" onclick="editComment(${escapeHtml(comment.id)}, \'${escapeHtml(comment.doctor)}\', \'${escapeHtml(comment.comment)}\', \'${escapeHtml(comment.time)}\')">Изменить</a>\
                      </div>` : ''}\
                    </div>\
                  </div>\
                </div>\
              </div>\
            </div>`;
}

function editComment(id, doctor, comment, time) {
    const commentSection = document.getElementById('editable-comment-content');
    commentSection.innerHTML = `<div class="d-flex justify-content-between align-items-center mb-3">\
                                  <h6 class="text-primary fw-bold mb-0">${doctor}</h6>\
                                  <p class="mb-0">${time}</p>\
                                </div>\
                                <div class="mb-4 position-relative">\
                                  <textarea placeholder="Введите ваш комментарий здесь" rows="4" class="form-control" id="comment-textarea">${comment}</textarea>\
                                  <div class="invalid-tooltip">\
                                    Комментарий не должен быть пустым\
                                  </div>\
                                </div>\
                                <div class="d-flex justify-content-between align-items-center mt-3">\
                                  <p class="small" style="color: #aaa;">\
                                  <button href="#!" class="btn btn-theme text-end mx-1" onclick="saveComment(${id})">Сохранить</button>\
                                  <button href="#!" class="btn text-end mx-1" onclick="cancelEditComment(${id}, \'${doctor}\', \'${comment}\', \'${time}\')">Отменить</button>\
                                </div>`;
}
  
function createCommentInputBlock(doctor) {
    const commentsContent = document.getElementById('comments-container');
    const commentInputBlockHtml = `<div class="card mb-3" id="add-comment">\
                                    <div class="card-body">\
                                      <div class="d-flex flex-start">\
                                        <img class="rounded-circle shadow-1-strong me-3"\
                                          src="/static/testPatientCardPhoto.jpg" alt="avatar" width="65"\
                                          height="64" />\
                                        <div class="flex-grow-1 flex-shrink-1">\
                                          <div class="d-flex justify-content-between align-items-center mb-3">\
                                            <h6 class="text-primary fw-bold mb-0">${doctor}</h6>\
                                          </div>\
                                          <div class="mb-4 position-relative">\
                                            <textarea placeholder="Введите ваш комментарий здесь" rows="4" class="form-control" id="comment-textarea"></textarea>\
                                            <div class="invalid-tooltip">\
                                              Комментарий не должен быть пустым\
                                            </div>\
                                          </div>\
                                          <div class="d-flex justify-content-between align-items-center mt-3">\
                                            <p class="small" style="color: #aaa;">\
                                            <button href="#!" class="btn btn-theme text-end mx-1" onclick="addComment()">Сохранить</button>\
                                          </div>\
                                        </div>\
                                      </div>\
                                    </div>\
                                  </div>`;
    const commentInputBlock = createElementFromHTML(commentInputBlockHtml);
    commentsContent.insertAdjacentElement('afterbegin', commentInputBlock);
}
  
function addComment() {
    const commentInput = document.getElementById('comment-textarea');
    const addedComment = commentInput.value;
    
    if (addedComment.trim() === '') {
        commentInput.classList.add('is-invalid');
        return;
    } else {
        commentInput.classList.remove('is-invalid');
    }
  
    $.ajax({
        url: `/add_comment`,
        method: 'GET',
        data: { comment: addedComment },
        success: function(comment) {
            const commentsContent = document.getElementById('comments-container');
            const addCommentBlock = document.getElementById('add-comment');
            addCommentBlock.remove();
            const commentBlock = createElementFromHTML(generateCommentHtml(comment));
            commentsContent.insertAdjacentElement('afterbegin', commentBlock);
        },
        error: function(xhr, status, error) {
            console.error('Ошибка при добавлении комментария:', error);
        }
    });
}
  
function saveComment(id) {
    const commentInput = document.getElementById('comment-textarea');
    const updatedComment = commentInput.value;
  
    if (updatedComment.trim() === '') {
        commentInput.classList.add('is-invalid');
        return;
    } else {
        commentInput.classList.remove('is-invalid');
    }
  
    $.ajax({
        url: `/edit_comment/${id}`,
        method: 'POST',
        data: { comment: updatedComment },
        success: function(comment) {
            const commentSection = document.getElementById('editable-comment');
            const newComment = createElementFromHTML(generateCommentHtml(comment));
            commentSection.parentNode.replaceChild(newComment, commentSection);
        },
        error: function(xhr, status, error) {
            console.error('Ошибка при обновлении комментария:', error);
        }
    });
}
  
function deleteComment(id) {
    $.ajax({
        url: `/delete_comment/${id}`,
        method: 'POST',
        success: function(doctor) {
            const elementToRemove = document.getElementById('editable-comment');
            if (elementToRemove) {
              elementToRemove.remove();
            }
            createCommentInputBlock(doctor);
        },
        error: function(xhr, status, error) {
            console.error('Ошибка при удалении комментария:', error);
        }
    });
}
  
function cancelEditComment(id, doctor, comment, time) {
    const commentSection = document.getElementById('editable-comment-content');
    commentSection.innerHTML = `<div class="d-flex justify-content-between align-items-center mb-3">\
                                  <h6 class="text-primary fw-bold mb-0">${doctor}\
                                    <span class="text-dark ms-2">${comment}</span>\
                                  </h6>\
                                  <p class="mb-0">${time}</p>\
                                </div>\
                                <div class="d-flex justify-content-between align-items-center">\
                                  <p class="small mb-0" style="color: #aaa;">\
                                  <a href="#!" class="link-grey" onclick="deleteComment(${id})">Удалить</a> •\
                                  <a href="#!" class="link-grey" onclick="editComment(${id}, \'${doctor}\', \'${comment}\', \'${time}\')">Изменить</a>\
                                </div>`;
}

window.addComment = addComment;
window.editComment = editComment;
window.saveComment = saveComment;
window.deleteComment = deleteComment;
window.cancelEditComment = cancelEditComment;
