function showLoading(form) {
    const button = document.getElementById("signup-btn");
    const text = document.getElementById("signup-text");
    const spinner = document.getElementById("signup-spinner");

    if (!button || !text || !spinner) {
        return true;
    }

    button.disabled = true;
    text.textContent = "Signing up...";
    spinner.classList.remove("hidden");

    return true;
}
