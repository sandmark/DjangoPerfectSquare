$(document).ready(function() {
    $(".dropdown-trigger[data-target='user-dropdown-sidenav']").dropdown({
        hover: false,
        constrainWidth: true,
        alignment: "right",
    });

    $(".dropdown-trigger[data-target='user-dropdown-navbar']").dropdown({
        hover: true,
        constrainWidth: false,
    });
});
