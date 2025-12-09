// Đổi tên "Dashboard" thành "Trang chủ" trong toàn bộ trang admin
// Chỉ chạy một lần khi DOM đã load xong
(function() {
    'use strict';
    
    function replaceDashboardText() {
        // 1. Đổi trong sidebar
        const dashboardLinks = document.querySelectorAll('.nav-sidebar .nav-item > .nav-link[href="/admin/"], .nav-sidebar .nav-item > .nav-link[href="/admin"]');
        
        dashboardLinks.forEach(function(link) {
            const text = link.textContent.trim();
            const href = link.getAttribute('href');
            
            if ((text.includes('Dashboard') || href === '/admin/' || href === '/admin') && !text.includes('Trang chủ')) {
                const icon = link.querySelector('i');
                if (icon) {
                    const iconClone = icon.cloneNode(true);
                    link.innerHTML = '';
                    link.appendChild(iconClone);
                    link.appendChild(document.createTextNode(' Trang chủ'));
                } else {
                    link.textContent = 'Trang chủ';
                }
            }
        });
        
        // 2. Đổi trong title của trang (h1, h2, etc.)
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        headings.forEach(function(heading) {
            if (heading.textContent.includes('Dashboard') && !heading.textContent.includes('Trang chủ')) {
                heading.textContent = heading.textContent.replace(/Dashboard/gi, 'Trang chủ');
            }
        });
        
        // 3. Đổi trong breadcrumb
        const breadcrumbs = document.querySelectorAll('.breadcrumb, .breadcrumb-item, [class*="breadcrumb"]');
        breadcrumbs.forEach(function(breadcrumb) {
            if (breadcrumb.textContent.includes('Dashboard') && !breadcrumb.textContent.includes('Trang chủ')) {
                breadcrumb.textContent = breadcrumb.textContent.replace(/Dashboard/gi, 'Trang chủ');
            }
        });
        
        // 4. Đổi trong tất cả các phần tử có text "Dashboard"
        const allElements = document.querySelectorAll('*');
        allElements.forEach(function(element) {
            // Bỏ qua các phần tử đã được xử lý
            if (element.tagName === 'SCRIPT' || element.tagName === 'STYLE') return;
            
            // Chỉ xử lý các phần tử có text node con
            Array.from(element.childNodes).forEach(function(node) {
                if (node.nodeType === Node.TEXT_NODE && node.textContent.includes('Dashboard') && !node.textContent.includes('Trang chủ')) {
                    node.textContent = node.textContent.replace(/Dashboard/gi, 'Trang chủ');
                }
            });
        });
    }
    
    // Chạy khi DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', replaceDashboardText);
    } else {
        replaceDashboardText();
    }
    
    // Chạy lại sau một khoảng thời gian ngắn để đảm bảo
    setTimeout(replaceDashboardText, 500);
    setTimeout(replaceDashboardText, 1000);
})();

