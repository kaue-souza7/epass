const select = document.getElementById("themeSelect");
const selected = select.querySelector(".selected");
const options = select.querySelector(".options");
const hidden = document.getElementById("theme");

selected.onclick = () => {
    options.style.display =
        options.style.display === "block" ? "none" : "block";
};

options.querySelectorAll("div").forEach(item => {
    item.onclick = () => {
        selected.textContent = item.textContent;
        hidden.value = item.dataset.value;
        options.style.display = "none";

        changeTheme(); // sua função
    };
});

document.addEventListener("click", e => {
    if (!select.contains(e.target)) {
        options.style.display = "none";
    }
});

function signOut() {
    alert("Você saiu da conta.");
    setTimeout(() => {
        window.top.location.href = "../index.html";
    }, 1000);
}

setTimeout(() => {
    document.querySelectorAll('.alert').forEach(el => {
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 300);
    });
}, 3000);


document.body.addEventListener("htmx:load", function () {

    const cepInput = document.getElementById("cep");

    if (!cepInput) return;

    cepInput.addEventListener("blur", function () {
        let cep = cepInput.value.replace(/\D/g, '');

        if (cep.length !== 8) return;

        fetch(`https://viacep.com.br/ws/${cep}/json/`)
            .then(res => res.json())
            .then(data => {

                if (data.erro) {
                    alert("CEP não encontrado");
                    return;
                }

                document.getElementById("rua").value = data.logradouro || '';
                document.getElementById("bairro").value = data.bairro || '';
                document.getElementById("cidade").value = data.localidade || '';
                document.getElementById("estado").value = data.uf || '';

            });
    });

});
