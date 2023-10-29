import LazyLoadTable from './LazyLoadTable.js';
import { openRequestInfoModal } from './requestInfoModal.js';

$(document).ready(function() {
    const patientsTable = new LazyLoadTable('patients-table', '/load_data_patients');
    let requestHistoryTable;

    $('#patients-table').on('click', 'tr', function() {
        var patientId = $(this).find('td:first').text();
    
        if (isNaN(patientId)) {
            return;
        }
    
        const loadSection = document.getElementById('patient-load-section');
        const dataSection = document.getElementById('patient-data-section');
    
        loadSection.style.display = 'block';
        dataSection.style.display = 'none';
    
        $.ajax({
            url: '/get_patient_info',
            method: 'GET',
            data: { patient_id: patientId },
            success: function(data) {
                loadSection.style.display = 'none';
                dataSection.style.display = 'block';
                $('#name').text(data.name);
                $('#birth-date').text(data.birthDate);
                $('#age').text(data.age);
                $('#snils').text(data.snils);
                if (requestHistoryTable) {
                    requestHistoryTable.removeEventListeners();
                    $('#request-history-table').off('click', 'tr');
                }
                requestHistoryTable = new LazyLoadTable('request-history-table', '/load_patient_history', patientId);

                $('#request-history-table').on('click', 'tr', function() {
                    var requestId = $(this).find('td:first').text();
                
                    if (isNaN(requestId)) {
                        return;
                    }
            
                    openRequestInfoModal('GET', { request_id: requestId });
                });
            },
            error: function(xhr, status, error) {
                console.error('Ошибка при получении информации о пациенте: ' + error);
            }
        });
    
        $('#patientModal').modal('show');
    });
})