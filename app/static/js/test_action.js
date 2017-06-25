'use strict';
// shows and hides fielsd in test forms (common, selection, etc)
$(document).ready(function() {
    document.getElementById('test_type').onchange=function () {
        var sel = $("#test_type").val();
        if (sel == 'selection') {
            $('#accuracy').prop('disabled', false);
            $('#rate_incr_step').prop('disabled', false);
            $('#max_succ_attempt').prop('disabled', false);
            $('#max_test_count').prop('disabled', false);
            $('#selection_test_type').prop('disabled', false);
        } else {
            $('#accuracy').prop('disabled', true);
            $('#rate_incr_step').prop('disabled', true);
            $('#max_succ_attempt').prop('disabled', true);
            $('#max_test_count').prop('disabled', true);
            $('#selection_test_type').prop('disabled', true);
        };
    };
});
