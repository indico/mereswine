(function(global) {
    'use strict';

    function addAjaxDeleter(container, buttonSelector) {
        container.on('click', buttonSelector, function(e) {
            var $this = $(this),
                row = $this.closest('tr.server-row');
 
            e.preventDefault();
            if (!confirm('Do you really want to delete this instance?')) {
                return;
            }
 
            $.ajax({
                type: 'DELETE',
                url: $(this).data('url'),
                success: function() {
                    row.fadeOut(function() {
                        if (row.siblings('.server-row').length) {
                            row.next('.server-info-row').remove();
                            row.remove();
                            $('#show-enabled').trigger('change');
                        }
                        else {
                            location.reload();
                        }
                    });
                },
                error: function (xhr, textStatus, errorThrown) {
                    alert('AJAX request failed: ' + errorThrown);
                }
            });
        });
    }
    global.addAjaxDeleter = addAjaxDeleter;
})(this);
