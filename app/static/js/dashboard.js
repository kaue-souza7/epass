document.body.addEventListener("htmx:afterSwap", function(evt) {
    if (evt.detail.target.id === "container-registro") {
        evt.detail.target.style.display = "block";
    }
});

<<<<<<< Updated upstream


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

=======
const select = document.getElementById("registroSelect");
const cards = document.querySelectorAll(".registro-card");

select.addEventListener("change", function(){

    cards.forEach(card => {
        card.style.display = "none";
    });

    const selecionado = document.getElementById(this.value);

    if(selecionado){
        selecionado.style.display = "block";
    }

>>>>>>> Stashed changes
});