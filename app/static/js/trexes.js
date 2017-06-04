'use strict';
// actions button and dropdown actions
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
        $('div#' + this.id + '.btn-idle').addClass('hidden');
        $('div#' + this.id + '.btn-down').removeClass('hidden');
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
        $('div#' + this.id + '.btn-down').addClass('hidden');
        $('div#' + this.id + '.btn-idle').removeClass('hidden');
    });
});
// autoset status
$(document).ready(function() {
    $('.check[id]').bind('click', function( event ) {
        event.preventDefault();
        var row = $(this)
        var btn_id = this.id
        $('#alert_place').html('<div class="alert alert-warning" role="alert"><strong>Warning!</strong> Need to wait for autoset status complete. Please do not reload or close page until getting status change message.</div>');
        $.get('/trex/' + this.id + '/autoset', function (data) {
            $('#alert_place').html(data['msg']);
            if (data['status'] == 'idle') {
                row.closest('tr').children('td.trex_status').text('idle');
                row.closest('tr').removeClass();
                $('div#' + btn_id + '.btn-down').addClass('hidden');
                $('div#' + btn_id + '.btn-idle').removeClass('hidden');
            } else if (data['status'] == 'down') {
                row.closest('tr').children('td.trex_status').text('down');
                row.closest('tr').removeClass();
                row.closest('tr').addClass('active');
                $('div#' + btn_id + '.btn-idle').addClass('hidden');
                $('div#' + btn_id + '.btn-down').removeClass('hidden');
            } else if (data['status'] == 'testing') {
                row.closest('tr').children('td.trex_status').text('testing');
                row.closest('tr').removeClass();
                row.closest('tr').addClass('warning');
                $('div#' + btn_id + '.btn-idle').addClass('hidden');
                $('div#' + btn_id + '.btn-down').addClass('hidden');
                $('div#' + btn_id + '.btn-testing').removeClass('hidden');
            } else if (data['status'] == 'error_rpc') {
                row.closest('tr').children('td.trex_status').text('error_rpc');
                row.closest('tr').removeClass();
                row.closest('tr').addClass('danger');
                $('div#' + btn_id + '.btn-down').addClass('hidden');
                $('div#' + btn_id + '.btn-idle').removeClass('hidden');
            } else {};
        });
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
