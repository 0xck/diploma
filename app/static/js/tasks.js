'use strict';
// on hold
$(document).ready(function() {
    $('.hold[id]').bind('click', function( event ) {
        event.preventDefault();
        console.log($(this))
        $.get('/task/' + this.id + '/hold', function (data) {
            $('#alert_place').html(data);
        });
        $(this).closest('tr').children('td.task_status').text('hold');
        $(this).closest('tr').removeClass();
        $(this).closest('tr').addClass('info');
        //$(this).removeClass();
        //$(this).addClass('queue');
        //$(this).text('To queue');
        //$(this).prop("href", '/task/' + this.id + '/queue');
    });
});
// to queue
$(document).ready(function() {
    $('.queue[id]').bind('click', function( event ) {
        event.preventDefault();
        console.log($(this))
        $.get('/task/' + this.id + '/queue', function (data) {
            $('#alert_place').html(data);
        });
        $(this).closest('tr').children('td.task_status').text('pending');
        $(this).closest('tr').removeClass();
        //$(this).removeClass();
        //$(this).addClass('hold');
        //$(this).text('On hold');
        //$(this).prop("href", '/task/' + this.id + '/hold');
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
        //$(this).removeClass();
        //$(this).addClass('hold');
        //$(this).text('On hold');
        //$(this).prop("href", '/task/' + this.id + '/hold');
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
        //$(this).removeClass();
        //$(this).addClass('readd');
        //$(this).text('Re add');
        //$(this).prop("href", '/task/' + this.id + '/readd');
    });
});
