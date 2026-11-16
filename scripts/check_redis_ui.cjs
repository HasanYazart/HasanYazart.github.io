// Exercise the real terminal event handlers without claiming browser/layout coverage.
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
class Node {
  constructor() { this.children = []; this.events = {}; this.dataset = {}; this.value = ''; this.textContent = ''; }
  addEventListener(type, fn) { this.events[type] = fn; }
  append(...nodes) { nodes.forEach(node => { node.parent = this; this.children.push(node); }); }
  replaceChildren(...nodes) { this.children = []; this.append(...nodes); }
  remove() { this.parent.children.splice(this.parent.children.indexOf(this), 1); }
  get firstElementChild() { return this.children[0]; }
  focus() { this.focused = true; }
  fire(type, fields = {}) { this.events[type]({ preventDefault() {}, ...fields }); }
}
const nodes = Object.fromEntries(['[data-redis-demo]', '[data-redis-form]', '#redis-command', '[data-redis-output]', '[data-redis-memory]', '[data-redis-count]', '[data-redis-reset]'].map(key => [key, new Node()]));
const example = new Node(); example.dataset.redisExample = 'SET ad Hasan';
const window = new Node();
let activeTimers = 0;
const script = readFileSync(join(__dirname, '..', 'site.js'), 'utf8');
vm.runInNewContext(script.slice(script.indexOf('function createMiniRedisDemo(')), {
  document: {
    querySelector: key => nodes[key],
    querySelectorAll: () => [example],
    createElement: () => new Node()
  },
  window,
  setInterval: () => { activeTimers++; return 1; },
  clearInterval: timer => { if (timer) activeTimers--; }
});
const input = nodes['#redis-command'];
const output = nodes['[data-redis-output]'];
const memory = nodes['[data-redis-memory]'];
function submit(value) { input.value = value; nodes['[data-redis-form]'].fire('submit'); }
function lastResult() { return output.children.at(-1).children[1].textContent; }
example.fire('click'); assert.equal(input.value, 'SET ad Hasan'); assert.ok(input.focused);
submit(input.value); assert.equal(lastResult(), 'OK'); assert.equal(input.value, '');
assert.equal(nodes['[data-redis-count]'].textContent, '1 anahtar');
assert.equal(memory.children[0].children[0].textContent, 'ad');
assert.equal(memory.children[0].children[1].textContent, 'Hasan');
submit('GET ad'); assert.equal(lastResult(), 'Hasan');
input.value = 'unfinished'; input.fire('keydown', {key:'ArrowUp'}); assert.equal(input.value, 'GET ad');
input.fire('keydown', {key:'ArrowDown'}); assert.equal(input.value, 'unfinished');
submit('SET markup <img/src=x/onerror=alert(1)>');
assert.equal(memory.children[1].children[1].textContent, '<img/src=x/onerror=alert(1)>');
assert.equal(memory.children[1].children[1].children.length, 0);
submit('BOGUS'); assert.equal(output.children.at(-1).children[1].className, 'terminal-error');
for (let i = 0; i < 85; i++) submit('GET ad');
assert.equal(output.children.length, 80);
nodes['[data-redis-reset]'].fire('click');
assert.equal(nodes['[data-redis-count]'].textContent, '0 anahtar');
assert.equal(output.children.length, 1);
assert.equal(input.value, '');
for (let i = 0; i < 100; i++) submit('SET k' + i + ' value');
submit('SET k0 updated'); assert.equal(lastResult(), 'OK');
submit('GET k0'); assert.equal(lastResult(), 'updated');
submit('SET k0 1'); submit('INCR k0'); assert.equal(lastResult(), '(integer) 2');
for (let i = 0; i < 200; i++) submit('SET overflow value');
assert.equal(output.children.length, 80);
assert.equal(nodes['[data-redis-count]'].textContent, '100 anahtar');
submit('DEL k1'); submit('SET replacement value'); assert.equal(lastResult(), 'OK');
nodes['[data-redis-reset]'].fire('click');
assert.equal(activeTimers, 1);
window.fire('pagehide'); assert.equal(activeTimers, 0);
// ClearInterval is idempotent in browsers; model the stopped interval before restore.
activeTimers = 1;
window.fire('pageshow'); assert.equal(activeTimers, 1);
console.log('PASS: demo mounting, example input, submit/output, memory panel, command history, text-only rendering, log bound, reset and timer lifecycle.');
