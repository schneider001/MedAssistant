class LazyLoadTable {
    constructor(tableId, dataUrl, searchData = '') {
        this.tableId = tableId;
        this.dataUrl = dataUrl;
        this.page = 1;
        this.perPage = 15;
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
          const $row = $('<tr>', { style: 'opacity: 0; pointer-events: none;', id: 'loading' });
          const $cell = $('<td>', { colspan: numColumns, style: 'text-align: center;' });
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

            $.ajax({
                url: `${this.dataUrl}?page=${this.page}&per_page=${this.perPage}&search=${this.searchData}`,
                method: 'GET',
                success: (data) => {
                    $loadingRow.remove();
                    
                    const $tbody = $(`#${this.tableId} tbody`);
                    if ($tbody.is(':empty') && data.length === 0) {
                        const $row = $('<tr>');
                        const $cell = $('<td>', { colspan: numColumns, style: 'text-align: center;' }).text('Ничего не найдено');
                        $row.append($cell);
                        $tbody.html($row);
                    }

                    if (data.length > 0) {
                        data.forEach(row => {
                            const $row = $('<tr>');
                            row.forEach(value => {
                                $row.append($('<td>').text(value));
                            });
                            $tbody.append($row);
                        });
                        this.page++;
                    } else {
                        this.noMoreData = true;
                    }
                  
                    this.isLoading = false;
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

export default LazyLoadTable;