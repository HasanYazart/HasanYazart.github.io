'use strict';
const siteEnglish = document.documentElement.lang === 'en';
const uiText = (tr, en) => siteEnglish ? en : tr;
document.documentElement.classList.add('js');
const menuButton = document.querySelector('[data-menu-button]');
const menu = document.querySelector('[data-menu]');

if (menuButton && menu) {
  const closeMenu = () => {
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.setAttribute('aria-label', uiText('Menüyü aç', 'Open menu'));
    menu.classList.remove('is-open');
    document.body.classList.remove('menu-open');
    document.querySelectorAll('main, footer').forEach((item) => { item.inert = false; });
  };

  menuButton.addEventListener('click', () => {
    const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!isOpen));
    menuButton.setAttribute('aria-label', isOpen ? uiText('Menüyü aç', 'Open menu') : uiText('Menüyü kapat', 'Close menu'));
    menu.classList.toggle('is-open', !isOpen);
    document.body.classList.toggle('menu-open', !isOpen);
    document.querySelectorAll('main, footer').forEach((item) => { item.inert = !isOpen; });
  });
  menu.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', (event) => {
    if (menuButton.getAttribute('aria-expanded') !== 'true') return;
    if (event.key === 'Escape') { closeMenu(); menuButton.focus(); }
    if (event.key === 'Tab') {
      const last = [...menu.querySelectorAll('a')].at(-1);
      if (event.shiftKey && document.activeElement === menuButton) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); menuButton.focus(); }
    }
  });
  window.addEventListener('resize', () => {
    if (window.innerWidth > 760) closeMenu();
  });
  window.addEventListener('pageshow', closeMenu);
}

const filters = [...document.querySelectorAll('[data-filter]')];
const projectCards = [...document.querySelectorAll('[data-category]')];
const count = document.querySelector('[data-project-count]');

if (filters.length && projectCards.length) {
  filters.forEach((button) => button.addEventListener('click', () => {
    const active = button.dataset.filter;
    filters.forEach((filter) => {
      const selected = filter === button;
      filter.classList.toggle('is-active', selected);
      filter.setAttribute('aria-pressed', String(selected));
    });
    let visible = 0;
    projectCards.forEach((card) => {
      const matches = active === 'all' || card.dataset.category.split(' ').includes(active);
      card.hidden = !matches;
      if (matches) visible++;
    });
    if (count) count.textContent = `${visible} ${uiText('çalışma', 'projects')}`;
  }));
}

const year = document.querySelectorAll('[data-year]');
year.forEach((element) => { element.textContent = new Date().getFullYear(); });

const progress = document.querySelector('[data-progress]');
const story = document.querySelector('[data-story]');
const storyScene = document.querySelector('[data-story-scene]');
const storySteps = [...document.querySelectorAll('[data-story-step]')];
const storyLabel = document.querySelector('[data-story-label]');
const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
let motionPaused = false;
try { motionPaused = sessionStorage.getItem('motion-paused') === 'true'; } catch { /* Optional storage. */ }
let motionAllowed = !motionQuery.matches && !motionPaused;
const motionButton = document.querySelector('[data-motion]');
const applyMotion = () => {
  motionAllowed = !motionQuery.matches && !motionPaused;
  document.documentElement.classList.toggle('motion-paused', !motionAllowed);
  if (motionButton) {
    motionButton.textContent = motionAllowed ? uiText('Hareketi durdur', 'Pause motion') : uiText('Hareket kapalı', 'Motion paused');
    motionButton.setAttribute('aria-pressed', String(!motionAllowed));
    motionButton.disabled = motionQuery.matches;
    motionButton.title = motionQuery.matches ? uiText('Cihazınızın azaltılmış hareket tercihi uygulanıyor.', 'Your reduced-motion preference is enabled.') : uiText('Dekoratif hareketleri aç veya kapat', 'Toggle decorative motion');
  }
  if (!motionAllowed) {
    document.querySelectorAll('[data-depth]').forEach((surface) => {
      surface.style.setProperty('--depth-x', '0deg');
      surface.style.setProperty('--depth-y', '0deg');
    });
    document.querySelectorAll('[data-reveal]').forEach((element) => {
      element.getAnimations?.().forEach((animation) => animation.finish());
    });
  }
  updateStory();
};
motionButton?.addEventListener('click', () => {
  motionPaused = !motionPaused;
  try { sessionStorage.setItem('motion-paused', String(motionPaused)); } catch { /* Optional storage. */ }
  applyMotion();
});
motionQuery.addEventListener('change', applyMotion);
applyMotion();
document.addEventListener('visibilitychange', () => document.documentElement.classList.toggle('page-hidden', document.hidden));
let scrollQueued = false;

const updateScrollEffects = () => {
  const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
  if (progress) progress.style.transform = `scaleX(${maxScroll > 0 ? Math.min(1, Math.max(0, window.scrollY / maxScroll)) : 0})`;
  updateStory();
  scrollQueued = false;
};

window.addEventListener('scroll', () => {
  if (!scrollQueued) {
    scrollQueued = true;
    requestAnimationFrame(updateScrollEffects);
  }
}, { passive: true });
window.addEventListener('resize', updateScrollEffects);
updateScrollEffects();

function updateStory() {
  if (!story || !storyScene || storySteps.length !== 3) return;
  const enabled = motionAllowed && window.innerWidth > 760 && window.innerHeight > 600;
  document.documentElement.classList.toggle('story-motion', enabled);
  if (!enabled) {
    storyScene.style.setProperty('--story-turn', '-32deg');
    storyScene.style.setProperty('--story-tilt', '56deg');
    storyScene.style.setProperty('--layer-gap', '110px');
    story.dataset.activeStage = 'data';
    if (storyLabel) storyLabel.textContent = uiText('Veri · Model · Ürün', 'Data · Model · Product');
    return;
  }
  const centers = storySteps.map((step) => {
    const rect = step.getBoundingClientRect();
    return rect.top + rect.height / 2;
  });
  const position = Math.min(1, Math.max(0, (window.innerHeight / 2 - centers[0]) / Math.max(1, centers[2] - centers[0])));
  const index = Math.min(2, Math.round(position * 2));
  story.dataset.activeStage = ['data', 'model', 'system'][index];
  storyScene.style.setProperty('--story-turn', `${(-32 + position * 20).toFixed(2)}deg`);
  storyScene.style.setProperty('--story-tilt', `${(56 + position * 4).toFixed(2)}deg`);
  storyScene.style.setProperty('--layer-gap', `${(120 - position * 25).toFixed(2)}px`);
  if (storyLabel) storyLabel.textContent = (siteEnglish ? ['Understand the data', 'Develop the solution', 'Bring the product together'] : ['Veriyi anlamak', 'Çözümü geliştirmek', 'Ürünü bir araya getirmek'])[index];
}

if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries, currentObserver) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      if (motionAllowed && entry.target.animate) entry.target.animate([
        { opacity: 0, transform: 'translateY(26px)' },
        { opacity: 1, transform: 'translateY(0)' }
      ], { duration: 650, easing: 'cubic-bezier(.22, 1, .36, 1)' });
      currentObserver.unobserve(entry.target);
    });
  }, { threshold: .08 });
  document.querySelectorAll('[data-reveal]').forEach((element) => observer.observe(element));
}

document.querySelector('[data-copy-email]')?.addEventListener('click', async () => {
  const status = document.querySelector('[data-copy-status]');
  try {
    await navigator.clipboard.writeText('tt41468@gmail.com');
    if (status) status.textContent = uiText('E-posta adresi kopyalandı.', 'Email address copied.');
  } catch {
    if (status) status.textContent = uiText('Adresi seçip kopyalayabilirsiniz: tt41468@gmail.com', 'Select and copy the address: tt41468@gmail.com');
  }
});

// Pointer depth is decorative: touch scrolling and keyboard links stay native.
const pointerQuery = window.matchMedia('(hover: hover) and (pointer: fine)');
document.querySelectorAll('[data-depth]').forEach((surface) => {
  let frame = 0;
  let x = 0;
  let y = 0;
  const reset = () => {
    cancelAnimationFrame(frame);
    frame = 0;
    surface.style.setProperty('--depth-x', '0deg');
    surface.style.setProperty('--depth-y', '0deg');
  };
  surface.addEventListener('pointermove', (event) => {
    if (!motionAllowed || !pointerQuery.matches || event.pointerType === 'touch') return;
    const rect = surface.getBoundingClientRect();
    x = Math.max(-1, Math.min(1, (event.clientX - rect.left) / rect.width * 2 - 1));
    y = Math.max(-1, Math.min(1, (event.clientY - rect.top) / rect.height * 2 - 1));
    if (frame) return;
    frame = requestAnimationFrame(() => {
      if (motionAllowed) {
        surface.style.setProperty('--depth-x', `${(x * 7).toFixed(2)}deg`);
        surface.style.setProperty('--depth-y', `${(-y * 5).toFixed(2)}deg`);
      }
      frame = 0;
    });
  });
  surface.addEventListener('pointerleave', reset);
  surface.addEventListener('pointercancel', reset);
  pointerQuery.addEventListener('change', reset);
});

const explodeButton = document.querySelector('[data-explode]');
explodeButton?.addEventListener('click', () => {
  const expanded = explodeButton.getAttribute('aria-pressed') !== 'true';
  explodeButton.setAttribute('aria-pressed', String(expanded));
  document.querySelector('.hero-object')?.classList.toggle('is-exploded', expanded);
  explodeButton.textContent = expanded ? uiText('Katmanları birleştir ↙', 'Join layers ↙') : uiText('Katmanları ayır ↗', 'Separate layers ↗');
});

// Browser adaptation of MiniRedis-Clone, commit fab2957032b6f1730977fc64433b130429888534.
// Mirrors the selected Java command/store behavior; no TCP, AOF or JVM metrics.
function createMiniRedisDemo(now = () => Date.now()) {
  const values = new Map();
  const expiries = new Map();
  const validLong = (value) => /^[+-]?\d+$/.test(value) && BigInt(value) >= -(2n ** 63n) && BigInt(value) < 2n ** 63n;
  const remove = (key) => { expiries.delete(key); return values.delete(key); };
  return {
    clear() { values.clear(); expiries.clear(); },
    sweep() { for (const [key, expiry] of expiries) if (expiry < now()) remove(key); },
    entries() { return [...values].map(([key, value]) => ({ key, value, expiry: expiries.get(key) })); },
    execute(line) {
      const cleaned = [...line].reduce((text, char) => char === '\b' || char === '\x7f' ? text.slice(0, -1) : text + char, '');
      const args = cleaned.trim().split(/\s+/);
      const command = args[0].toUpperCase();
      if (!command) return '';
      const signatures = {
        SET: [3, 'HATA: SET komutu 2 parametre alir. (Ornek: SET ad Hasan)'],
        GET: [2, 'HATA: GET komutu 1 parametre alir. (Ornek: GET ad)'],
        DEL: [2, 'HATA: DEL komutu 1 parametre alir. (Ornek: DEL ad)'],
        SETEX: [4, 'HATA: SETEX komutu 3 parametre alir. (Ornek: SETEX mesaj 15 selam)'],
        TTL: [2, 'HATA: TTL komutu 1 parametre alir. (Ornek: TTL mesaj)'],
        INCR: [2, 'HATA: INCR komutu 1 parametre alir. (Ornek: INCR bilet)'],
        DECR: [2, 'HATA: DECR komutu 1 parametre alir. (Ornek: DECR stok)']
      };
      if (Object.hasOwn(signatures, command) && args.length !== signatures[command][0]) return signatures[command][1];
      const key = args[1];
      switch (command) {
        case 'SET': values.set(key, args[2]); expiries.delete(key); return 'OK';
        case 'GET':
          if (expiries.has(key) && expiries.get(key) < now()) remove(key);
          return values.get(key) ?? '(nil)';
        case 'DEL': return `(integer) ${remove(key) ? 1 : 0}`;
        case 'SETEX': {
          if (!/^[+-]?\d+$/.test(args[2]) || Number(args[2]) < -2147483648 || Number(args[2]) > 2147483647) return 'HATA: Saniye degeri bir sayi olmalidir!';
          values.set(key, args[3]); expiries.set(key, now() + Number(args[2]) * 1000); return 'OK';
        }
        case 'TTL': {
          if (!values.has(key)) return '(integer) -2';
          if (!expiries.has(key)) return '(integer) -1';
          const left = expiries.get(key) - now();
          return `(integer) ${left > 0 ? Math.floor(left / 1000) : -2}`;
        }
        case 'INCR':
        case 'DECR': {
          const value = values.get(key) ?? '0';
          if (!validLong(value)) return 'HATA: Deger bir tam sayi degil!';
          const updated = String(BigInt.asIntN(64, BigInt(value) + (command === 'INCR' ? 1n : -1n)));
          values.set(key, updated); return `(integer) ${updated}`;
        }
        case 'FLUSHDB': this.clear(); return 'OK';
        case 'INFO':
        case 'QUIT': return 'Bu komutu GitHub deposundaki Java uygulamasında deneyin; tarayıcı uyarlamasına dahil değil.';
        default: return 'HATA: Bilinmeyen komut!';
      }
    }
  };
}

const redisDemo = document.querySelector('[data-redis-demo]');
if (redisDemo) {
  const demoEnglish = document.documentElement?.lang === 'en';
  const demoText = (tr, en) => demoEnglish ? en : tr;
  const engine = createMiniRedisDemo();
  const form = document.querySelector('[data-redis-form]');
  const input = document.querySelector('#redis-command');
  const output = document.querySelector('[data-redis-output]');
  const memory = document.querySelector('[data-redis-memory]');
  const counter = document.querySelector('[data-redis-count]');
  const commandHistory = [];
  let historyPosition = 0;
  let draft = '';
  const appendLog = (entry) => {
    output.append(entry);
    while (output.children.length > 80) output.firstElementChild.remove();
    output.scrollTop = output.scrollHeight;
  };
  const renderMemory = () => {
    const entries = engine.entries();
    counter.textContent = `${entries.length} ${demoText('anahtar', 'keys')}`;
    memory.replaceChildren();
    if (!entries.length) {
      const item = document.createElement('li');
      item.className = 'memory-empty'; item.textContent = demoText('Henüz veri yok.', 'No data yet.'); memory.append(item);
    }
    for (const {key, value, expiry} of entries) {
      const item = document.createElement('li');
      const name = document.createElement('strong'); name.textContent = key;
      const data = document.createElement('code'); data.textContent = value;
      const ttl = document.createElement('span');
      ttl.textContent = expiry === undefined ? demoText('Süresiz', 'No expiry') : `${Math.max(0, Math.floor((expiry - Date.now()) / 1000))} ${demoText('sn kaldı', 'seconds left')}`;
      item.append(name, data, ttl); memory.append(item);
    }
  };
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const command = input.value.trim();
    if (!command) return;
    // Only new keys consume capacity; expired keys free capacity before checking.
    engine.sweep();
    const parts = command.split(/\s+/);
    const entries = engine.entries();
    if (entries.length >= 100 && /^(SET|SETEX|INCR|DECR)$/i.test(parts[0]) && parts[1] && !entries.some(entry => entry.key === parts[1])) {
      const message = document.createElement('p'); message.textContent = demoText('Tarayıcı demosu 100 anahtarla sınırlıdır. FLUSHDB ile temizleyebilirsiniz.', 'The browser demo is limited to 100 keys. Use FLUSHDB to clear it.');
      appendLog(message); renderMemory(); return;
    }
    const entry = document.createElement('div'); entry.className = 'terminal-entry';
    const prompt = document.createElement('p'); prompt.className = 'terminal-command'; prompt.textContent = `› ${command}`;
    const result = document.createElement('p'); result.textContent = engine.execute(command);
    result.className = result.textContent.startsWith('HATA') ? 'terminal-error' : 'terminal-result';
    entry.append(prompt, result); appendLog(entry);
    commandHistory.push(command); if (commandHistory.length > 80) commandHistory.shift();
    historyPosition = commandHistory.length; draft = ''; input.value = ''; renderMemory(); input.focus();
  });
  input.addEventListener('keydown', (event) => {
    if (!['ArrowUp', 'ArrowDown'].includes(event.key) || !commandHistory.length) return;
    event.preventDefault();
    if (historyPosition === commandHistory.length) draft = input.value;
    historyPosition = Math.max(0, Math.min(commandHistory.length, historyPosition + (event.key === 'ArrowUp' ? -1 : 1)));
    input.value = commandHistory[historyPosition] ?? draft;
  });
  document.querySelectorAll('[data-redis-example]').forEach((button) => button.addEventListener('click', () => {
    input.value = button.dataset.redisExample; input.focus();
  }));
  document.querySelector('[data-redis-reset]').addEventListener('click', () => {
    engine.clear(); commandHistory.length = 0; historyPosition = 0; draft = ''; input.value = '';
    const message = document.createElement('p'); message.className = 'terminal-hint'; message.textContent = demoText('Demo sıfırlandı. Yeni bir komut yazabilirsiniz.', 'Demo reset. Enter a new command.');
    output.replaceChildren(message); renderMemory(); input.focus();
  });
  // Match the Java store's one-second active expiry scan. Restart after bfcache restore.
  let sweepTimer;
  const startSweep = () => { clearInterval(sweepTimer); sweepTimer = setInterval(() => { engine.sweep(); renderMemory(); }, 1000); };
  window.addEventListener('pagehide', () => clearInterval(sweepTimer));
  window.addEventListener('pageshow', startSweep);
  startSweep();
}
