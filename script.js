// ── Feature strip: clone track for seamless CSS marquee ──
(function () {
  function initStrip() {
    var track = document.getElementById('featTrack');
    if (!track) return;

    // Clone all cards and append — CSS animation goes from 0 to -50%
    var items = Array.from(track.children);
    items.forEach(function (item) {
      var clone = item.cloneNode(true);
      clone.setAttribute('aria-hidden', 'true');
      // Re-trigger videos inside clones
      var videos = clone.querySelectorAll('video');
      videos.forEach(function (v) { v.play().catch(function () { }); });
      track.appendChild(clone);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initStrip);
  } else {
    initStrip();
  }
})();

// ── Sticky Cards Scroll Effect ──
(function() {
  function initCards() {
    const cards = document.querySelectorAll('.step-card');
    if (!cards.length) return;

    window.addEventListener('scroll', () => {
      cards.forEach((card, index) => {
        const nextCard = cards[index + 1];
        if (nextCard) {
          const rect = card.getBoundingClientRect();
          const nextRect = nextCard.getBoundingClientRect();
          
          const minDistance = 24; 
          const maxDistance = card.offsetHeight; 
          
          let dist = nextRect.top - rect.top;
          let progress = 1 - ((dist - minDistance) / (maxDistance - minDistance));
          progress = Math.max(0, Math.min(1, progress));
          
          card.style.setProperty('--progress', progress);
        } else {
          card.style.setProperty('--progress', 0);
        }
      });
    }, {passive: true});
    
    // Trigger once on load
    window.dispatchEvent(new Event('scroll'));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCards);
  } else {
    initCards();
  }
})();

// ── Mobile Menu Toggle ──
(function() {
  function initMenu() {
    const hamburgers = document.querySelectorAll('.nav__hamburger, .nav__burger, #hamburger');
    const mobileNavs = document.querySelectorAll('.nav__mobile, #nav-mobile, #mobileNav');
    
    hamburgers.forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        mobileNavs.forEach(nav => {
          nav.classList.toggle('open');
          
          if (nav.classList.contains('open')) {
            nav.style.display = 'flex';
          } else {
            nav.style.display = 'none';
          }
        });
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMenu);
  } else {
    initMenu();
  }
})();
