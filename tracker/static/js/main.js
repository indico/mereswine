(function(global) {
    'use strict';

    function addAjaxDeleter(container, buttonSelector) {
        container.on('click', buttonSelector, function(e) {
            var $this = $(this),
                row = $this.closest('tr');
 
            e.preventDefault();
            if (!confirm('Do you really want to delete this item?')) {
                return;
            }
 
            $.ajax({
                type: 'DELETE',
                url: $(this).data('url'),
                success: function() {
                    row.fadeOut(function() {
                        if (row.siblings().length) {
                            row.remove();
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
