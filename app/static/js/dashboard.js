document.body.addEventListener("htmx:afterSwap", function(evt) {
    if (evt.detail.target.id === "container-registro") {
        evt.detail.target.style.display = "block";
    }
});



