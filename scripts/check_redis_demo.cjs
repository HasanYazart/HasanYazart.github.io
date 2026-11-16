// Behavior fixtures read against the actual Java sources at MiniRedis-Clone/fab2957.
// This verifies the browser adaptation; it does not run a JVM or test TCP/AOF.
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = readFileSync(join(__dirname, '..', 'site.js'), 'utf8');
const start = source.indexOf('function createMiniRedisDemo(');
const end = source.indexOf('\nconst redisDemo =', start);
assert.ok(start >= 0 && end > start);
const create = vm.runInNewContext(source.slice(start, end) + '\ncreateMiniRedisDemo;');
let now = 10000;
const db = create(() => now);
let cases = 0;
function check(command, expected) { assert.equal(db.execute(command), expected, command); cases++; }
check('GET missing', '(nil)');
check('SET ad Hasan', 'OK');
check('get ad', 'Hasan');
check('TTL ad', '(integer) -1');
check('DEL ad', '(integer) 1');
check('DEL ad', '(integer) 0');
check('TTL ad', '(integer) -2');
check('SET ad Hasan Yazar', 'HATA: SET komutu 2 parametre alir. (Ornek: SET ad Hasan)');
check('SET ad "Hasan"', 'OK');
check('GET ad', '"Hasan"'); // Quotes are literal in ClientHandler, not a shell parser.
check('SETEX mesaj 15 selam', 'OK');
check('TTL mesaj', '(integer) 15');
now += 14500;
check('TTL mesaj', '(integer) 0');
check('GET mesaj', 'selam');
now += 501;
check('TTL mesaj', '(integer) -2');
check('GET mesaj', '(nil)'); // Lazy deletion.
check('SETEX transient 1 test', 'OK');
now += 1001; db.sweep(); // Active deletion.
assert.ok(!db.entries().some(entry => entry.key === 'transient'));
check('SETEX permanent 1 old', 'OK');
check('SET permanent new', 'OK');
now += 2000; db.sweep();
check('GET permanent', 'new');
check('TTL permanent', '(integer) -1');
check('SETEX x invalid value', 'HATA: Saniye degeri bir sayi olmalidir!');
check('SETEX x 2147483648 value', 'HATA: Saniye degeri bir sayi olmalidir!');
check('INCR ziyaret', '(integer) 1');
check('INCR ziyaret', '(integer) 2');
check('DECR ziyaret', '(integer) 1');
check('DECR absent', '(integer) -1');
check('SET text hello', 'OK');
check('INCR text', 'HATA: Deger bir tam sayi degil!');
check('SET large 9223372036854775807', 'OK');
check('INCR large', '(integer) -9223372036854775808'); // Java long overflow.
check('DECR large', '(integer) 9223372036854775807');
check('SET tooLarge 9223372036854775808', 'OK');
check('DECR tooLarge', 'HATA: Deger bir tam sayi degil!');
check('KEYS', 'HATA: Bilinmeyen komut!');
check('HELP', 'HATA: Bilinmeyen komut!');
check('EXISTS ad', 'HATA: Bilinmeyen komut!');
check('FLUSHDB', 'OK');
assert.equal(db.entries().length, 0);
check('SET __proto__ safe', 'OK');
check('GET __proto__', 'safe');
check('SET html <img/src=x/onerror=alert(1)>', 'OK');
check('GET html', '<img/src=x/onerror=alert(1)>');
for (const command of ['GET', 'DEL', 'TTL', 'INCR', 'DECR', 'SET', 'SETEX']) {
  assert.match(db.execute(command), /^HATA:/); cases++;
}
assert.match(db.execute('INFO'), /Java uygulamasında/);
assert.match(db.execute('QUIT'), /Java uygulamasında/);
db.clear(); assert.equal(db.entries().length, 0);
console.log(`PASS: ${cases} source-based command fixtures, TTL cleanup, reset, Java integer bounds and unsupported-command handling.`);
