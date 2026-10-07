(() => {
  const loader = document.getElementById('page-loader');
  if (!loader) return;

  const storageKey = 'wmdms-navigation-transition';
  const isAuthenticated = document.body.dataset.authenticated === 'true';
  const currentLocation = `${window.location.pathname}${window.location.search}`;
  const showLoader = () => {
    if (document.readyState === 'complete') return;
    loader.hidden = false;
    document.body.setAttribute('aria-busy', 'true');
    const hideLoader = () => {
      loader.hidden = true;
      document.body.removeAttribute('aria-busy');
    };
    window.addEventListener('load', hideLoader, { once: true });
    window.setTimeout(hideLoader, 12000);
  };

  const saveTransition = (destination = null) => {
    sessionStorage.setItem(storageKey, JSON.stringify({
      from: currentLocation,
      destination,
      timestamp: Date.now(),
    }));
  };

  let pendingTransition = null;
  try {
    pendingTransition = JSON.parse(sessionStorage.getItem(storageKey) || 'null');
  } catch {
    sessionStorage.removeItem(storageKey);
  }

  if (pendingTransition) {
    sessionStorage.removeItem(storageKey);
    const isRecent = Date.now() - pendingTransition.timestamp < 15000;
    const isExpectedDestination = pendingTransition.destination
      ? pendingTransition.destination === currentLocation
      : pendingTransition.from !== currentLocation;
    if (isAuthenticated && isRecent && isExpectedDestination) {
      showLoader();
    }
  }

  document.addEventListener('click', event => {
    if (
      !isAuthenticated
      || event.defaultPrevented
      || event.button !== 0
      || event.metaKey
      || event.ctrlKey
      || event.shiftKey
      || event.altKey
    ) return;

    const link = event.target instanceof Element ? event.target.closest('a') : null;
    if (!link || link.hasAttribute('download') || link.dataset.noLoader === 'true') return;
    if (link.target && link.target.toLowerCase() !== '_self') return;

    const destination = new URL(link.href, window.location.href);
    if (destination.origin !== window.location.origin) return;
    const destinationLocation = `${destination.pathname}${destination.search}`;
    if (destinationLocation === currentLocation) return;
    if (destination.pathname === window.location.pathname && destination.search === window.location.search) return;

    saveTransition(destinationLocation);
  });

  document.addEventListener('submit', event => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    if (form.target && form.target.toLowerCase() !== '_self') return;
    if (!isAuthenticated && form.id !== 'login-form') return;
    saveTransition();
  });
})();