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
      const $loadingRow = $(`<tr style="opacity: 0;"><td colspan="${numColumns}" style="text-align: center;"><div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Загрузка...</span></div></td></tr>`);

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
                  $row.append(`<td>${escapeHtml(value)}</td>`);
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
          $('#name').text(data.name);
          $('#birth-date').text(data.birthDate);
          $('#age').text(data.age);
          $('#snils').text(data.snils);
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

    const spinner = '<div class="spinner-container text-center"><div class="spinner-border spinner-border-lg" role="status"><span class="visually-hidden">Загрузка...</span></div></div>';
    $('#diagnosis-section').html(spinner);

    $.ajax({
      url: '/get_request_info',
      method: 'POST',
      data: $(this).serialize(),
      success: function(response) {
        $('#diagnosis-section').html('<h5 class="text-center">Диагноз</h5><p>' + escapeHtml(response.diagnosis) + '</p>');
        var commentsHtml = '<div class="container-fluid my-2 py-2">\
                              <div class="row d-flex justify-content-center">\
                                <div class="col-md-12 col-lg-10 col-xl-11">\
                                  <div class="card">\
                                    <div class="card-body p-4">\
                                      <h4 class="text-center mb-4 pb-2">Комментарии врачей</h4>\
                                      <div class="row">\
                                        <div class="col">';
        for (let i = 0; i < response.doctor_comments.length; i++) {
          const comment = response.doctor_comments[i];
          commentsHtml += `<div class="d-flex flex-start p-4">\
                              <img class="rounded-circle shadow-1-strong me-3"\
                                src="/static/testPatientCardPhoto.jpg" alt="avatar" width="65"\
                                height="65" />\
                              <div class="flex-grow-1 flex-shrink-1">\
                                <div>\
                                  <div class="d-flex justify-content-between align-items-center">\
                                    <p class="mb-1">\
                                    ${escapeHtml(comment.doctor)} <span class="small">- ${escapeHtml(comment.time)}</span>\
                                    </p>\
                                    <a href="#!"><i class="fas fa-edit fa-xs"></i><span class="small"> edit</span></a>\
                                  </div>\
                                  <p class="small mb-0">${escapeHtml(comment.comment)}</p>\
                                </div>\
                              </div>\
                            </div>`;
          if (i < response.doctor_comments.length - 1) {
            commentsHtml += '<hr class="my-0" />';
          }
        };
        commentsHtml += '</div></div></div></div></div></div></div>';
        $('#diagnosis-section').append(commentsHtml);
      },
      error: function(xhr, status, error) {
        console.error('Ошибка при отправке запроса: ' + error);
      }
    });

    $('#requestModal').modal('show');
  });

  function escapeHtml(unsafe)
  {
    if (typeof unsafe === 'string') {
      return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    } else {
      return unsafe;
    }
 }
});
