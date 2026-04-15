


function toggleProfessores() {
    document.getElementById('professoresLista').classList.toggle('hidden');
}

function atualizarProfessores() {
    const checks = document.querySelectorAll('input[name="professores"]:checked');
    const nomes = [...checks].map(item =>
        item.closest('label').querySelector('span').innerText
    );

    document.getElementById('professoresDisplay').value =
        nomes.length ? nomes.join(', ') : '';
}

// fecha clicando fora
document.addEventListener('click', function(e) {
    const box = document.querySelector('.input-group');
    const lista = document.getElementById('professoresLista');

    if (!box.contains(e.target)) {
        lista.classList.add('hidden');
    }
});