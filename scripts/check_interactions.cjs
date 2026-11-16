// Contract checks against the actual site script; no browser/layout emulation.
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = join(__dirname, '..');
const source = readFileSync(join(root, 'site.js'), 'utf8');
class Element {
  constructor(dataset = {}) {
    this.dataset = dataset; this.attrs = {}; this.events = {}; this.hidden = false;
    this.classes = new Set(); this.textContent = ''; this.style = { setProperty: (k, v) => { this.style[k] = v; } };
    this.classList = { add: k => this.classes.add(k), remove: k => this.classes.delete(k), toggle: (k, v) => v ? this.classes.add(k) : this.classes.delete(k) };
  }
  setAttribute(k, v) { this.attrs[k] = v; }
  getAttribute(k) { return this.attrs[k]; }
  addEventListener(k, fn) { (this.events[k] ??= []).push(fn); }
  async dispatchEvent(e) { for (const fn of this.events[e.type] ?? []) await fn(e); }
  focus() { this.document.activeElement = this; }
  querySelectorAll() { return this.links ?? []; }
}
function fixture({ empty = false, blockedStorage = false, reduced = false, desktop = false, english = false } = {}) {
  const nodes = Object.fromEntries(['menu-button','menu','project-count','progress','story','story-scene','story-label','motion','copy-email','copy-status'].map(k => [k, new Element()]));
  nodes['menu-button'].attrs['aria-expanded'] = 'false';
  const cards = [...readFileSync(join(root, 'projects.html'), 'utf8').matchAll(/data-category="([^"]+)"/g)].map(m => new Element({category:m[1]}));
  const filters = ['all','ai','systems','vision','apps'].map(filter => new Element({filter}));
  const steps = ['data','model','system'].map(storyStep => new Element({storyStep}));
  const background = [new Element(), new Element()];
  const doc = new Element(); doc.documentElement = new Element(); doc.documentElement.scrollHeight = 1000; doc.body = new Element();
  doc.documentElement.lang = english ? 'en' : 'tr';
  doc.querySelector = s => empty ? null : nodes[s.replace('[data-', '').replace(']', '')] ?? null;
  doc.querySelectorAll = s => empty ? [] : ({'[data-filter]':filters, '[data-category]':cards, '[data-story-step]':steps, 'main, footer':background}[s] ?? []);
  nodes.menu.links = [new Element(),new Element(),new Element(),new Element()];
  [nodes['menu-button'],...nodes.menu.links].forEach(e => {e.document = doc;});
  const media = new Element(); media.matches = reduced;
  const win = new Element(); win.matchMedia = () => media; win.innerHeight = 500; win.innerWidth = 390; win.scrollY = 250;
  if (desktop) { win.innerWidth = 1440; win.innerHeight = 900; }
  steps.forEach((step, i) => { step.getBoundingClientRect = () => ({top:1500 + i * 765 - win.scrollY, height:765}); });
  const storage = new Map();
  const context = {document:doc, window:win, sessionStorage:{getItem:k => {if(blockedStorage) throw Error(); return storage.get(k);}, setItem:(k,v) => {if(blockedStorage) throw Error(); storage.set(k,v);}}, navigator:{clipboard:{writeText:async text => { context.copied = text; }}}, requestAnimationFrame: fn => fn(), Event:class {constructor(type){this.type=type;}}, console};
  vm.runInNewContext(source, context);
  return {nodes,cards,filters,steps,background,doc,media,win,context};
}
(async () => {
  fixture({empty:true}); fixture({blockedStorage:true});
  const f = fixture(); const click = element => element.dispatchEvent({type:'click'});
  const en = fixture({english:true});
  await click(en.filters[1]); assert.equal(en.nodes['project-count'].textContent, '7 projects');
  await click(en.nodes['menu-button']); assert.equal(en.nodes['menu-button'].getAttribute('aria-label'), 'Close menu');
  assert.equal(en.nodes['story-label'].textContent, 'Data · Model · Product');
  await click(en.nodes['copy-email']); assert.equal(en.nodes['copy-status'].textContent, 'Email address copied.');
  for (const [i, expected] of [9,7,2,3,3].entries()) {
    await click(f.filters[i]); assert.equal(f.cards.filter(c => !c.hidden).length, expected);
    assert.equal(f.nodes['project-count'].textContent, `${expected} çalışma`);
    assert.equal(f.filters.filter(e => e.getAttribute('aria-pressed') === 'true').length, 1);
  }
  await click(f.nodes['menu-button']); assert.equal(f.nodes['menu-button'].getAttribute('aria-expanded'), 'true'); assert.ok(f.background.every(e => e.inert));
  f.doc.activeElement = f.nodes.menu.links.at(-1);
  let prevented = false;
  await f.doc.dispatchEvent({type:'keydown',key:'Tab',preventDefault(){prevented=true;}});
  assert.ok(prevented); assert.equal(f.doc.activeElement, f.nodes['menu-button']);
  await f.doc.dispatchEvent({type:'keydown',key:'Escape'}); assert.ok(f.background.every(e => !e.inert)); assert.equal(f.nodes['menu-button'].getAttribute('aria-expanded'), 'false');
  await click(f.nodes.motion); assert.ok(f.doc.documentElement.classes.has('motion-paused'));
  await click(f.nodes.motion); assert.ok(!f.doc.documentElement.classes.has('motion-paused'));
  f.media.matches = true; await f.media.dispatchEvent({type:'change'}); assert.ok(f.nodes.motion.disabled); assert.ok(f.doc.documentElement.classes.has('motion-paused'));
  assert.ok(fixture({reduced:true}).nodes.motion.disabled);
  assert.equal(f.nodes['story-label'].textContent, 'Veri · Model · Ürün');
  assert.ok(!f.doc.documentElement.classes.has('story-motion'));
  const desktop = fixture({desktop:true});
  assert.ok(desktop.doc.documentElement.classes.has('story-motion'));
  for (const [i, stage] of ['data', 'model', 'system'].entries()) {
    desktop.win.scrollY = 1500 + i * 765 + 382.5 - 450;
    await desktop.win.dispatchEvent({type:'scroll'});
    assert.equal(desktop.nodes.story.dataset.activeStage, stage);
    assert.equal(desktop.nodes['story-scene'].style['--story-turn'], `${(-32 + i * 10).toFixed(2)}deg`);
  }
  desktop.win.scrollY = 0; await desktop.win.dispatchEvent({type:'scroll'});
  assert.equal(desktop.nodes['story-scene'].style['--layer-gap'], '120.00px');
  desktop.win.scrollY = 99999; await desktop.win.dispatchEvent({type:'scroll'});
  assert.equal(desktop.nodes['story-scene'].style['--layer-gap'], '95.00px');
  await click(desktop.nodes.motion);
  assert.ok(!desktop.doc.documentElement.classes.has('story-motion'));
  assert.equal(desktop.nodes['story-scene'].style['--story-turn'], '-32deg');
  await click(f.nodes['copy-email']); assert.equal(f.context.copied, 'tt41468@gmail.com');
  f.context.navigator.clipboard.writeText = async () => {throw Error('denied');}; await click(f.nodes['copy-email']); assert.match(f.nodes['copy-status'].textContent, /tt41468@gmail.com/);
  assert.equal(f.nodes.progress.style.transform, 'scaleX(0.5)');
  console.log('PASS: 5 filters, mobile focus/Escape, motion preference, blocked storage, 3 scroll scenes and bounds, mobile/static fallback, clipboard success/failure, empty pages and scroll progress.');
})().catch(error => { console.error(error); process.exitCode = 1; });
