'use strict';
// to down
$(document).ready(function() {
    $('.down[id]').bind('click', function( event ) {
        event.preventDefault();
        $.get('/trex/' + this.id + '/down', function (data) {
            $('#alert_place').html(data);
        });
        $(this).closest('tr').children('td.trex_status').text('down');
        $(this).closest('tr').removeClass();
        $(this).closest('tr').addClass('active');
    });
});
// to idle
$(document).ready(function() {
    $('.idle[id]').bind('click', function( event ) {
        event.preventDefault();
        $.get('/trex/' + this.id + '/idle', function (data) {
            $('#alert_place').html(data);
        });
        $(this).closest('tr').children('td.trex_status').text('idle');
        $(this).closest('tr').removeClass();
    });
});
// trex filter
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
