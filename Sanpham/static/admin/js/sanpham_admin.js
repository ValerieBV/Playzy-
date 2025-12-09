(function($) {
    'use strict';
    
    // Đảm bảo khung hiển thị ngay cả khi Select2 khởi tạo muộn
    function ensureBoxDisplay() {
        var $selection = $('.form-group.field-san_pham_lien_quan .select2-selection');
        var $container = $('.form-group.field-san_pham_lien_quan .select2-container');

        // Đảm bảo khung hiển thị ngay
        if ($selection.length) {
            $selection.css({
                'border': '1px solid #dee2e6',
                'border-radius': '4px',
                'padding': '6px 8px',
                'min-height': '38px',
                'background-color': '#fff',
                'box-shadow': '0 1px 2px rgba(0,0,0,0.05)'
            });
        }
        
        // Đảm bảo container có width đầy đủ
        if ($container.length) {
            $container.css('width', '100%');
        }
    }
    
    // Chạy ngay khi DOM sẵn sàng
    $(document).ready(function() {
        ensureBoxDisplay();
        
        // Chạy lại sau một chút để đảm bảo Select2 đã khởi tạo
        setTimeout(ensureBoxDisplay, 100);
        setTimeout(ensureBoxDisplay, 500);
    });
    
    // Chạy lại sau khi Select2 được khởi tạo
    $(document).on('select2:open select2:select select2:unselect', function() {
        setTimeout(ensureBoxDisplay, 50);
    });
    
    // Đảm bảo chạy với Django jQuery nếu có
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).ready(function() {
            ensureBoxDisplay();
            setTimeout(ensureBoxDisplay, 100);
            setTimeout(ensureBoxDisplay, 500);
        });
    }
    
})(django.jQuery || jQuery);

