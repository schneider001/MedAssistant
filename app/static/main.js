$(document).ready(function() {
    $('#symptoms').select2({
      theme: 'bootstrap-5',
      closeOnSelect: false,
      tags: false,
      allowHtml: true,
			allowClear: true
    });
})

$(document).ready(function() {
  $('#patientname').select2({
    theme: 'bootstrap-5',
    closeOnSelect: false,
  });
})

$(document).ready(function() {
  let searchTimeout;
  let isLoading = false;

  const currentPage = window.location.pathname;
  
  function createLazyLoadTable(tableId, dataUrl, searchData = '') {
    let page = 1;
    const perPage = 15;
    let noMoreData = false;

    function loadMoreData() {
      if (noMoreData) {
        return;
      }

      const numColumns = $(`#${tableId} tbody tr:first td`).length;
      const $loadingRow = $('<tr style="opacity: 0;"><td colspan="' + numColumns + '" style="text-align: center;"><div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Загрузка...</span></div></td></tr>');

      if (!isLoading) {
          $loadingRow.animate({ opacity: 1 }, 1000);
          $(`#${tableId} tbody`).append($loadingRow);
        isLoading = true;

        $.ajax({
          url: `${dataUrl}?page=${page}&per_page=${perPage}&search=${searchData}`,
          method: 'GET',
          success: function(data) {
            $loadingRow.remove();

            if ($(`#${tableId} tbody`).is(':empty') && data.length === 0) {
              $(`#${tableId} tbody`).html('<tr><td style="text-align: center;">Ничего не найдено</td></tr>');
            }
            if (data.length > 0) {
              data.forEach(row => {
                const $row = $('<tr>');
                row.forEach(value => {
                  $row.append(`<td>${value}</td>`);
                });
                $(`#${tableId} tbody`).append($row);
              });
              page++;
            } else {
              noMoreData = true;
            }

            isLoading = false;
          },
          error: function(xhr, status, error) {
            console.error(`Error fetching data: ${error}`);
          }
        });
      }
    }

    function filterData(searchText) {
      $(`#${tableId} tbody`).empty();
      page = 1;
      noMoreData = false;
      searchData = searchText;
      loadMoreData();
    }

    loadMoreData();

    $(`#${tableId}`).scroll(function() {
      if (page != 1 && $(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
        loadMoreData();
      }
    });

    $('#search-input').on('input', function() {
      const searchText = $(this).val();
      clearTimeout(searchTimeout);

      searchTimeout = setTimeout(function() {
        filterData(searchText);
      }, 300);
    });

    document.getElementById('search-input').addEventListener('keydown', function(event) {
      if (event.keyCode === 13) {
        event.preventDefault();
      }
    });
  }

  if (currentPage === '/patients') {
    createLazyLoadTable('patients-table', '/load_data_patients');
  } else if (currentPage === '/history') {
    createLazyLoadTable('request-history-table', '/load_data_requests');
  }

  $('#patients-table').on('click', 'tr', function() {
    var patientId = $(this).find('td:first').text();

    $.ajax({
        url: '/get_patient_info',
        method: 'GET',
        data: { patient_id: patientId },
        success: function(data) {
          $('#name').html(data.name);
          $('#birth-date').html(data.birthDate);
          $('#age').html(data.age);
          $('#snils').html(data.snils);
          createLazyLoadTable('patient-history-table', '/load_patient_history', patientId);
          $('#patientModal').modal('show');
        },
        error: function(xhr, status, error) {
            console.error('Ошибка при получении HTML-кода модального окна: ' + error);
        }
    });
  });


  $('#requestForm').submit(function(e) {
    e.preventDefault();
    console.info("a");
    const spinner = '<div class="spinner-container text-center"><div class="spinner-border spinner-border-lg" role="status"><span class="visually-hidden">Загрузка...</span></div></div>';
    $('#diagnosis-section').html(spinner);

    $.ajax({
      url: '/process_request',
      method: 'POST',
      data: $(this).serialize(),
      success: function(response) {
        $('#diagnosis-section').html('<h5 class="text-center">Диагноз</h5><p>' + response.diagnosis + '</p>');
        var commentsHtml = '<h5 class="text-center mt-4">Комментарии врачей</h5><ul>';
        response.doctor_comments.forEach(function(comment) {
          commentsHtml += '<li>' + comment.doctor + ' (' + comment.time + '): ' + comment.comment + '</li>';
        });
        commentsHtml += '</ul>';
        $('#diagnosis-section').append(commentsHtml);
      },
      error: function(xhr, status, error) {
        console.error('Ошибка при отправке запроса: ' + error);
      }
    });

    $('#requestModal').modal('show');
  });

  function createCommentCard(username, avatar, upvotes, upvoted) {
    const commentCard = document.createElement('div');
    commentCard.classList.add('card', 'mb-4');
  
    commentCard.innerHTML = `
      <div class="card-body">
        <p>Type your note, and hit enter to add it</p>
  
        <div class="d-flex justify-content-between">
          <div class="d-flex flex-row align-items-center">
            <img src="${avatar}" alt="avatar" width="25" height="25" />
            <p class="small mb-0 ms-2">${username}</p>
          </div>
          <div class="d-flex flex-row align-items-center">
            <p class="small text-muted mb-0">Upvote?</p>
            <i class="far fa-thumbs-up mx-2 fa-xs text-black" style="margin-top: -0.16rem;"></i>
            <p class="small text-muted mb-0">${upvotes}</p>
          </div>
        </div>
      </div>
    `;

    return commentCard;
  }

  function addCommentToSection(username, comment, time) {
    const commentSection = document.getElementById('comment-section');
    const commentCard = createCommentCard(username, avatar, upvotes, upvoted);
    commentSection.appendChild(commentCard);
  }
});
