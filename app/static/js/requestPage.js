import { openRequestInfoModal } from "./requestInfoModal.js";

$(document).ready(function() {
    $('#symptoms').select2({
        theme: 'bootstrap-5',
        closeOnSelect: false,
        tags: false,
        allowHtml: true,
	    allowClear: true
    });

    $.fn.select2.amd.define("PatientsDropdownAdapter", [
        "select2/utils",
        "select2/dropdown",
        "select2/dropdown/attachBody",
        "select2/dropdown/attachContainer",
        "select2/dropdown/search"
    ], function(Utils, Dropdown, AttachBody, AttachContainer, Search) {
        let dropdownWithSearch = Utils.Decorate(Dropdown, Search);
        dropdownWithSearch.prototype.render = function() {
            var $rendered = Dropdown.prototype.render.call(this);
            let placeholder = this.options.get("placeholderForSearch") || "";
            let $search = $('<span>', {
                class: 'select2-search select2-search--dropdown',
            }).append(
                $('<input>', {
                    class: 'select2-search__field',
                    type: 'search',
                    tabindex: '-1',
                    placeholder: placeholder,
                    autocomplete: 'off',
                    autocorrect: 'off',
                    autocapitalize: 'off',
                    spellcheck: 'false',
                    role: 'textbox',
                })
            );

            var $button = $('<div>', {
                class: 'add-patient-button my-1',
                text: 'Добавить нового пациента',
                style: 'border-radius: 5px; cursor: pointer; margin-left: 11px; margin-right: 11px'
            }).append($('<i>', {
                class: 'zmdi zmdi-account-add ms-3'
            }));
          
            $button.click(function() {
                openCreatePatientModal();
            });

            var $resultsHeader = $('<div>', { class: 'row pt-3 pb-1 mx-0' });
            var $nameCol = $('<div>', { class: 'col', text: 'Имя' }).css('font-weight', 'bold');
            var $snilsCol = $('<div>', { class: 'col-3', text: 'СНИЛС' }).css('font-weight', 'bold');
            var $line = $('<hr>', { class: 'mt-2 mb-0' });

            $resultsHeader.append($nameCol, $snilsCol);
            $resultsHeader.append($line);

            this.$searchContainer = $search;
            this.$search = $search.find('input');
            
            this.$buttonContainer = $button;
            this.$resultsHeader = $resultsHeader;

            $rendered.prepend($resultsHeader);
            $rendered.prepend($button);
            $rendered.prepend($search);
            return $rendered;
        };
    
        let adapter = Utils.Decorate(dropdownWithSearch, AttachContainer);
        adapter = Utils.Decorate(adapter, AttachBody);
    
        return adapter;
    });

    $('#patientname').select2({
        theme: 'bootstrap-5',
        closeOnSelect: true,
        placeholderForSearch: 'Поиск...',
        dropdownAdapter: $.fn.select2.amd.require("PatientsDropdownAdapter"),
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
        templateResult: function(option) {
            console.info(option);
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
        openRequestInfoModal('POST', $(this).serialize());
    });
})