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

  const currentPage = window.location.pathname;
  
  function createLazyLoadTable(tableId, dataUrl) {
    let page = 1;
    const perPage = 15;
    let noMoreData = false;
    let searchData = '';

    function loadMoreData() {
      if (noMoreData) {
        return;
      }

      $.ajax({
        url: `${dataUrl}?page=${page}&per_page=${perPage}&search=${searchData}`,
        method: 'GET',
        success: function(data) {
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
        },
        error: function(xhr, status, error) {
          console.error(`Error fetching data: ${error}`);
        }
      });
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
  }

  if (currentPage === '/patients') {
    createLazyLoadTable('patients-table', '/load_data_patients');
  } else if (currentPage === '/history') {
    createLazyLoadTable('request-history-table', '/load_data_requests');
  }
});