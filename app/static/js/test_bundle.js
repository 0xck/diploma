'use strict';
// dynamic test list maker
$(document).ready(function() {
    // index for making new test form
    // in case test edit
    if ($('#bundle_length').length) {
        var indx = Number($('#bundle_length').text());
    // in case new test
    } else {
        var indx = 0;
    };
    // adding/deleting func
    // click on "add button" add field
    $(document).on('click', '.add_btn', function(event) {
        event.preventDefault();
        // increasing index; index rises all time in order to prevent situation when field with intermediate value was deleted
        indx++;
        // func for replacing index in form
        function replacer(str, test_str, offset, s) {
            return test_str + indx;
        };
        // choosing initial field and clones one
        var parent = $('.generator div:first'),
            curr_entr = $(this).parents('.entr:first'),
            new_entr = $(curr_entr.clone()).appendTo(parent);
        // changing index in new field
        new_entr.html(new_entr.html().replace(/(test-)(\d+)/g, replacer));
        // changing button from "add" to "del"
        parent.find('.entr:not(:last) .add_btn')
            .removeClass('add_btn').addClass('del_btn')
            .removeClass('btn-success').addClass('btn-danger')
            .html('Delete test');
    // click on "del button" delete field
    }).on('click', '.del_btn', function(event) {
        $(this).parents('.entr:first').remove();
        event.preventDefault();
        return false;
    });
});
