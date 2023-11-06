let requestId;
let socket = io().connect(`http://'${document.domain}:${location.port}`);

socket.on('connect', function() {
    console.log('Подключено к серверу');
});

socket.on('joined_room', function(data) {
    console.log(data);
});

export function openRequestInfoModal(mode, data) {
           
    const loadSection = document.getElementById('request-load-section');
    const dataSection = document.getElementById('request-data-section');

    loadSection.style.display = 'block';
    dataSection.style.display = 'none';

    $.ajax({
        url: mode === 'by_id' ? '/get_request_info_by_id' : '/get_request_info',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            console.info(response.id);
            socket.emit('join_room', { room_id: response.id });
            loadSection.style.display = 'none';
            dataSection.style.display = 'block';
            loadRequestInfoModal(response)
        },
        error: function(xhr, status, error) {
            console.error('Ошибка при получении информации о запросе: ' + error);
        }
    });
    
    requestId = data.request_id;
    $('#requestModal').modal('show');
}

$('#requestModal').on('hidden.bs.modal', function() {
    socket.emit('leave_room', { room_id: requestId });
});

function loadRequestInfoModal(response) {
    const $infoContainer = $('<div>', { class: 'container-fluid my-2 py-2' });

    const $patientInfo = $('<div>', { class: 'info-item' });
    $patientInfo.append($('<span>', { class: 'info-label' }).text('Имя пациента: '));
    $patientInfo.append($('<span>', { class: 'info-value', id: 'name' }).text(response.patient_name));

    const $symptomsInfo = $('<div>', { class: 'info-item' });
    $symptomsInfo.append($('<span>', { class: 'info-label' }).text('Симптомы: '));
    $symptomsInfo.append($('<span>', { class: 'info-value', id: 'symptoms' }).text(response.symptoms.join(', ')));

    const $diagnosisInfo = $('<div>', { class: 'info-item' });
    $diagnosisInfo.append($('<span>', { class: 'info-label' }).text('Предсказанный диагноз: '));
    $diagnosisInfo.append($('<span>', { class: 'info-value', id: 'diagnosis' }).text(response.diagnosis));

    $infoContainer.append($patientInfo, $symptomsInfo, $diagnosisInfo);

    const $commentsContainer = $('<div>', { class: 'container-fluid my-2 py-2' });
    const $commentsCard = $('<div>', { class: 'card comments-block-card' });
    const $commentsCardBody = $('<div>', { class: 'card-body p-4' });

    const $commentsTitle = $('<h4>', { class: 'text-center mb-2 pb-2', style: 'font-weight: bold' }).text('Комментарии врачей');

    const $comments = $('<div>', { class: 'row', id: 'comments-container' });

    response.doctor_comments.forEach(function(comment) {
        $comments.append(generateCommentElement(comment));
    });

    $commentsCardBody.append($comments);
    $commentsCard.append($commentsCardBody);
    $commentsContainer.append($commentsTitle, $commentsCard);

    const requestDataSection = $('#request-data-section');
    requestDataSection.empty().append($infoContainer, $commentsContainer);

    const hasEditableComment = response.doctor_comments.some(comment => comment.editable === true);

    if (!hasEditableComment) {
        createCommentInputBlock(response.doctor);
    }
}

function createCommentBlock(id, doctor, comment, time, editable = false) {
    const $container1 = $('<div>', { class: 'd-flex justify-content-between align-items-center mb-3' });
    const $doctorName = $('<h6>', { class: 'text-primary fw-bold mb-0', text: doctor });
    const $commentText = $('<span>', { class: 'text-dark ms-2', text: comment });
    const $timeElement = $('<p>', { class: 'mb-0', text: time });
    
    $doctorName.append($commentText);
    $container1.append($doctorName, $timeElement);
    
    let $container2;
    if (editable) {
        $container2 = $('<div>', { class: 'd-flex justify-content-between align-items-center' });
        const $deleteLink = $('<a>', { class: 'link-grey', text: 'Удалить', role: 'button', click: function() { deleteComment(id); } });
        const $editLink = $('<a>', { class: 'link-grey', text: 'Изменить', role: 'button', click: function() { editComment(id, doctor, comment, time); } });
        $container2.append($('<p>', { class: 'small mb-0', style: 'color: #aaa;' }).append($deleteLink, ' • ', $editLink));
    }

    return { container1: $container1, container2: $container2 };
}

function generateCommentElement(comment) {
    const $div = $('<div>', { class: 'card mb-3 comment-card' });

    if (comment.editable) {
        $div.attr('id', 'editable-comment');
    }

    const $cardBody = $('<div>', { class: 'card-body' });
    const $dFlexStart = $('<div>', { class: 'd-flex flex-start' });
    const $avatar = $('<img>', {
        class: 'rounded-circle shadow-1-strong me-3',
        src: '/static/testPatientCardPhoto.jpg',
        alt: 'avatar',
        width: '64',
        height: '64'
    });
    const $flexContainer = $('<div>', { class: 'flex-grow-1 flex-shrink-1' });

    const $commentContent = $('<div>');

    if (comment.editable) {
        $commentContent.attr('id', 'editable-comment-content');
    }

    const $commentBlock = createCommentBlock(comment.id, comment.doctor, comment.comment, comment.time, comment.editable);
    $commentContent.append($commentBlock.container1);
    if ($commentBlock.container2) {
        $commentContent.append($commentBlock.container2);
    }

    $flexContainer.append($commentContent);
    $dFlexStart.append($avatar, $flexContainer);
    $cardBody.append($dFlexStart);
    $div.append($cardBody);

    return $div;
}

function editComment(id, doctor, comment, time) {
    const commentSection = $('#editable-comment-content');
    
    const $header = $('<div>').addClass('d-flex justify-content-between align-items-center mb-3');
    const $title = $('<h6>').addClass('text-primary fw-bold mb-0').text(doctor);
    const $time = $('<p>').addClass('mb-0').text(time);
    
    const $textareaWrapper = $('<div>').addClass('mb-4 position-relative');
    const $textarea = $('<textarea>').attr('placeholder', 'Введите ваш комментарий здесь').attr('rows', 4).addClass('form-control').attr('id', 'comment-textarea').text(comment);
    const $invalidTooltip = $('<div>').addClass('invalid-tooltip').text('Комментарий не должен быть пустым');
    
    const $buttonWrapper = $('<div>').addClass('d-flex justify-content-between align-items-center mt-3');
    const $smallText = $('<p>').addClass('small').css('color', '#aaa');
    const $saveButton = $('<button>').addClass('btn btn-theme text-end mx-1').text('Сохранить').on('click', function() {
        saveComment(id);
    });
    const $cancelButton = $('<button>').addClass('btn text-end mx-1').text('Отменить').on('click', function() {
        cancelEditComment(id, doctor, comment, time);
    });
    
    $header.append($title, $time);
    $textareaWrapper.append($textarea, $invalidTooltip);
    $buttonWrapper.append($smallText.append($saveButton, $cancelButton));
    
    commentSection.empty().append($header, $textareaWrapper, $buttonWrapper);
}
  
function createCommentInputBlock(doctor) {
    const commentsContent = $('#comments-container');
    
    const $commentInputBlock = $('<div>', { class: 'card mb-3 add-comment-card', id: 'add-comment' });
    const $cardBody = $('<div>', { class: 'card-body' });
    
    const $dFlex = $('<div>', { class: 'd-flex flex-start' });
    const $avatar = $('<img>', { 
        class: 'rounded-circle shadow-1-strong me-3', 
        src: '/static/testPatientCardPhoto.jpg', 
        alt: 'avatar', 
        width: 64, 
        height: 64 
    });
    const $flexGrow = $('<div>', { class: 'flex-grow-1 flex-shrink-1' });
    
    const $header = $('<div>', { class: 'd-flex justify-content-between align-items-center mb-3' });
    const $doctorName = $('<h6>', { class: 'text-primary fw-bold', text: doctor });
    
    const $commentTextareaContainer = $('<div>', { class: 'mb-3 position-relative' });
    const $commentTextarea = $('<textarea>', { placeholder: 'Введите ваш комментарий здесь', rows: 4, class: 'form-control', id: 'comment-textarea' });
    const $invalidTooltip = $('<div>', { class: 'invalid-tooltip', text: 'Комментарий не должен быть пустым' });
    
    const $buttonContainer = $('<div>', { class: 'mt-1 text-end' });
    const $saveButton = $('<button>', { class: 'btn btn-theme', text: 'Сохранить', click: addComment });
    
    $header.append($doctorName);
    $commentTextareaContainer.append($commentTextarea, $invalidTooltip);
    $buttonContainer.append($saveButton);
    
    $flexGrow.append($header, $commentTextareaContainer, $buttonContainer);
    $dFlex.append($avatar, $flexGrow);
    $cardBody.append($dFlex);
    $commentInputBlock.append($cardBody);
    
    commentsContent.prepend($commentInputBlock);
}
  
function addComment() {
    const commentInput = $('#comment-textarea');
    const addedComment = commentInput.val();
    
    if (addedComment.trim() === '') {
        commentInput.addClass('is-invalid');
        return;
    } else {
        commentInput.removeClass('is-invalid');
    }
    
    socket.emit('add_comment', { request_id: requestId, comment: addedComment, room_id: requestId });
}

function addCommentElement(comment) {
    const commentsContent = $('#comments-container');
    const addCommentBlock = $('#add-comment');
    addCommentBlock.remove();
    const $commentBlock = generateCommentElement(comment);
    
    const editableComment = $('#editable-comment');
    if (editableComment.length) {
        editableComment.replaceWith($commentBlock);
    } else {
        commentsContent.prepend($commentBlock);
    }
}

socket.on('added_comment', function(comment) {
    console.info('added_comment');
    addCommentElement(comment);
});

socket.on('self_added_comment', function(comment) {
    console.info('self_added_comment');
    comment.editable = true;
    addCommentElement(comment);
});

function saveComment(id) {
    const commentInput = $('#comment-textarea');
    const updatedComment = commentInput.val();
  
    if (updatedComment.trim() === '') {
        commentInput.addClass('is-invalid');
        return;
    } else {
        commentInput.removeClass('is-invalid');
    }

    socket.emit('edit_comment', { room_id: requestId, comment_id: id, comment: updatedComment });
}

function editCommentElement(comment) {
    const commentSection = $('#editable-comment');
    const $newComment = generateCommentElement(comment);
    commentSection.replaceWith($newComment);
}

socket.on('edited_comment', function(comment) {
    editCommentElement(comment);
});
  
socket.on('self_edited_comment', function(comment) {
    comment.editable = true;
    editCommentElement(comment);
});

function deleteComment(id) {
    socket.emit('delete_comment', { room_id: requestId, comment_id: id });
}

socket.on('deleted_comment', function(doctor) {
    const elementToRemove = $('#editable-comment');
    if (elementToRemove) {
      elementToRemove.remove();
    }
    createCommentInputBlock(doctor);
});
  
function cancelEditComment(id, doctor, comment, time) {
    const commentSection = $('#editable-comment-content');
    const $commentBlock = createCommentBlock(id, doctor, comment, time, true);
    commentSection.empty()
    commentSection.append($commentBlock.container1);
    if ($commentBlock.container2) {
        commentSection.append($commentBlock.container2);
    }
}
