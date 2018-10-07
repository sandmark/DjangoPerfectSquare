$(document).ready(function() {
    $(".dropdown-trigger[data-target='user-dropdown-navbar']").dropdown({
        hover: true,
        constrainWidth: false,
    });

    $(".dropdown-trigger[data-target='tags-dropdown-navbar']").dropdown({
        hover: false,
        constrainWidth: true,
    });
});
