"""Build original, explicitly illustrative SVG covers from portfolio project briefs.

No fabricated measurements or application screenshots. Redis commands follow its
public README; NLP uses the separately downloaded original repository graphics.
"""
from pathlib import Path
from html import escape
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'projects'
OUT.mkdir(exist_ok=True)


def rect(x, y, w, h, fill, r=0, stroke='none', extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" {extra}/>'


def text(x, y, value, size=18, color='#d9e1ee', weight=400, mono=False):
    family = 'Consolas,monospace' if mono else 'Segoe UI,Arial,sans-serif'
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{family}" font-size="{size}" font-weight="{weight}">{escape(value)}</text>'


def line(x1, y1, x2, y2, color='#324155', width=1, extra=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" {extra}/>'


def circle(x, y, radius, fill, extra=''):
    return f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}" {extra}/>'


def path(d, fill='none', stroke='#748499', width=2, extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>'


def pill(x, y, label, color='#7dd8cb', bg='#203e40', width=160):
    return rect(x, y, width, 34, bg, 17) + text(x+15, y+23, label, 14, color, 600)


def window(title, accent='#aa9ce6', bg='#131b29'):
    title_color = '#776779' if bg in ('#f4f0ea', '#ebe8ef') else '#b1bdcf'
    return rect(55, 75, 1090, 555, '#000000', 22, extra='opacity=".13" transform="translate(0 15)"') + rect(55, 75, 1090, 555, bg, 22, '#ffffff24') + line(55, 132, 1145, 132, '#ffffff1a') + ''.join(circle(83+i*19, 104, 5, color) for i, color in enumerate([accent, '#66748a', '#485669'])) + text(160, 111, title, 17, title_color, mono=True)


def save(name, content, bg='#e8e4ef', accent='#bbb0d4'):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720">
<defs><radialGradient id="ambient"><stop stop-color="{accent}" stop-opacity=".35"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient><linearGradient id="paper" x2="1" y2="1"><stop stop-color="#f8f6f0"/><stop offset="1" stop-color="#dedbd1"/></linearGradient><linearGradient id="wood" x2="1" y2="1"><stop stop-color="#ddbe8c"/><stop offset="1" stop-color="#ac8050"/></linearGradient></defs>
{rect(0,0,1200,720,bg)}<ellipse cx="600" cy="360" rx="620" ry="370" fill="url(#ambient)"/>{content}</svg>'''
    (OUT / f'{name}.svg').write_text(svg, encoding='utf-8')


# Disaster relief: schematic urban map, requests and a priority queue.
s = window('İhtiyaç önceliklendirme / çalışma akışı', '#d9a16c')
s += rect(80, 155, 650, 450, '#e8e6df', 10)
for row in range(5):
    for col in range(7):
        x, y = 95+col*90, 173+row*84
        s += rect(x, y, 65 if col % 2 else 71, 57, ['#d7d4ca', '#d0d6cc', '#ddd8d0'][(row+col)%3], 4, '#c9c6bd')
s += path('M80 495 C220 445 240 505 375 410 S540 375 730 330', stroke='#bbcfd0', width=32)
s += path('M140 155 L298 605 M80 340 L730 255 M450 155 L535 605', stroke='#faf8f1', width=15)
s += path('M210 400 L325 370 L440 400 L570 280', stroke='#ba774d', width=4, extra='stroke-dasharray="8 7"')
for x,y,n,c in [(210,400,'1','#bd715a'),(440,400,'2','#bd715a'),(570,280,'3','#a58a55'),(325,235,'+','#527f78')]:
    s += circle(x,y,33,c,'opacity=".15"')+circle(x,y,17,c)+text(x-5,y+6,n,17,'#fff',700)
s += pill(101, 175, 'ŞEMATİK HARİTA', '#526963', '#f7f7ef', 180)
s += text(760, 184, 'İhtiyaç kuyruğu', 23, '#f0eee9', 600)+text(760,213,'Kategori → aciliyet → kaynak',14,'#91a0b0')
for i,(title,sub,col) in enumerate([('Sağlık','Tıbbi destek talebi','#dc9782'),('Barınma','Geçici yaşam alanı','#dbbb7b'),('Gıda ve su','Temel ihtiyaç desteği','#8bc4b7')]):
    y=240+i*102
    s += rect(758,y,358,86,'#1e2938',10)+rect(758,y+12,3,62,col,1)+circle(785,y+29,5,col)+text(803,y+36,title,20,'#e8eaf0',600)+text(780,y+64,sub,15,'#9cabbc')
s += text(760,582,'VERİ  /  MODEL  /  PLANLAMA',14,'#b7a4ce',mono=True)
save('disaster',s,'#e9e3d9','#c5a984')

# Redis: README-backed command examples, not a fabricated execution capture.
s=window('MiniRedis / TCP :6379', '#e69588','#141b24')
s+=text(87,177,'KOMUT ÖRNEKLERİ',13,'#a59ab1',600,True)+line(730,155,730,600,'#33404c')
commands=[('> SET ad Hasan','#d7dee8'),('> GET ad','#d7dee8'),('Hasan','#a3d9ad'),('> SETEX mesaj 15 selam','#d7dee8'),('> TTL mesaj','#d7dee8'),('> INCR ziyaretci_sayisi','#d7dee8'),('> INFO','#d7dee8')]
for i,(cmd,c) in enumerate(commands):
    s+=text(89,227+i*49,cmd,23,c,mono=True)
s+=text(768,180,'İŞLEM AKIŞI',13,'#a59ab1',600,True)
for i,(head,sub) in enumerate([('TCP bağlantısı','ServerSocket'),('Komut yönlendirme','CommandFactory'),('Bellek içi depolama','ConcurrentHashMap')]):
    y=205+i*108
    s+=rect(766,y,342,80,'#202b38',10,'#3a4858')+text(785,y+31,head,19,'#edf0f4',600)+text(785,y+57,sub,15,'#92a7bf',mono=True)
    if i<2:s+=line(935,y+80,935,y+105,'#e69588',2)
s+=pill(767,548,'TTL','#dec698','#393428',100)+pill(880,548,'AOF','#e6b4af','#402e32',100)+text(87,606,'Core Java · Thread pool · Kalıcılık',16,'#9ba9b8',mono=True)
save('redis',s,'#e5dfe7','#c7a0ab')


def person(x,y,scale=1,color='#8c9aa4'):
    return f'<g transform="translate({x} {y}) scale({scale})">'+circle(0,0,15,color)+path('M-19 25 Q0 12 19 25 L25 85 L13 85 L8 142 L-3 142 L-8 85 L-15 142 L-27 142 L-23 78 L-30 78 Z',color,'none')+'</g>'


# IoT / vision: explicitly schematic interior, no face or unsupported identity claim.
s=window('Görüntü analizi / kapalı alan', '#7ebfb5')
s+=rect(80,155,720,450,'#24313a',10)
s+=path('M80 155 L365 295 L570 295 L800 155','#3a4850','none')+path('M80 605 L365 295 L570 295 L800 605','#414c4e','none')
for x in [120,260,400,540,680,800]:s+=line(465,295,x,605,'#61706c',1)
for y in [360,440,540]:s+=line(80,y,800,y,'#5c6866',1)
s+=path('M135 190 L250 245 L250 430 L135 480 Z','#1a252e','#5f7076')+path('M650 250 L744 190 L744 480 L650 432 Z','#1a252e','#5f7076')
s+=person(438,335,1.15)+rect(383,300,112,230,'none',3,'#a1d5bd',extra='stroke-width="2"')+pill(383,270,'KİŞİ','#b6e4cb','#294a42',112)
s+=text(833,187,'Algılama zinciri',21,'#eff2ee',600)
for i,(a,b) in enumerate([('01','Görüntü alımı'),('02','Model çıkarımı'),('03','Olay incelemesi'),('04','IoT entegrasyonu')]):
    y=247+i*90
    s+=circle(854,y-5,20,'#2c4647')+text(843,y+1,a,13,'#9bcebf',mono=True)+text(889,y+2,b,17,'#c9d5d7')
    if i<3:s+=line(854,y+16,854,y+62,'#435b5c')
save('indoor-vision',s,'#dee6e4','#91b6ac')

# Vertebra study: abstract annotation diagram, not invented radiographic evidence.
s=window('Vertebra / anahtar nokta anotasyonu', '#82c0db')
s+=rect(82,155,670,450,'#101c29',10)
for x in range(100,750,40):s+=line(x,165,x,595,'#1c2a38')
for y in range(175,600,40):s+=line(90,y,743,y,'#1c2a38')
s+=path('M400 174 C375 290 442 405 418 590',stroke='#8995a4',width=10)
for i in range(5):
    x=392+int(math.sin(i*.9)*18); y=180+i*78
    s+=path(f'M{x-58} {y} Q{x} {y-14} {x+58} {y} L{x+65} {y+42} Q{x} {y+67} {x-65} {y+42} Z','#727f8e','#9aa5b3',2)
    s+=path(f'M{x-65} {y+18} L{x-105} {y+12} L{x-76} {y+40} M{x+65} {y+18} L{x+105} {y+12} L{x+76} {y+40}',stroke='#7e8d9c',width=9)
    if i>1:
        s+=rect(x-78,y-10,156,80,'none',6,'#83c3db',extra='stroke-width="2"')+text(x+95,y+31,f'L{i+1}',20,'#9ed9ef',600)
        for dx,dy in [(-58,0),(58,0),(-65,42),(65,42)]:s+=circle(x+dx,y+dy,4,'#ecbd81')
s+=text(790,194,'Anatomik bölgeler',22,'#dce6ef',600)
for i,label in enumerate(['L3 vertebra','L4 vertebra','L5 vertebra']):
    s+=rect(790,228+i*82,315,62,'#202d3e',10)+circle(814,259+i*82,6,'#85c7df')+text(836,266+i*82,label,21,'#d6e4ee')
s+=text(790,516,'Sınır kutusu',17,'#95cde1')+text(790,551,'Köşe / anahtar noktalar',17,'#e1bd8c')+text(790,587,'Anatomik şema',14,'#90a3b8')
save('vertebra',s,'#e0e7ed','#9fbbd2')

# Personnel detection: clearly drawn silhouettes and boxes in a scene.
s=window('Personel tespiti / anotasyon çalışması', '#a9c8a8')
s+=rect(80,155,1040,450,'#293939',10)+rect(80,155,1040,150,'#415254',10)
for x in range(120,1120,130):s+=rect(x,182,85,120,'#26383c',3,'#6f8585')
s+=path('M80 605 L400 305 L830 305 L1120 605','#53605a','none')
for x in [90,300,570,830,1100]:s+=line(610,305,x,605,'#718075')
for y in [375,465,570]:s+=line(80,y,1120,y,'#6c7d73')
for x,y,z,label in [(345,340,1.25,'KİŞİ 01'),(655,320,1.0,'KİŞİ 02'),(890,362,1.2,'KİŞİ 03')]:
    s+=person(x,y,z,'#a8b1a5')+rect(x-52,y-30,103,190*z,'none',4,'#b5d2a8',extra='stroke-width="2"')+pill(x-52,y-64,label,'#d1e2c7','#3d5b46',103)
s+=pill(102,175,'ETİKETLEME GÖRÜNÜMÜ','#d4e2d8','#263d39',240)
save('personnel',s,'#e4e7de','#afbda3')

# Content production: editorial draft and composition preview.
s=window('İçerik stüdyosu / fikirden yayına', '#dca89c','#f4f0ea')
s+=rect(80,155,300,450,'#e6dfd7',12)+text(106,199,'İçerik akışı',24,'#493e48',600)
for i,(num,label) in enumerate([('01','Konu ve brief'),('02','Metin taslağı'),('03','Görsel düzen'),('04','Yayın hazırlığı')]):
    y=240+i*82
    s+=rect(102,y,255,61,'#faf7f2' if i==2 else '#eee8e1',9)+text(119,y+37,num,15,'#a07978',mono=True)+text(154,y+37,label,18,'#5f5058',600)
s+=rect(408,155,365,450,'#fffdfa',12,'#dfd5cc')+text(436,194,'Görsel kompozisyon',17,'#685560',600)
s+=rect(433,219,315,258,'#c6b6b4',8)+circle(661,300,71,'#f0e6d4')+path('M433 408 Q520 303 611 415 Q675 341 748 370 L748 477 L433 477 Z','#7d8780','none')+path('M433 449 Q545 373 658 453 L748 423 L748 477 L433 477 Z','#525f57','none')
s+=text(454,261,'BİR FİKİR,',22,'#faf6ec',600)+text(454,288,'YENİ BİR HİKÂYE.',22,'#faf6ec',600)
s+=text(436,514,'Başlık + görsel + anlatı',20,'#594951',600)
for i,w in enumerate([275,245,180]):s+=rect(436,536+i*16,w,5,'#ded4cc',2)
s+=text(812,195,'Metin taslağı',22,'#534552',600)+pill(810,215,'TASLAK','#967064','#eadbd1',120)
for i,w in enumerate([260,245,270,215,250,170]):s+=rect(812,285+i*24,w,7,'#d5c9c2',3)
s+=rect(812,474,275,93,'#e6dfd6',10)+text(833,509,'Son kontrol',19,'#5b4c55',600)+text(833,539,'Düzenle → gözden geçir',16,'#8b747c')
save('content-studio',s,'#e8ddd5','#cea49c')

# Report review: document plus linked editorial notes, no imaginary scores.
s=window('Rapor değerlendirme / belge incelemesi','#a99bdd','#ebe8ef')
s+=rect(118,160,539,444,'#c7c1d1',8,extra='transform="rotate(-2 380 380)"')+rect(132,155,539,444,'#fffdfa',8,'#d7d0de')
s+=text(171,206,'ARAŞTIRMA RAPORU',14,'#9b8fa7',600)+text(171,250,'Yöntem ve bulgular',30,'#3d3548',600)
for i,w in enumerate([430,407,420,375]):s+=rect(171,278+i*21,w,6,'#d9d3dc',3)
s+=rect(166,374,443,51,'#eee7fa',4)+text(176,397,'Yöntemin kapsamı ve sınırları',18,'#6a538a')+text(176,420,'açık biçimde tanımlanmalıdır.',18,'#6a538a')
for i,w in enumerate([425,392,418,358,400]):s+=rect(171,451+i*21,w,6,'#d9d3dc',3)
s+=path('M610 398 C700 398 675 317 737 317',stroke='#ae92d0',width=2)
for i,(title,desc,col) in enumerate([('Güçlü yönler','Yapı ve anlatım bütünlüğü','#659385'),('Geliştirilecek alanlar','Yöntemi ayrıntılandırma','#ad815e'),('Öneriler','Kaynak ve bulgu bağlantısı','#8c73af')]):
    y=172+i*142
    s+=rect(738,y,346,122,'#fcfafc',12,'#d5cddd')+circle(764,y+29,5,col)+text(782,y+36,title,21,'#51465d',600)+text(760,y+70,desc,17,'#8a7c94')+rect(760,y+90,278,5,'#e9e1ed',2)
save('report-review',s,'#e6e0ee','#bcabd1')

# Mobile board games: recognizable Mangala pits and a 9×9 Quoridor board.
s=rect(102,82,460,558,'#000',32,extra='opacity=".10" transform="translate(0 15)"')+rect(102,82,460,558,'#2b303b',32,'#5d6170')+rect(120,102,424,518,'#e5d4b7',20)
s+=text(148,155,'MANGALA',23,'#544430',600)+text(148,184,'Strateji · Taşlar · Hamleler',14,'#927b5d')
s+=rect(143,227,379,265,'url(#wood)',22,'#ab8250')+rect(158,251,39,213,'#997343',18)+rect(468,251,39,213,'#997343',18)
for row in range(2):
    for col in range(6):
        x,y=224+col*42,285+row*136
        s+=f'<ellipse cx="{x}" cy="{y}" rx="17" ry="37" fill="#987348" stroke="#e0bf89"/>'
        for j in range(3):s+=circle(x+(j%2)*7-3,y-14+j*13,6,'#efe4cc',extra='stroke="#c7af83"')
s+=pill(220,534,'MANGALA TAHTASI','#71583b','#f4e7cd',208)
s+=rect(628,82,460,558,'#000',32,extra='opacity=".10" transform="translate(0 15)"')+rect(628,82,460,558,'#2b303b',32,'#5d6170')+rect(646,102,424,518,'#ede7dc',20)
s+=text(677,155,'QUORIDOR',23,'#514631',600)+text(677,184,'Yolunu bul. Rakibinin yolunu değiştir.',14,'#927e62')
s+=rect(694,208,328,328,'#b49569',8)
for row in range(9):
    for col in range(9):s+=rect(705+col*35,219+row*35,27,27,'#e5cfaa',2,'#c4a373')
for x,y,w,h in [(771,254,6,62),(841,359,62,6),(911,429,6,62),(736,464,62,6)]:s+=rect(x,y,w,h,'#694a32',2)
s+=circle(858,303,11,'#61527d','stroke="#e4dcf2" stroke-width="3"')+circle(858,478,11,'#e6ded1','stroke="#7c674c" stroke-width="3"')
s+=pill(754,554,'9 × 9 OYUN TAHTASI','#71583b','#e0d3bd',218)
save('board-games',s,'#e6dfd3','#b9a67e')

print('Built 8 project-specific SVG covers.')
