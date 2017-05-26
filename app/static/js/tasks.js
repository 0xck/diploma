'use strict';
// actions button and dropdown actions
// on hold
$(document).ready(function() {
    $('.hold[id]').bind('click', function( event ) {
        event.preventDefault();
        $.get('/task/' + this.id + '/hold', function (data) {
            $('#alert_place').html(data);
        });
        $(this).closest('tr').children('td.task_status').text('hold');
        $(this).closest('tr').removeClass();
        $(this).closest('tr').addClass('info');
    });
});
// to queue
$(document).ready(function() {
    $('.queue[id]').bind('click', function( event ) {
        event.preventDefault();
        $.get('/task/' + this.id + '/queue', function (data) {
            $('#alert_place').html(data);
        });
        $(this).closest('tr').children('td.task_status').text('pending');
        $(this).closest('tr').removeClass();
    });
});
// re add
$(document).ready(function() {
    $('.readd[id]').bind('click', function( event ) {
        event.preventDefault();
        $.get('/task/' + this.id + '/readd', function (data) {
            $('#alert_place').html(data);
        });
        $(this).closest('tr').children('td.task_status').text('pending');
        $(this).closest('tr').removeClass();
    });
});
// cancel
$(document).ready(function() {
    $('.cancel[id]').bind('click', function( event ) {
        event.preventDefault();
        $.get('/task/' + this.id + '/cancel', function (data) {
            $('#alert_place').html(data);
        });
        $(this).closest('tr').children('td.task_status').text('canceled');
        $(this).closest('tr').removeClass();
        $(this).closest('tr').addClass('active');
    });
});
// clone
$(document).ready(function() {
    $('.clone[id]').bind('click', function( event ) {
        event.preventDefault();
        $.get('/task/' + this.id + '/clone', function (data) {
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
// task filter
// all
$(document).ready(function() {
    $('#filter_all').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').show();
    });
});
// pending
$(document).ready(function() {
    $('#filter_pending').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').hide();
    $('tr.pending').show();
    });
});
// successful
$(document).ready(function() {
    $('#filter_successful').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').hide();
    $('tr.successful').show();
    });
});
// done
$(document).ready(function() {
    $('#filter_hold').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').hide();
    $('tr.hold').show();
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
// canceled
$(document).ready(function() {
    $('#filter_canceled').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').hide();
    $('tr.canceled').show();
    });
});
