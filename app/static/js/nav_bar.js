'use strict';
// shows nav bar current link
$(document).ready(function() {
    if ($('h1').hasClass('tasks')) {
        $('li.tasks_menu').addClass('active');
    } else if ($('h1').hasClass('tests')) {
        $('li.tests_menu').addClass('active');
    } else if ($('h1').hasClass('trexes')) {
        $('li.trexes_menu').addClass('active');
    } else if ($('h1').hasClass('devices')) {
        $('li.devices_menu').addClass('active');
    };
});
