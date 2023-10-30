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
            } else if (!state.disabled || state.id === "header") {
                try {
                    var text = state.text.replace(/'/g, '"');
                    const patientData = JSON.parse(text);
                    if (Object.keys(patientData).length === 2) {
                        const container = $('<div>').css('display', 'flex').css('justify-content', 'space-between');
                        const nameElement = $('<div>').text(patientData.name);
                        const snilsElement = $('<div>').text(patientData.snils);

                        nameElement.css('max-width', '75%').css('word-wrap', 'break-word').css('white-space', 'pre-wrap');

                        return container.append(nameElement, snilsElement);
                    } else {
                        return state.text;
                    }
                } catch {

                }
            }
            return state.text;
        },
        escapeMarkup: function(m) { 
            return m;
        },
        templateSelection: function(state) {
            try {
                var text = state.text.replace(/'/g, '"');
                const patientData = JSON.parse(text);
                if (Object.keys(patientData).length === 2) {
                    const container = $('<div>').css('display', 'flex').css('justify-content', 'space-between');
                    container.attr('title', `Имя: ${patientData.name}, СНИЛС: ${patientData.snils}`);
    
                    const nameWrapper = $('<div>');
                    nameWrapper.append($('<span>').text('Имя: ').css('color', '#888'));
                    nameWrapper.append($('<span>').text(patientData.name));
                
                    const snilsWrapper = $('<div>');
                    snilsWrapper.append($('<span>').text('СНИЛС: ').css('color', '#888'));
                    snilsWrapper.append($('<span>').text(patientData.snils));

                    nameWrapper.css('margin-right', '15px');
                    
                    return container.append(nameWrapper, snilsWrapper);
                }
            } catch {
            
            }
            return state.text;
        }
    });

    $('#requestForm').submit(function(e) {
        e.preventDefault();
        openRequestInfoModal('POST', $(this).serialize());
    });
})