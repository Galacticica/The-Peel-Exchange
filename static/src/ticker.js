/*
* File: ticker.js
* Author: Reagan Zierke <reaganzierke@gmail.com>
* Date: 2025-11-08
* Description: JavaScript for the stock ticker and news bar functionality.
*/
import './app.css';

const TICKER_POLL_INTERVAL = 5000; 
const TICKER_FETCH_URL = '/api/ticker/';
const NEWS_POLL_INTERVAL = 30000; 
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
    pr.textContent = `${price} 🍌`;

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

        if (!track.classList.contains('ticker-animate')) {
            track.classList.add('ticker-animate');
        }
    } else {
        const children = track.children;
        const n = __ticker_item_count;
        for (let i = 0; i < n; i++) {
            const it = items[i];
            const el1 = children[i];
            const el2 = children[i + n];
            if (!el1 || !el2) continue;
            const sym1 = el1.querySelector('.ticker-symbol');
            const pr1 = el1.querySelector('.ticker-price');
            const ar1 = el1.querySelector('.ticker-arrow');
            const sym2 = el2.querySelector('.ticker-symbol');
            const pr2 = el2.querySelector('.ticker-price');
            const ar2 = el2.querySelector('.ticker-arrow');
            if (sym1) sym1.textContent = it.symbol;
            if (pr1) pr1.textContent = `${(typeof it.price === 'number' ? it.price.toFixed(2) : parseFloat(it.price).toFixed(2))} 🍌`;
            if (ar1) ar1.textContent = arrowForDirection(it.direction);
            if (sym2) sym2.textContent = it.symbol;
            if (pr2) pr2.textContent = `${(typeof it.price === 'number' ? it.price.toFixed(2) : parseFloat(it.price).toFixed(2))} 🍌`;
            if (ar2) ar2.textContent = arrowForDirection(it.direction);
                el1.classList.remove('ticker-up', 'ticker-down', 'ticker-neutral');
                el2.classList.remove('ticker-up', 'ticker-down', 'ticker-neutral');
                const cls = it.direction > 0 ? 'ticker-up' : (it.direction < 0 ? 'ticker-down' : 'ticker-neutral');
                el1.classList.add(cls);
                el2.classList.add(cls);
        }
    }

    try {
        const totalWidth = track.scrollWidth || 0; 
        const contentHalf = totalWidth / 2 || 0;
        const viewport = window.innerWidth || document.documentElement.clientWidth || 0;

        const translatePx = -(contentHalf + viewport);

        const speedPxPerSec = 8; 
        let durationSec = Math.abs((contentHalf + viewport) / speedPxPerSec);
        if (!isFinite(durationSec) || durationSec < 40) durationSec = 40;
        if (durationSec > 600) durationSec = 600;

        track.style.setProperty('--ticker-duration', `${durationSec}s`);
        track.style.setProperty('--ticker-translate', `${translatePx}px`);
    } catch (e) {
        // decorative: ignore errors
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
        const didRender = renderNews(data);
        if (!didRender) {
            const observer = new MutationObserver((mutations, obs) => {
                const el = document.getElementById('news-bar-text');
                if (el) {
                    renderNews(data);
                    obs.disconnect();
                }
            });
            observer.observe(document.documentElement || document.body, { childList: true, subtree: true });
            setTimeout(() => observer.disconnect(), 10000);
        }
    } catch (e) {
        setTimeout(fetchNewsAndUpdate, 5000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetchAndUpdate();
    setInterval(fetchAndUpdate, TICKER_POLL_INTERVAL);

    fetchNewsAndUpdate();
    setInterval(fetchNewsAndUpdate, NEWS_POLL_INTERVAL);

    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') fetchNewsAndUpdate();
    });
    window.addEventListener('focus', () => fetchNewsAndUpdate());
});
