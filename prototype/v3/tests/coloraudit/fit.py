import json,subprocess,sys
from coloraide import Color
sys.stdout.reconfigure(encoding='utf-8')
def apca(f,b):
    js="const {APCAcontrast,sRGBtoY}=require('apca-w3');const {colorParsley}=require('colorparsley');const p=JSON.parse(require('fs').readFileSync(0,'utf8'));console.log(JSON.stringify(p.map(([f,b])=>Number(APCAcontrast(sRGBtoY(colorParsley(f)),sRGBtoY(colorParsley(b)))))))"
    return json.loads(subprocess.run(['node','-e',js],input=json.dumps([[f,b]]),capture_output=True,text=True).stdout)[0]
def fit(name, seed, H, C, targets, direction):
    # targets: list of (bg, minLc, minWcag); идём по L от исходной в сторону direction, пока все пороги не пройдены
    L=Color(seed).convert('oklch')['lightness']
    for i in range(400):
        c=Color('oklch',[L,C,H]).fit('srgb'); h=c.to_string(hex=True).upper()
        res=[(bg,abs(apca(h,bg)),Color(h).contrast(bg,method='wcag21')) for bg,_,_ in targets]
        if all(lc>=t and w>=tw for (bg,lc,w),(_,t,tw) in zip(res,targets)):
            print(f"{name}: {seed} → {h}  (OKLCH L{L:.3f} C{C} H{H})  " + " · ".join(f"на {bg}: Lc {lc:.1f}, WCAG {w:.2f}" for bg,lc,w in res)); return h
        L+=0.002*direction
    print(name,'не найдено')
# тёмная тема: фоны bg #121415, card #1D2022, film #2A2E31, soft #1F2A2E
H=232; C=0.006
fit('dark ink2 (вторичный текст, предложения)','#A8ABA9',H,C,[('#121415',75,4.5),('#1D2022',72,4.5),('#2A2E31',60,4.5),('#1F2A2E',60,4.5)],+1)
fit('dark ai (ответ GigaChat, курсив)','#9A9D9B',H,C,[('#121415',75,4.5),('#1D2022',72,4.5),('#2A2E31',60,4.5)],+1)
fit('dark line (разделитель, декор)','#33383B',234,0.009,[('#1D2022',15,1.0)],+1)
# светлая: bg #F3F3F1, card #FFFFFF, film #E4E4E0, soft #E9EEF0
fit('light ai (ответ GigaChat, курсив)','#6A6A66',107,0.006,[('#F3F3F1',75,4.5),('#FFFFFF',75,4.5),('#E4E4E0',60,4.5)],-1)
fit('light ink2 (вторичный, на плашках тоже)','#5E5E5A',107,0.006,[('#F3F3F1',75,4.5),('#E9EEF0',72,4.5),('#E4E4E0',62,4.5)],-1)
