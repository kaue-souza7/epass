document.body.addEventListener("htmx:afterSwap", function(evt) {
    if (evt.detail.target.id === "container-registro") {
        evt.detail.target.style.display = "block";
    }
});

document.body.addEventListener("htmx:beforeRequest", function(evt){

    if(evt.detail.target.id === "lista-alunos"){
        document.getElementById("lista-box").classList.remove("hidden");
    }

});

document.body.addEventListener("htmx:afterSwap", function(evt){

    if(evt.detail.target.id === "lista-alunos"){
        document.getElementById("lista-box").classList.remove("hidden");
    }

});

