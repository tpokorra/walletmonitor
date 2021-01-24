/* https://github.com/nathancahill/skeleton-tabs */
(function() {
    function main() {
        var tabButtons = [].slice.call(document.querySelectorAll('ul.tab-nav li a.button'));

        tabButtons.map(function(button) {
            button.addEventListener('click', function() {
                active = document.querySelector('li a.active.button')
                if (active) active.classList.remove('active');
                button.classList.add('active');
                active = document.querySelector('.tab-pane.active')
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
