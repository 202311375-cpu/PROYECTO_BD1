// Manejo de submenús desplegables permitiendo abrir varios a la vez
const menuButtons = document.querySelectorAll('.menu-btn');

menuButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const submenu = btn.nextElementSibling;
        // Alternar visibilidad del submenu actual
        if (submenu.style.display === 'flex') {
            submenu.style.display = 'none';
        } else {
            submenu.style.display = 'flex';
        }
    });
});

// Manejo de contenido al hacer click en submenús
const submenuButtons = document.querySelectorAll('.submenu-btn');
const content = document.getElementById('content');

submenuButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const opcion = btn.dataset.target;
        content.innerHTML = `<h1>${opcion.replace(/-/g, ' ').toUpperCase()}</h1>`;
    });
});