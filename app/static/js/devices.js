'use strict';
// to down
$(document).ready(function() {
    $('.down[id]').bind('click', function( event ) {
        event.preventDefault();
        $.get('/device/' + this.id + '/down', function (data) {
            $('#alert_place').html(data);
        });
        $(this).closest('tr').children('td.device_status').text('down');
        $(this).closest('tr').removeClass();
        $(this).closest('tr').addClass('active');
    });
});
// to idle
$(document).ready(function() {
    $('.idle[id]').bind('click', function( event ) {
        event.preventDefault();
        $.get('/device/' + this.id + '/idle', function (data) {
            $('#alert_place').html(data);
        });
        $(this).closest('tr').children('td.device_status').text('idle');
        $(this).closest('tr').removeClass();
    });
});
