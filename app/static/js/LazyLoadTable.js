class LazyLoadTable {
    constructor(tableId, dataUrl, searchData = '') {
        this.tableId = tableId;
        this.dataUrl = dataUrl;
        this.page = 1;
        this.searchData = searchData;
        this.noMoreData = false;
        this.isLoading = false;
        this.searchTimeout = null;
    
        this.init();
    }

    loadMoreData() {
        if (this.noMoreData) {
            return;
        }
  
        function createLoadingRow(numColumns) {
            const $row = $('<tr>', { style: 'opacity: 0; pointer-events: none;' });
            const $cell = $('<td>', { colspan: numColumns, style: 'text-align: center;', id: 'loading' });
            const $div = $('<div>', { class: 'spinner-border spinner-border-sm', role: 'status' }).append($('<span>', { class: 'visually-hidden' }).text('Загрузка...'));
            $cell.append($div);
            $row.append($cell);
            return $row;
        }

        const numColumns = $(`#${this.tableId} thead tr:first th`).length;
        const $loadingRow = createLoadingRow(numColumns);
  
        if (!this.isLoading) {
            $loadingRow.animate({ opacity: 1 }, 1000);
            $(`#${this.tableId} tbody`).append($loadingRow);
            this.isLoading = true;
            console.info($loadingRow);

            $.ajax({
                url: `${this.dataUrl}?page=${this.page}&search=${this.searchData}`,
                method: 'GET',
                success: (data) => {
                    $loadingRow.remove();
                    
                    const $tbody = $(`#${this.tableId} tbody`);
                    console.info(data);
                    if ($tbody.is(':empty') && data.results.length === 0) {
                        const $row = $('<tr>');
                        const $cell = $('<td>', { colspan: numColumns, style: 'text-align: center;', id: 'notfound' }).text('Ничего не найдено');
                        $row.append($cell);
                        $tbody.html($row);
                    }

                    if (data.results.length > 0) {
                        data.results.forEach(row => {
                            let $row;

                            switch (this.tableId) {
                              case "request-history-table":
                                $row = convertRequestsToTableRow(row);
                                break;
                              case "patients-table":
                                $row = convertPatientsToTableRow(row);
                                break;
                            }

                            $tbody.append($row);
                        });
                        this.page++;
                    }
                    
                    this.noMoreData = !data.pagination.more;
                    
                    this.isLoading = false;

                    const tableContainer = document.getElementById(this.tableId);
                    if (tableContainer.scrollHeight <= tableContainer.clientHeight) {
                        this.loadMoreData();
                    }
                },
                error: function(xhr, status, error) {
                    console.error(`Error fetching data: ${error}`);
                }
            });
        }
    }

    filterData(searchText) {
        $(`#${this.tableId} tbody`).empty();
        this.page = 1;
        this.noMoreData = false;
        this.searchData = searchText;
        this.loadMoreData();
    }

    init() {
        $(`#${this.tableId} tbody`).empty();
        this.loadMoreData();
        
        this.scrollHandler = () => {
            if (this.page != 1 && $(`#${this.tableId}`).scrollTop() + $(`#${this.tableId}`).innerHeight() >= $(`#${this.tableId}`)[0].scrollHeight * 0.9) {
                this.loadMoreData();
            }
        };
        $(`#${this.tableId}`).scroll(this.scrollHandler);
      
        this.searchHandler = () => {
            const searchText = $('#search-input').val();
            clearTimeout(this.searchTimeout);
            
            this.searchTimeout = setTimeout(() => {
                this.filterData(searchText);
            }, 300);
        };
        $('#search-input').on('input', this.searchHandler);
      
        document.getElementById('search-input').addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
            }
        });
    }

    removeEventListeners() {
        $(`#${this.tableId}`).off('scroll', this.scrollHandler);
        $('#search-input').off('input', this.searchHandler);
        document.getElementById('search-input').removeEventListener('keydown', this.keydownHandler);
    }
}

function convertPatientsToTableRow(patient) {
    const $row = $('<tr>');

    $row.append($('<td>').text(patient.id));
    $row.append($('<td>').text(patient.name));
    $row.append($('<td>').text(patient.oms));    

    return $row;
}

function convertRequestsToTableRow(request) {
    const $row = $('<tr>');

    $row.append($('<td>').text(request.id));
    $row.append($('<td>').text(request.name));
    $row.append($('<td>').text(request.date));    
    $row.append($('<td>').text(request.diagnosis));    
    $row.append($('<td>').text(request.is_commented ? "Прокомментирован" : "Без комментариев"));

    return $row;
}

export default LazyLoadTable;