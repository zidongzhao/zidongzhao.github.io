document.addEventListener('DOMContentLoaded', function() {
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    const mobileNav = document.querySelector('.mobile-nav');
    const body = document.body;

    // Toggle mobile navigation
    mobileNavToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        mobileNav.classList.toggle('active');
        body.classList.toggle('nav-open');
    });

    // Close navigation when clicking on white space
    mobileNav.addEventListener('click', function(e) {
        if (e.target === this) {
            mobileNav.classList.remove('active');
            body.classList.remove('nav-open');
        }
    });

    // Prevent clicks inside the navigation from closing it
    mobileNav.querySelector('ul').addEventListener('click', function(e) {
        e.stopPropagation();
    });

    // Prevent clicks on social icons from closing the navigation
    const socialIcons = mobileNav.querySelector('.social-icons');
    if (socialIcons) {
        socialIcons.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
}); 