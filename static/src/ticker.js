import './app.css';

// Ticker logic: poll `/api/ticker/` and render a continuously scrolling track.
const TICKER_POLL_INTERVAL = 5000; // ms
const TICKER_FETCH_URL = '/api/ticker/';
const NEWS_POLL_INTERVAL = 30000; // ms
const NEWS_FETCH_URL = '/api/latest-event/';

function arrowForDirection(direction) {
    if (direction > 0) return '▲';
    if (direction < 0) return '▼';
    return '•';
}

let __ticker_initialized = false;
let __ticker_item_count = 0;

function createItemElement(it) {
    const cls = it.direction > 0 ? 'ticker-up' : (it.direction < 0 ? 'ticker-down' : 'ticker-neutral');
    const price = (typeof it.price === 'number') ? it.price.toFixed(2) : parseFloat(it.price).toFixed(2);
    const el = document.createElement('div');
    el.className = `ticker-item inline-flex items-center gap-2 px-4 py-1 rounded-full bg-base-100 shadow-sm ${cls}`;
    el.setAttribute('role', 'listitem');
    el.dataset.symbol = it.symbol;

    const sym = document.createElement('span');
    sym.className = 'font-semibold ticker-symbol';
    sym.textContent = it.symbol;

    const pr = document.createElement('span');
    pr.className = 'text-xs text-muted ticker-price';
    pr.textContent = `$${price}`;

    const ar = document.createElement('span');
    ar.className = 'text-sm ticker-arrow';
    ar.textContent = arrowForDirection(it.direction);

    el.appendChild(sym);
    el.appendChild(pr);
    el.appendChild(ar);
    return el;
}

function renderTicker(items) {
    const track = document.getElementById('ticker-track');
    if (!track) return;

    // If not initialized or item count changed, build DOM nodes once (two copies)
    if (!__ticker_initialized || items.length !== __ticker_item_count) {
        track.innerHTML = '';
        if (items.length === 0) return;
        for (let copy = 0; copy < 2; copy++) {
            for (const it of items) {
                track.appendChild(createItemElement(it));
            }
        }
        __ticker_initialized = true;
        __ticker_item_count = items.length;

        // ensure animation class is present (only add, don't restart on updates)
        if (!track.classList.contains('ticker-animate')) {
            track.classList.add('ticker-animate');
        }
    } else {
        // Update existing nodes in-place to avoid restarting animation
        const children = track.children;
        const n = __ticker_item_count;
        for (let i = 0; i < n; i++) {
            const it = items[i];
            const el1 = children[i];
            const el2 = children[i + n];
            if (!el1 || !el2) continue;
            // update symbol
            const sym1 = el1.querySelector('.ticker-symbol');
            const pr1 = el1.querySelector('.ticker-price');
            const ar1 = el1.querySelector('.ticker-arrow');
            const sym2 = el2.querySelector('.ticker-symbol');
            const pr2 = el2.querySelector('.ticker-price');
            const ar2 = el2.querySelector('.ticker-arrow');
            if (sym1) sym1.textContent = it.symbol;
            if (pr1) pr1.textContent = `$${(typeof it.price === 'number' ? it.price.toFixed(2) : parseFloat(it.price).toFixed(2))}`;
            if (ar1) ar1.textContent = arrowForDirection(it.direction);
            if (sym2) sym2.textContent = it.symbol;
            if (pr2) pr2.textContent = `$${(typeof it.price === 'number' ? it.price.toFixed(2) : parseFloat(it.price).toFixed(2))}`;
            if (ar2) ar2.textContent = arrowForDirection(it.direction);
                // update color class based on direction (use ticker-specific classes)
                el1.classList.remove('ticker-up', 'ticker-down', 'ticker-neutral');
                el2.classList.remove('ticker-up', 'ticker-down', 'ticker-neutral');
                const cls = it.direction > 0 ? 'ticker-up' : (it.direction < 0 ? 'ticker-down' : 'ticker-neutral');
                el1.classList.add(cls);
                el2.classList.add(cls);
        }
    }

    // compute slow duration and translate distance so the ticker scrolls across the full viewport
    try {
        const totalWidth = track.scrollWidth || 0; // duplicated content width
        const contentHalf = totalWidth / 2 || 0; // width of one copy
        const viewport = window.innerWidth || document.documentElement.clientWidth || 0;

        // distance to move so that content has fully passed the viewport: contentHalf + viewport
        const translatePx = -(contentHalf + viewport);

        // choose a slow speed in pixels/sec
        const speedPxPerSec = 8; // lower => slower
        let durationSec = Math.abs((contentHalf + viewport) / speedPxPerSec);
        if (!isFinite(durationSec) || durationSec < 40) durationSec = 40;
        if (durationSec > 600) durationSec = 600;

        track.style.setProperty('--ticker-duration', `${durationSec}s`);
        track.style.setProperty('--ticker-translate', `${translatePx}px`);
    } catch (e) {
        // ignore
    }
}

async function fetchAndUpdate() {
    try {
        const res = await fetch(TICKER_FETCH_URL, { cache: 'no-store' });
        if (!res.ok) return;
        const data = await res.json();
        renderTicker(data);
    } catch (e) {
        // decorative: ignore errors
    }
}


function renderNews(eventObj) {
    const el = document.getElementById('news-bar-text');
    if (!el) return false;

    if (!eventObj || !eventObj.event) {
        el.textContent = 'No notable news';
        return true;
    }

    const ev = eventObj.event;
    // parse created_at and determine age
    let createdAt = null;
    try {
        createdAt = Date.parse(ev.created_at);
    } catch (e) {
        createdAt = null;
    }

    const now = Date.now();
    const FIVE_MIN = 5 * 60 * 1000;

    if (!createdAt || (now - createdAt) > FIVE_MIN) {
        el.textContent = 'No notable news';
        return true;
    }

    // prefer server-rendered text (placeholder replaced). fall back to name+text
    const rendered = ev.rendered_text || null;
    if (rendered) {
        el.textContent = rendered;
    } else {
        const text = ev.text || '';
        const name = ev.name || '';
        el.textContent = `${name}: ${text}`;
    }

    return true;
}

async function fetchNewsAndUpdate() {
    try {
        const res = await fetch(NEWS_FETCH_URL, { cache: 'no-store' });
        if (!res.ok) return;
        const data = await res.json();
        // Try to render; if the news element isn't present yet, observe the DOM and
        // render once it appears (helps when this script runs before template insertion).
        const didRender = renderNews(data);
        if (!didRender) {
            // wait for the element to be added to the DOM, then render once
            const observer = new MutationObserver((mutations, obs) => {
                const el = document.getElementById('news-bar-text');
                if (el) {
                    renderNews(data);
                    obs.disconnect();
                }
            });
            observer.observe(document.documentElement || document.body, { childList: true, subtree: true });
            // safety: stop observing after 10s
            setTimeout(() => observer.disconnect(), 10000);
        }
    } catch (e) {
        // transient network error: try again shortly to avoid long gaps
        setTimeout(fetchNewsAndUpdate, 5000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetchAndUpdate();
    setInterval(fetchAndUpdate, TICKER_POLL_INTERVAL);

    // News bar: fetch initially and poll periodically
    fetchNewsAndUpdate();
    setInterval(fetchNewsAndUpdate, NEWS_POLL_INTERVAL);

    // When the page becomes visible again (or regains focus), fetch immediately
    // so the news line updates promptly after tab switches / background throttling.
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') fetchNewsAndUpdate();
    });
    window.addEventListener('focus', () => fetchNewsAndUpdate());
});
