$.fn.select2.amd.define("PatientsDropdownAdapter", [
    "select2/utils",
    "select2/dropdown",
    "select2/dropdown/attachBody",
    "select2/dropdown/attachContainer",
    "select2/dropdown/search",
    "select2/dropdown/closeOnSelect"
], function(Utils, Dropdown, AttachBody, AttachContainer, Search, closeOnSelect) {
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
    adapter = Utils.Decorate(adapter, closeOnSelect);

    return adapter;
});

