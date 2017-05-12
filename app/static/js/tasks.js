'use strict';
// on hold
$(document).ready(function() {
    $('.hold[id]').bind('click', function( event ) {
        event.preventDefault();
        $.get('/task/' + this.id + '/hold', function (data) {
            $('#alert_place').html(data);
        });
        $(this).closest('tr').children('td.task_status').text('hold');
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
    });
});
