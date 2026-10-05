import Color from 'colorjs.io';
import {APCAcontrast, sRGBtoY} from 'apca-w3';
import {colorParsley} from 'colorparsley';
const lc=(f,b)=>Math.abs(APCAcontrast(sRGBtoY(colorParsley(f)),sRGBtoY(colorParsley(b))));
const wc=(f,b)=>new Color(f).contrastWCAG21(new Color(b));
function fit(name, seed, H, C, targets, dir){
  let L=new Color(seed).to('oklch').coords[0];
  for(let i=0;i<500;i++){
    const h=new Color('oklch',[L,C,H]).toGamut({space:'srgb'}).to('srgb').toString({format:'hex'}).toUpperCase();
    const hx=h.length===4?'#'+[...h.slice(1)].map(x=>x+x).join(''):h;
    const res=targets.map(([bg,t,tw])=>[bg,lc(hx,bg),wc(hx,bg),t,tw]);
    if(res.every(([,l,w,t,tw])=>l>=t&&w>=tw)){ console.log(`${name}: ${seed} → ${hx} (OKLCH L${L.toFixed(3)} C${C} H${H}) `+res.map(([bg,l,w])=>`на ${bg}: Lc ${l.toFixed(1)}, WCAG ${w.toFixed(2)}`).join(' · ')); return hx;}
    L+=0.002*dir;
  }
  console.log(name,'не найдено');
}
fit('dark ink2','#C8CDCF',232,0.006,[['#121415',75,4.5],['#1D2022',75,4.5],['#2A2E31',60,4.5],['#1F2A2E',60,4.5]],+1);
