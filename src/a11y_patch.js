(function() {
  console.log('A11y Patch: Initializing...');
  
  function patch() {
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(el => {
      if (el.getAttribute('aria-label')) return;
      
      let text = '';
      // 1. Try immediate predecessor
      const prev = el.previousElementSibling;
      if (prev && prev.textContent.trim()) {
        text = prev.textContent.trim();
      }
      
      // 2. Try parent's first child (common in hostile tables/rows)
      if (!text || text.length < 2) {
        const parent = el.parentElement;
        if (parent && parent.firstElementChild && parent.firstElementChild !== el) {
          text = parent.firstElementChild.textContent.trim();
        }
      }
      
      if (text && text.length > 1 && text.length < 100) {
        const cleanText = text.replace(/:$/, '').trim();
        el.setAttribute('aria-label', cleanText);
        el.setAttribute('data-patched', 'true');
      }
    });
  }

  // Set up observer for dynamic Angular content
  const observer = new MutationObserver(patch);
  
  function start() {
    if (document.body) {
      observer.observe(document.body, { childList: true, subtree: true });
      patch();
      console.log('A11y Patch: Observer active on document.body');
    } else {
      setTimeout(start, 50);
    }
  }
  
  start();
})();
