$(document).ready(function() {
    $('#loginForm').submit(function(e) {
        e.preventDefault();

        var formData = $('#loginForm').serialize();
        $.ajax({
            url: '/login',
            method: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    window.location.href = '/main';
                } else {
                    $('#errorMessagePlaceholder').hide();
                    $('#errorMessage').text('Неправильный логин или пароль').show();
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
})