import LazyLoadTable from './LazyLoadTable.js';
import { openRequestInfoModal } from "./requestInfoModal.js";

$(document).ready(function() {
    const requestHistoryTable = new LazyLoadTable('request-history-table', '/load_data_requests');

    $('#request-history-table').on('click', 'tr', function() {
        var requestId = $(this).find('td:first').text();
    
        if (isNaN(requestId)) {
            return;
        }

        openRequestInfoModal('GET', { request_id: requestId });
    });
})