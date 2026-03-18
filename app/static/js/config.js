let themeSelector;

window.addEventListener('DOMContentLoaded', () => {
    themeSelector = document.getElementById("theme");
    updateBody(localStorage.getItem("theme"));
});

function changeTheme() {
    updateBody(themeSelector.value);
}

function updateBody(theme) {
    top.document.body.classList.remove('auto', 'dark', 'light');
    top.document.body.classList.add(`${theme}`);
    localStorage.setItem("theme", theme);
    themeSelector.value = theme;
}

function signOut() {
    alert("Você saiu da conta.");
    setTimeout(() => {
        window.top.location.href = "../index.html";
    }, 1000);
}

// Auto fechar alerta
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(el => {
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 300);
    });
}, 3000);