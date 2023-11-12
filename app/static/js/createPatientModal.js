import "./select2adapters.js"

export function openCreatePatientModal() {
    $('#patientname').select2('close');
    $('#createPatientModal').modal('show');
  
    $('#birthdate').datepicker({
        format: "dd.mm.yyyy"
    });
  
    var omsInput = document.querySelector('.oms-input');
    var omsParts = document.querySelectorAll('.oms-part');
  
    var oms1 = document.getElementById('oms1');
    var oms2 = document.getElementById('oms2');
    var oms3 = document.getElementById('oms3');
    var oms4 = document.getElementById('oms4');
  
    omsInput.addEventListener('click', function(event) {
        if (event.target === omsInput) {   
            for (var i = omsParts.length - 1; i >= 0; i--) {
                if (omsParts[i].value.length > 0 || i === 0) {
                    if (omsParts[i].value.length < 3) {
                        omsParts[i].focus();
                    } else {
                        omsParts[i + 1].focus();
                    }
                    break;
                }
            }
        }
    });
  
    omsParts.forEach(function(input, index) {
        input.addEventListener('input', function() {
            var value = input.value;
        
            if (value.length === input.maxLength && index < omsParts.length - 1) {
                omsParts[index + 1].focus();
            }
        });
  
        input.addEventListener('keydown', function(event) {
            if (event.key === 'Backspace' && input.value.length === 0 && index > 0) {
                omsParts[index - 1].focus();
            } else if (event.key === 'ArrowRight' && input.selectionStart === input.value.length && index < omsParts.length - 1) {
                omsParts[index + 1].focus();
                setTimeout(function () {
                    omsParts[index + 1].setSelectionRange(1, 1);
                }, 0);
                event.preventDefault();
            } else if (event.key === 'ArrowLeft' && input.selectionStart <= 1 && index > 0) {
                omsParts[index - 1].focus();
                setTimeout(function () {
                    const newSelection = omsParts[index - 1].value.length;
                    omsParts[index - 1].setSelectionRange(newSelection, newSelection);
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
        
        var formData = new FormData();

        var selectedSex = $("#sex").select2('data')[0].id;
        
        formData.append("fullname", $("#fullname").val());
        formData.append("birthdate", $("#birthdate").val());
        formData.append("oms", `${oms1.value}-${oms2.value}-${oms3.value} ${oms4.value}`);
        formData.append("sex", selectedSex);
        
        var imageFile = $('#file-input')[0].files[0];
        if (imageFile) {
            formData.append("image", imageFile);
        }

        $.ajax({
            url: '/create_patient',
            method: 'POST',
            data: formData,
            contentType: false,
            processData: false,
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
  
    oms1.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');
    });
    
    oms2.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');
    });
    
    oms3.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');
    });
    
    oms4.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');
    });
}

$('#sex').select2({
    theme: 'bootstrap-5',
    dropdownAdapter: $.fn.select2.amd.require("SexDropdownAdapter"),
    closeOnSelect: true,
    language: {
        errorLoading: () => 'Невозможно загрузить пол'
    }
});

function handleDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'copy';
    document.getElementById('image-upload').classList.add('dragover');
}
window.handleDragOver = handleDragOver;

function handleDragLeave(event) {
    event.preventDefault();
    document.getElementById('image-upload').classList.remove('dragover');
}
window.handleDragLeave = handleDragLeave;

function handleFileDrop(event) {
    event.preventDefault();
    document.getElementById('image-upload').classList.remove('dragover');
    var file = event.dataTransfer.files[0];
    displayImage(file);
}
window.handleFileDrop = handleFileDrop;

function handleFileSelect(event) {
    var file = event.target.files[0];
    displayImage(file);
}
window.handleFileSelect = handleFileSelect;

function displayImage(file) {
    if (file && file.type.match('image.*')) {
        var reader = new FileReader();
        reader.onload = function(e) {
            var img = new Image();
            img.src = e.target.result;
            img.onload = function() {
                var canvas = document.createElement('canvas');
                var ctx = canvas.getContext('2d');
                canvas.width = 64;
                canvas.height = 64;
                ctx.drawImage(img, 0, 0, 256, 256);

                var thumbnail = document.getElementById('thumbnail');
                thumbnail.src = canvas.toDataURL('image/png');
                thumbnail.style.display = 'block';

                var uploadText = document.getElementById('image-upload');
                uploadText.style.display = 'none';

                var thumbnailContainer = document.getElementById('thumbnail-container');
                thumbnailContainer.style.display = 'block';
            };
        };
        reader.readAsDataURL(file);
    }
}
window.displayImage = displayImage;

window.openCreatePatientModal = openCreatePatientModal;
