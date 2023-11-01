import { openRequestInfoModal } from "./requestInfoModal.js";
import "./select2adapters.js";

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
        placeholderForSearch: 'Поиск...',
        dropdownAdapter: $.fn.select2.amd.require("PatientsDropdownAdapter"),
        closeOnSelect: true,
        ajax: {
            url: '/load_patients',
            dataType: 'json',
            delay: 250,
            data: function(params) {
                return {
                    search: params.term,
                    page: params.page || 1
                };
            },
            processResults: function(data, params) {
                params.page = params.page || 1;

                return {
                    results: data.results,
                    pagination: {
                        more: data.pagination.more
                    }
                };
            },
            cache: true
        },
        language: {
            errorLoading: () => 'Невозможно загрузить результаты',
            inputTooLong: () => 'Слишком много символов',
            inputTooShort: () => 'Слишком мало символов',
            maximumSelected: () => 'Выбрано максимальное количество элементов',
            noResults: () => $('<div>', { class: 'text-center' }).text('Нет результатов'),
            removeAllItems: () => 'Удалить все элементы',
            removeItem: () => 'Удалить элемент',
            search: () => 'Поиск',
            searching: () => $('<div>', { class: 'text-center' }).append($('<div>', { class: 'spinner-border spinner-border-sm', role: 'status' })
                    .append($('<span>', { class: 'visually-hidden' }).text('Загрузка...'))),
            loadingMore: () => $('<div>', { class: 'text-center' }).append($('<div>', { class: 'spinner-border spinner-border-sm', role: 'status' })
                    .append($('<span>', { class: 'visually-hidden' }).text('Загрузка...')))
        },   
        templateResult: function(option) {
            if (!option.id) { return option.text; }
            
            var $row = $('<div>', { class: 'row' });
            var $nameCol = $('<div>', { class: 'col', text: option.name });
            var $snilsCol = $('<div>', { class: 'col-3', text: option.snils });

            $row.append($nameCol, $snilsCol);
            return $row;
        },
        templateSelection: function(option) {
            if (!option.id) { return option.text; }

            const container = $('<div>').css('display', 'flex').css('justify-content', 'space-between');
            container.attr('title', `Имя: ${option.name}, СНИЛС: ${option.snils}`);
        
            const nameWrapper = $('<div>');
            nameWrapper.append($('<span>').text('Имя: ').css('color', '#888'));
            nameWrapper.append($('<span>').text(option.name));
        
            const snilsWrapper = $('<div>');
            snilsWrapper.append($('<span>').text('СНИЛС: ').css('color', '#888'));
            snilsWrapper.append($('<span>').text(option.snils));
            nameWrapper.css('margin-right', '15px');
            
            return container.append(nameWrapper, snilsWrapper);
        }
    })

    $('#requestForm').submit(function(e) {
        e.preventDefault();
        var selectedData = $('#patientname').select2('data');
        var selectedOption = selectedData[0];
        var symptoms = $('#symptoms').val();
        openRequestInfoModal('new', { id: selectedOption.id, name: selectedOption.name, snils: selectedOption.snils, symptoms: symptoms });
    });
})