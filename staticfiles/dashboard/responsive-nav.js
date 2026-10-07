(() => {
  const menus = [...document.querySelectorAll('.nav-toggle')].map(button => {
    const navigation = document.getElementById(button.getAttribute('aria-controls'));
    if (!navigation) return null;

    const close = () => {
      button.setAttribute('aria-expanded', 'false');
      button.setAttribute('aria-label', button.dataset.closedLabel);
      navigation.classList.remove('is-open');
    };

    button.dataset.closedLabel = button.getAttribute('aria-label');
    button.addEventListener('click', () => {
      const isOpen = button.getAttribute('aria-expanded') === 'true';
      button.setAttribute('aria-expanded', String(!isOpen));
      button.setAttribute('aria-label', isOpen ? button.dataset.closedLabel : 'Close navigation');
      navigation.classList.toggle('is-open', !isOpen);
    });
    navigation.addEventListener('click', event => {
      if (event.target instanceof Element && event.target.closest('a')) close();
    });

    const desktopQuery = matchMedia(button.closest('.site-header') ? '(min-width: 601px)' : '(min-width: 901px)');
    desktopQuery.addEventListener('change', event => {
      if (event.matches) close();
    });

    return { button, navigation, close };
  }).filter(Boolean);

  document.addEventListener('click', event => {
    for (const menu of menus) {
      if (!menu.button.contains(event.target) && !menu.navigation.contains(event.target)) menu.close();
    }
  });

  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    for (const menu of menus) {
      if (menu.button.getAttribute('aria-expanded') === 'true') {
        menu.close();
        menu.button.focus();
      }
    }
  });
})();