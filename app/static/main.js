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
        success: function(newContent) {
          $('#patientModal .modal-content').html(newContent);
          createLazyLoadTable('patient-history-table', '/load_patient_history', patientId);
          $('#patientModal').modal('show');
        },
        error: function(xhr, status, error) {
            console.error('Ошибка при получении HTML-кода модального окна: ' + error);
        }
    });
  });
});
