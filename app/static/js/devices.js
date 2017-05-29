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
// autoset status
$(document).ready(function() {
    $('.check[id]').bind('click', function( event ) {
        event.preventDefault();
        var row = $(this)
        $('#alert_place').html('<div class="alert alert-warning" role="alert"><strong>Warning!</strong> Need to wait for autoset status complete. Please do not reload or close page until getting status change message.</div>');
        $.get('/device/' + this.id + '/autoset', function (data) {
            $('#alert_place').html(data['msg']);
            if (data['status'] == 'idle') {
                row.closest('tr').children('td.device_status').text('idle');
                row.closest('tr').removeClass();
            } else if (data['status'] == 'down') {
                row.closest('tr').children('td.device_status').text('down');
                row.closest('tr').removeClass();
                row.closest('tr').addClass('active');
            } else {};
        });
    });
});
// device filter
// all
$(document).ready(function() {
    $('#filter_all').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').show();
    });
});
// idle
$(document).ready(function() {
    $('#filter_idle').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').hide();
    $('tr.idle').show();
    });
});
// down
$(document).ready(function() {
    $('#filter_down').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').hide();
    $('tr.down').show();
    });
});
// testing
$(document).ready(function() {
    $('#filter_testing').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').hide();
    $('tr.testing').show();
    });
});
// error
$(document).ready(function() {
    $('#filter_error').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').hide();
    $('tr.error').show();
    });
});
