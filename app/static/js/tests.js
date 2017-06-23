'use strict';
// clone
$(document).ready(function() {
    $('.clone[id]').bind('click', function( event ) {
        event.preventDefault();
        $.get('/test/' + this.id + '/clone', function (data) {
            $('#alert_place').html(data);
            // reload page in 5 sec
            var timeout = 4;
            setInterval(function () {
                $('#timeout').html(timeout);
                if (timeout == 1) { 
                    location.reload(true);
                };
                timeout--;
        }, 1000);
        });
    });
});
