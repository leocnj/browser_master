(function() {
  console.log('🚀 Axe-Powered Smart Patcher: Initializing...');

  /**
   * Heuristic to find the most likely text label for an element.
   */
  function findDiscoveredLabel(el) {
    let text = '';
    
    // Strategy 1: Preceding sibling (e.g. <span>Label:</span> <input>)
    const prev = el.previousElementSibling;
    if (prev && prev.textContent.trim()) {
      text = prev.textContent.trim();
    }

    // Strategy 2: Parent's first child (e.g. <div> <span>Label:</span> <input> </div>)
    if (!text || text.length < 2) {
      const parent = el.parentElement;
      if (parent && parent.firstElementChild && parent.firstElementChild !== el) {
        text = parent.firstElementChild.textContent.trim();
      }
    }

    return text.replace(/:$/, '').trim();
  }

  /**
   * The core patching logic. Uses Axe-core for precision if available.
   */
  async function patch() {
    // If Axe-core is loaded, use it to find EXACTLY what is broken
    if (typeof axe !== 'undefined') {
      try {
        const results = await axe.run({
          runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa'] },
          rules: {
            'label': { enabled: true },
            'select-name': { enabled: true },
            'button-name': { enabled: true }
          }
        });

        results.violations.forEach(v => {
          v.nodes.forEach(node => {
            const el = document.querySelector(node.target[0]);
            if (el && !el.getAttribute('aria-label')) {
              const label = findDiscoveredLabel(el);
              if (label) {
                el.setAttribute('aria-label', label);
                el.setAttribute('data-patched', 'axe-smart');
              }
            }
          });
        });
      } catch (err) {
        console.error('Axe-smart patch failed:', err);
      }
    } else {
      // Fallback: Basic scan if Axe-core is missing
      const inputs = document.querySelectorAll('input, select, textarea');
      inputs.forEach(el => {
        if (!el.getAttribute('aria-label')) {
          const label = findDiscoveredLabel(el);
          if (label) {
            el.setAttribute('aria-label', label);
            el.setAttribute('data-patched', 'basic');
          }
        }
      });
    }
  }

  // Setup Observer for dynamic content (Angular/React/etc)
  const observer = new MutationObserver(() => {
    // Debounce a bit for performance
    if (window._patchTimeout) clearTimeout(window._patchTimeout);
    window._patchTimeout = setTimeout(patch, 100);
  });

  function start() {
    if (document.body) {
      observer.observe(document.body, { childList: true, subtree: true });
      patch();
    } else {
      setTimeout(start, 50);
    }
  }

  start();
})();
