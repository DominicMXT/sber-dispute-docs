import Color from 'colorjs.io';
import {APCAcontrast, sRGBtoY} from 'apca-w3';
import {colorParsley} from 'colorparsley';
const lc=(f,b)=>Math.abs(APCAcontrast(sRGBtoY(colorParsley(f)),sRGBtoY(colorParsley(b))));
const acc=new Color('#9AC8D6'); const [L0,C0,H0]=new Color('#72B7CA').to('oklch').coords;
for(let L=0.74;L>=0.56;L-=0.02){ const c=new Color('oklch',[L,C0,H0]).toGamut({space:'srgb'}); const hx=c.to('srgb').toString({format:'hex'}).toUpperCase();
 console.log(hx, 'L',L.toFixed(2),'ΔE к accent',c.deltaE2000(acc).toFixed(1),'| на film WCAG',c.contrastWCAG21(new Color('#2A2E31')).toFixed(2),'Lc',lc(hx,'#2A2E31').toFixed(1),'| на card WCAG',c.contrastWCAG21(new Color('#1D2022')).toFixed(2)); }
