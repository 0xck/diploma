'use strict';
// hide/show spoiled data
$(document).ready(function() {
    // hide all
    $('.spoiler').hide();
    // in case single test shows data
    if (!($('.not_single').length)) {
        $('.spoiler').toggle('fast');
    };
    // click on "expand all" shows data
    $('.expand_all').click(function(event) {
        event.preventDefault();
        $('.spoiler').toggle('fast');
    });
    // click on "hide all" hides data
    $('.hide_all').click(function(event) {
        event.preventDefault();
        $('.spoiler').hide();
    });
    // click on button near test header
    $('.spoiler_title').click(function() {
        $(this).parents('.container').find('.spoiler').toggle('fast');
    });
});
