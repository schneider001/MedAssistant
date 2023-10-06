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
  function createLazyLoadTable(tableId, dataUrl) {
    let page = 1;
    const perPage = 10;
    let columns = [];
    let noMoreData = false;

    function loadMoreData() {
      if (noMoreData) {
        return;
      }
      
      $.ajax({
        url: `${dataUrl}?page=${page}&per_page=${perPage}`,
        method: 'GET',
        success: function(data) {
          if (data.length > 0) {
            if (columns.length === 0 && data[0]) {
              columns = Object.keys(data[0]);
            }

            data.forEach(row => {
              const $row = $('<tr>');
              columns.forEach(column => {
                $row.append(`<td>${row[column]}</td>`);
              });
              $(`#${tableId} tbody`).append($row);
            });
            page++;
          } else {
            noMoreData = true;
          }
        },
        error: function(xhr, status, error) {
          console.error(`Error fetching data: ${error}`);
        }
      });
    }

    loadMoreData();

    $(`#${tableId}`).scroll(function() {
      if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
        loadMoreData();
      }
    });
  }

  createLazyLoadTable('patients-table', '/load_data_patients');
  createLazyLoadTable('request-history-table', '/load_data_requests');
});