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
// test filter
// all
$(document).ready(function() {
    $('#filter_all').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').show();
    });
});
// stateful
$(document).ready(function() {
    $('#filter_stateful').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').hide();
    $('tr.stateful').show();
    });
});
// stateless
$(document).ready(function() {
    $('#filter_stateless').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').hide();
    $('tr.stateless').show();
    });
});
// bundle
$(document).ready(function() {
    $('#filter_bundle').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').hide();
    $('tr.bundle').show();
    });
});
// common
$(document).ready(function() {
    $('#filter_common').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').hide();
    $('tr.common').show();
    });
});
// selection
$(document).ready(function() {
    $('#filter_selection').bind('click', function( event ) {
        event.preventDefault();
    $('li.active').removeClass();
    $(this).addClass('active');
    $('tr.condition').hide();
    $('tr.selection').show();
    });
});
