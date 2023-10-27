
// make bootstap tooltips accessible 
// (tooltip to remain visible on hover and dismissable by pressing escape key)
document.addEventListener("DOMContentLoaded", function (event) {
    var tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        var tooltip = new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'manual',
            boundary: document.body,
            sanitize: false,
        });

        tooltipTriggerEl.addEventListener('mouseenter', function () {
            tooltip.show();
            document.querySelector('.tooltip').addEventListener('mouseleave', function () {
                tooltip.hide();
            });
            // hides tooltip when it was shown by mouseenter
            document.addEventListener('keydown', function (event) {
                if (event.key === 'Escape') {
                    tooltip.hide();
                }
            });
        });

        tooltipTriggerEl.addEventListener('focus', function () {
            tooltip.show();
        });

        tooltipTriggerEl.addEventListener('mouseout', function () {
            setTimeout(function () {
                if (!document.querySelector('.tooltip:hover')) {
                    tooltip.hide();
                }
            }, 100);
        });

        tooltipTriggerEl.addEventListener('blur', function () {
            tooltip.hide();
        });

        // works only when the tooltip was shown by focus
        tooltipTriggerEl.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                tooltip.hide();
            }
        });

        return tooltip;
    });
})


