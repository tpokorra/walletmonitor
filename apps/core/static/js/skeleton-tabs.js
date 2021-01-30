/* https://github.com/nathancahill/skeleton-tabs */
(function() {
    function main() {
        var tabButtons = [].slice.call(document.querySelectorAll('ul.tab-nav li a.button'));

        tabButtons.map(function(button) {
            button.addEventListener('click', function() {

                // only get the active buttons from the current tabs control
                tabnav = button.closest('ul.tab-nav');
                active = document.querySelector('#' + tabnav.id + ' li a.active.button')
                if (active) active.classList.remove('active');
                button.classList.add('active');

                // only get the active panes from the current tabs control
                tabcontent = tabnav.nextSibling.nextSibling
                active = document.querySelector('#' + tabcontent.id + ' .tab-pane.active')
                if (active) active.classList.remove('active');
                document.querySelector(button.getAttribute('href')).classList.add('active');
            })
        })
    }

    if (document.readyState !== 'loading') {
        main();
    } else {
        document.addEventListener('DOMContentLoaded', main);
    }
})();
