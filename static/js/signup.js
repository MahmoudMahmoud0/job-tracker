function showLoading(form) {
    const isLoginForm = form.querySelector("#login-btn") !== null;
    const button = document.getElementById(isLoginForm ? "login-btn" : "signup-btn");
    const text = document.getElementById(isLoginForm ? "login-text" : "signup-text");
    const spinner = document.getElementById(isLoginForm ? "login-spinner" : "signup-spinner");

    if (!button || !text || !spinner) {
        return true;
    }

    button.disabled = true;
    text.textContent = isLoginForm ? "Logging in..." : "Signing up...";
    spinner.classList.remove("hidden");

    return true;
}
