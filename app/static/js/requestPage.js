import { openRequestInfoModal } from "./requestInfoModal.js";

$(document).ready(function() {
    $('#symptoms').select2({
        theme: 'bootstrap-5',
        closeOnSelect: false,
        tags: false,
        allowHtml: true,
	    allowClear: true
    });
    
    $('#patientname').select2({
        theme: 'bootstrap-5',
        closeOnSelect: true,
        templateResult: function(state) {
            if (state.id === "add") {
                return $(`<div class="add-patient-button" onClick="openCreatePatientModal()">\
                            ${state.text} <i class="zmdi zmdi-account-add"></i>\
                        </div>`);
            }
            return state.text;
        },
        escapeMarkup: function(m) { 
            return m;
        }
    });

    $('#requestForm').submit(function(e) {
        e.preventDefault();
        openRequestInfoModal('POST', $(this).serialize());
    });
})