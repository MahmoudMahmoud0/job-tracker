const navOpenButton = document.getElementById("toggleOpen");
const navCloseButton = document.getElementById("toggleClose");
const navMenu = document.getElementById("collapseMenu");
const featuresToggleButton = document.getElementById("featuresToggle");
const featuresDropdownMenu = document.getElementById("featuresMenu");

let lastFocusedElement = null;

function openNavMenu() {
    if (!navMenu || !navOpenButton) return;

    lastFocusedElement = document.activeElement;
    navMenu.classList.remove("hidden");
    navOpenButton.setAttribute("aria-expanded", "true");
    navMenu.focus();
}

function closeNavMenu() {
    if (!navMenu || !navOpenButton) return;

    navMenu.classList.add("hidden");
    navOpenButton.setAttribute("aria-expanded", "false");
    lastFocusedElement?.focus();
}

function openFeaturesDropdown() {
    if (!featuresDropdownMenu || !featuresToggleButton) return;

    featuresDropdownMenu.classList.remove("hidden");
    featuresToggleButton.setAttribute("aria-expanded", "true");
}

function closeFeaturesDropdown() {
    if (!featuresDropdownMenu || !featuresToggleButton) return;

    featuresDropdownMenu.classList.add("hidden");
    featuresToggleButton.setAttribute("aria-expanded", "false");
}

if (navOpenButton && navCloseButton && navMenu) {
    navOpenButton.addEventListener("click", openNavMenu);
    navCloseButton.addEventListener("click", closeNavMenu);

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !navMenu.classList.contains("hidden")) {
            closeNavMenu();
        }
    });
}

if (featuresToggleButton && featuresDropdownMenu) {
    featuresToggleButton.addEventListener("click", (event) => {
        event.preventDefault();
        const isExpanded = featuresToggleButton.getAttribute("aria-expanded") === "true";

        if (isExpanded) {
            closeFeaturesDropdown();
        } else {
            openFeaturesDropdown();
        }
    });

    document.addEventListener("click", (event) => {
        if (
            !featuresToggleButton.contains(event.target) &&
            !featuresDropdownMenu.contains(event.target)
        ) {
            closeFeaturesDropdown();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeFeaturesDropdown();
            featuresToggleButton.focus();
        }
    });
}
