export function openCreatePatientModal() {
    $('#patientname').select2('close');
    $('#createPatientModal').modal('show');
  
    $('#birthdate').datepicker({
        format: "dd.mm.yyyy"
    });
  
    var snilsInput = document.querySelector('.snils-input');
    var snilsParts = document.querySelectorAll('.snils-part');
  
    var snils1 = document.getElementById('snils1');
    var snils2 = document.getElementById('snils2');
    var snils3 = document.getElementById('snils3');
    var snils4 = document.getElementById('snils4');
  
    snilsInput.addEventListener('click', function(event) {
        if (event.target === snilsInput) {   
            for (var i = snilsParts.length - 1; i >= 0; i--) {
                if (snilsParts[i].value.length > 0 || i === 0) {
                    if (snilsParts[i].value.length < 3) {
                        snilsParts[i].focus();
                    } else {
                        snilsParts[i + 1].focus();
                    }
                    break;
                }
            }
        }
    });
  
    snilsParts.forEach(function(input, index) {
        input.addEventListener('input', function() {
            var value = input.value;
        
            if (value.length === input.maxLength && index < snilsParts.length - 1) {
                snilsParts[index + 1].focus();
            }
        });
  
        input.addEventListener('keydown', function(event) {
            if (event.key === 'Backspace' && input.value.length === 0 && index > 0) {
                snilsParts[index - 1].focus();
            } else if (event.key === 'ArrowRight' && input.selectionStart === input.value.length && index < snilsParts.length - 1) {
                snilsParts[index + 1].focus();
                setTimeout(function () {
                    snilsParts[index + 1].setSelectionRange(1, 1);
                }, 0);
                event.preventDefault();
            } else if (event.key === 'ArrowLeft' && input.selectionStart <= 1 && index > 0) {
                snilsParts[index - 1].focus();
                setTimeout(function () {
                    const newSelection = snilsParts[index - 1].value.length;
                    snilsParts[index - 1].setSelectionRange(newSelection, newSelection);
                }, 0);
                event.preventDefault();
            }
        });
  
        input.addEventListener('paste', function (event) {
            event.preventDefault();
        });
    });
  
    function createPatientSubmitHandler (event) {
        event.preventDefault();
        
        var fullname = $("#fullname").val();
        var birthdate = $("#birthdate").val();
        
        var snils = `${snils1.value}-${snils2.value}-${snils3.value} ${snils4.value}`;
        
        $.ajax({
            url: '/create_patient',
            method: 'POST',
            data: { fullname: fullname, birthdate: birthdate, snils: snils },
            success: function(response) {
                var $select = $('#patientname');

                $select.select2('trigger', 'select', { data: response });
        
                $('#createPatientModal').modal('hide');
            },
            error: function(xhr, status, error) {
                console.error('Ошибка при создании нового пациента: ' + error);
            }
        });
    };

    $("#create-patient-form").on('submit', createPatientSubmitHandler);
  
    $('#createPatientModal').on('hidden.bs.modal', function() {
        var form = document.getElementById('create-patient-form');
        
        if (form) {
            form.reset();
        }

        $("#create-patient-form").off('submit', createPatientSubmitHandler);
    });
  
    snils1.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');
    });
    
    snils2.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');
    });
    
    snils3.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');
    });
    
    snils4.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');
    });
}

window.openCreatePatientModal = openCreatePatientModal;