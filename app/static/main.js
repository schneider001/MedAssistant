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
  let page = 1;
  const perPage = 10;

  function loadMoreData() {
      $.ajax({
          url: `/load_data?page=${page}&per_page=${perPage}`,
          method: 'GET',
          success: function(data) {
            if (data.length > 0) {
              $('#patients-table tbody').append(data.map(row => `
                  <tr>
                      <td>${row.id}</td>
                      <td>${row.name}</td>
                  </tr>
              `).join(''));
              page++;
            }
          },
          error: function(xhr, status, error) {
            console.error(`Error fetching data: ${error}`);
          }
      });
  }

  loadMoreData();

  $('#patients-table').scroll(function() {
    if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
        loadMoreData();
    }
  });
});