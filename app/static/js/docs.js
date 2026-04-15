function toggleLista(id, botao){
    const box = document.getElementById(id);

    // se já tem conteúdo e está aberta -> fecha
    if(!box.classList.contains("hidden") && box.innerHTML.trim() !== ""){
        box.classList.add("hidden");
        botao.removeAttribute("hx-disable");
        event.preventDefault();
        return;
    }

    // vai abrir
    box.classList.remove("hidden");
}

document.body.addEventListener("htmx:afterSwap", function(evt){
    if(evt.detail.target.id === "lista-pendentes" ||
       evt.detail.target.id === "lista-entregues"){
        evt.detail.target.classList.remove("hidden");
    }
});