/* ===== interactive calculators: type inputs, read results live ===== */
(function(){
const money=x=>x.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
const fac=x=>x.toFixed(6);
const pct=x=>(Math.round(x*1e4)/1e4).toString();
const fr=(a,b)=>`<span class="frac"><span>${a}</span><span>${b}</span></span>`;
const pw=(b,e)=>`(${b})<sup>${String(e).replace('-','−')}</sup>`;
const eq=s=>`<div class="eq" dir="ltr">${s}</div>`;
const res=(l,v,sec)=>`<div class="res${sec?' sec':''}"><span>${l}</span><b${sec?'':' data-res'}>${v}</b></div>`;
const ln=s=>`<p class="ln">${s}</p>`;
const n=s=>`<span class="n">${s}</span>`;
const err=s=>`<div class="err">${s}</div>`;
const FVFA=(r,t)=>r===0?t:(Math.pow(1+r,t)-1)/r;
const PVFA=(r,t)=>r===0?t:(1-Math.pow(1+r,-t))/r;
function num(s){s=String(s).replace(/[,\s]/g,'');const m=/^(-?[\d.]+)\/([\d.]+)$/.exec(s);if(m){const b=parseFloat(m[2]);return b?parseFloat(m[1])/b:NaN;}return s===''?NaN:Number(s);}

/* small live timeline, same drawing rules as the static ones */
function TLJ(ticks,flows,moves,W=560,fs=17){const k=ticks.length,left=26,right=W-36,dx=(right-left)/Math.max(k-1,1),X={};ticks.forEach((l,i)=>{X[l]=left+i*dx;});
 const lab=Object.values(flows).some(Boolean),y0=lab?68:42;let p=`<line x1="6" y1="${y0}" x2="${W-12}" y2="${y0}" stroke="#1b2d55" stroke-width="2.6"/><polygon points="${W-4},${y0} ${W-17},${y0-6} ${W-17},${y0+6}" fill="#1b2d55"/>`;
 const txt=(x,y,t,o={})=>{const w=String(t).length*fs*.56;let a='middle';if(x-w/2<3){x=3;a='start';}else if(x+w/2>W-3){x=W-3;a='end';}const he=/[\u0590-\u05ff]/.test(t);if(he)a={start:'end',end:'start',middle:'middle'}[a];return `<text x="${x}" y="${y}" font-size="${o.fs||fs}" text-anchor="${a}" fill="${o.fill||'#16213a'}" font-weight="${o.w||600}"${he?' direction="rtl"':''}>${t}</text>`;};
 ticks.forEach(l=>{const x=X[l];if(String(l).startsWith('...')){p+=txt(x,y0+fs+6,'···',{fill:'#8a93aa',w:700});return;}p+=`<line x1="${x}" y1="${y0-6}" x2="${x}" y2="${y0+6}" stroke="#1b2d55" stroke-width="2.2"/>`+txt(x,y0+fs+6,String(l).replace('-','−'));});
 Object.entries(flows).forEach(([t,l])=>{if(!(t in X))return;const x=X[t],top=y0-36;p+=`<line x1="${x}" y1="${y0}" x2="${x}" y2="${top+8}" stroke="#ff6a4d" stroke-width="3"/><polygon points="${x},${top} ${x-5.5},${top+11} ${x+5.5},${top+11}" fill="#ff6a4d"/>`;if(l)p+=txt(x,top-6,l,{fill:'#b8391f',fs:fs-1,w:700});});
 let ym=y0+fs+24;moves.forEach(m=>{const a=X[m.a],b=X[m.b];const c=b>=a?'#0f9d90':'#6d4df2',s=b>=a?1:-1;
  if(a===b){p+=`<circle cx="${a}" cy="${ym}" r="5.5" fill="${c}"/>`;}else{p+=`<circle cx="${a}" cy="${ym}" r="4.5" fill="${c}"/><line x1="${a}" y1="${ym}" x2="${b-s*9}" y2="${ym}" stroke="${c}" stroke-width="2.6" stroke-dasharray="7 5"/><polygon points="${b},${ym} ${b-s*11},${ym-6} ${b-s*11},${ym+6}" fill="${c}"/>`;}
  if(m.t)p+=txt((a+b)/2,ym+fs+4,m.t,{fill:c,fs:fs-1,w:700});ym+=fs+24;});
 return `<div class="tlw"><svg class="tl" dir="ltr" viewBox="0 0 ${W} ${ym-6}">${p}</svg></div>`;}
/* ticks for a series between two times, with optional extra points */
function ticksFor(first,last,extra){const set=new Set(extra.concat([first,last]));if(last>first)set.add(first+1);const v=[...set].filter(x=>Number.isFinite(x)).sort((a,b)=>a-b);const out=[];v.forEach((x,i)=>{if(i&&x-v[i-1]>1)out.push('...'+i);out.push(x);});return out;}

const need=(v,keys)=>keys.every(k=>Number.isFinite(v[k]));
const BAD='הקלידו מספרים תקינים בכל השדות.';
const C={
fv(v){if(!need(v,['pv','r','t']))return err(BAD);const r=v.r/100,f=Math.pow(1+r,v.t),fv=v.pv*f,si=v.pv*(1+r*v.t);
 return eq(`FV = ${money(v.pv)} × ${pw((1+r).toFixed(4).replace(/0+$/,''),v.t)}`)+eq(`= ${money(v.pv)} × ${fac(f)}`)+res('ערך עתידי',money(fv))+res('בריבית פשוטה',money(si),1)+res('הריבית שנצברה על הריבית',money(fv-si),1);},
fvvar(v){if(!need(v,['pv','r1','t1','r2','t2']))return err(BAD);const a=Math.pow(1+v.r1/100,v.t1),b=Math.pow(1+v.r2/100,v.t2);
 return eq(`FV = ${money(v.pv)} × ${pw(1+v.r1/100,v.t1)} × ${pw(1+v.r2/100,v.t2)}`)+eq(`= ${money(v.pv)} × ${fac(a)} × ${fac(b)}`)+res('ערך עתידי',money(v.pv*a*b))+ln(`סך התקופות: ${n(v.t1+v.t2)}. בדקו שהוא מכסה את כל אורך העסקה.`);},
pvvar(v){if(!need(v,['fv','r1','t1','r2','t2']))return err(BAD);const a=Math.pow(1+v.r1/100,-v.t1),b=Math.pow(1+v.r2/100,-v.t2);
 return eq(`PV = ${money(v.fv)} × ${pw(1+v.r1/100,-v.t1)} × ${pw(1+v.r2/100,-v.t2)}`)+eq(`= ${money(v.fv)} × ${fac(a)} × ${fac(b)}`)+res('ערך נוכחי',money(v.fv*a*b))+ln('המבנה זהה לערך עתידי בריבית משתנה. רק סימן המעריך התהפך.');},
nper(v){if(!need(v,['pv','fv','r']))return err(BAD);const r=v.r/100;if(v.pv<=0||v.fv<=v.pv||r<=0)return err('הסכום בעתיד חייב להיות גדול מהסכום היום, והריבית חיובית.');const ratio=v.fv/v.pv;let k=0,f=1,cells='',guard=0;
 while(f<ratio-1e-6&&guard<400){k++;guard++;f*=1+r;if(k<=9||f>=ratio-1e-6)cells+=`<span class="${f>=ratio-1e-6?'hit':''}">(${(1+r).toFixed(3)})<sup>${k}</sup> = ${f.toFixed(4)}</span>`;}
 const exact=Math.abs(f-ratio)<5e-4;
 return eq(`(${(1+r).toFixed(3)})<sup>t</sup> = ${fr(money(v.fv),money(v.pv))} = ${ratio.toFixed(4)}`)+`<div class="cgrid">${cells}</div>`+res('מספר תקופות',exact?String(k):`בין ${k-1} ל-${k}`)+(exact?'':ln('המספרים אינם ״עגולים״. כלי כללי לחילוץ מספר תקופות יוצג בהמשך הקורס.'));},
pv(v){if(!need(v,['fv','r','t']))return err(BAD);const b=1+v.r/100,f=Math.pow(b,-v.t);
 return eq(`PV = ${fr(money(v.fv),pw(b,v.t))}`)+eq(`PV = ${money(v.fv)} × ${pw(b,-v.t)}`)+eq(`= ${money(v.fv)} × ${fac(f)}`)+res('ערך נוכחי',money(v.fv*f));},
cmp(v){if(!need(v,['a','b','t','r']))return err(BAD);const b=1+v.r/100,pv=v.b*Math.pow(b,-v.t),win=pv>v.a?'חלופה ב':pv<v.a?'חלופה א':'שתיהן שקולות';
 return eq(`PV = ${money(v.b)} × ${pw(b,-v.t)}`)+res('חלופה ב, בזמן 0',money(pv))+res('חלופה א, בזמן 0',money(v.a),1)+res('העדיפה',win,1);},
flows(v){if(!need(v,['T','r','a1','t1','a2','t2','a3','t3','a4','t4']))return err(BAD);const b=1+v.r/100;let fv=0,pv=0,terms=[],vals=[];[1,2,3,4].forEach(i=>{const a=v['a'+i],t=v['t'+i];if(!Number.isFinite(a)||!Number.isFinite(t)||a===0)return;const e=v.T-t,val=a*Math.pow(b,e);fv+=val;pv+=a*Math.pow(b,-t);terms.push(`${money(a)} × ${pw(b,e)}`);vals.push(money(val));});
 if(!terms.length)return err('הקלידו לפחות תזרים אחד.');
 return eq('FV = '+terms.slice(0,2).join(' + '))+(terms.length>2?eq('+ '+terms.slice(2).join(' + ')):'')+eq('= '+vals.join(' + '))+res('ערך בנקודת היעד',money(fv))+res('ערך נוכחי, בזמן 0',money(pv),1);},
fva(v){if(!need(v,['pmt','r','n','T']))return err(BAD);const r=v.r/100,beg=v.when==='beg',first=beg?0:1,last=first+v.n-1,e=v.T-last,F=FVFA(r,v.n),base=v.pmt*F,out=base*Math.pow(1+r,e);
 const ticks=ticksFor(first,last,[0,v.T]),fl={};[first,first+1,last].forEach(t=>fl[t]='');const mv=[{a:last,b:last,t:'הנוסחה: זמן '+last}];if(e)mv.push({a:last,b:v.T,t:'התאמה'});
 return TLJ(ticks,fl,mv)+eq(`FVFA(${pct(v.r)}%,${v.n}) = ${fr(pw(1+r,v.n)+' − 1',r)} = ${fac(F)}`)+eq(`FV = ${money(v.pmt)} × ${fac(F)}${e?' × '+pw(1+r,e):''}`)+res('סכום במועד הפירעון',money(out))+res(`בזמן ${n(last)}, לפני ההתאמה`,money(base),1);},
pmtfv(v){if(!need(v,['fv','r','n']))return err(BAD);const r=v.r/100,beg=v.when==='beg',F=FVFA(r,v.n),d=F*(beg?1+r:1);
 return eq(`x × FVFA(${pct(v.r)}%,${v.n})${beg?' × '+pw(1+r,1):''} = ${money(v.fv)}`)+eq(`FVFA = ${fac(F)}`)+eq(`x = ${fr(money(v.fv),fac(F)+(beg?' × '+(1+r):''))}`)+res('הפקדה תקופתית',money(v.fv/d))+res(beg?'לעומת תום תקופה':'לעומת תחילת תקופה',money(beg?v.fv/F:v.fv/(F*(1+r))),1);},
splitfv(v){if(!need(v,['p1','n1','r1','p2','n2','r2','T']))return err(BAD);const r1=v.r1/100,r2=v.r2/100,e=v.T-v.n1,e2=v.T-v.n1-v.n2;if(e2<0)return err('מועד הפירעון מוקדם מסוף הסדרה השנייה.');const a=v.p1*FVFA(r1,v.n1)*Math.pow(1+r2,e),b=v.p2*FVFA(r2,v.n2)*Math.pow(1+r2,e2);
 return eq(`${money(v.p1)} × FVFA(${pct(v.r1)}%,${v.n1}) × ${pw(1+r2,e)}`)+eq(`+ ${money(v.p2)} × FVFA(${pct(v.r2)}%,${v.n2})${e2?' × '+pw(1+r2,e2):''}`)+eq(`= ${money(a)} + ${money(b)}`)+res('סכום במועד הפירעון',money(a+b))+ln(`סדרה א עוצרת בזמן ${n(v.n1)}, וסדרה ב עוצרת בזמן ${n(v.n1+v.n2)}. כל סדרה מותאמת עד היעד, ורק אז מחברים.`);},
pva(v){if(!need(v,['pmt','r','n','f']))return err(BAD);const r=v.r/100,land=v.f-1,F=PVFA(r,v.n),base=v.pmt*F,e=-land,out=base*Math.pow(1+r,e);
 const last=v.f+v.n-1,ticks=ticksFor(v.f,last,[0,land]),fl={};[v.f,v.f+1,last].forEach(t=>fl[t]='');const mv=[{a:v.f,b:land,t:'הנוסחה: זמן '+String(land).replace('-','−')}];if(land!==0)mv.push({a:land,b:0,t:'התאמה'});
 return TLJ(ticks,fl,mv)+eq(`PVFA(${pct(v.r)}%,${v.n}) = ${fr('1 − '+pw(1+r,-v.n),r)} = ${fac(F)}`)+eq(`PV = ${money(v.pmt)} × ${fac(F)}${e?' × '+pw(1+r,e):''}`)+res('ערך נוכחי, בזמן 0',money(out))+res(`בזמן ${land<0?'מינוס '+(-land):land}, לפני ההתאמה`,money(base),1);},
loan(v){if(!need(v,['L','r','n']))return err(BAD);const r=v.r/100,beg=v.when==='beg',F=PVFA(r,v.n),d=F*(beg?1+r:1),x=v.L/d;
 return eq(`${money(v.L)} = x × PVFA(${pct(v.r)}%,${v.n})${beg?' × '+pw(1+r,1):''}`)+eq(`PVFA = ${fac(F)}`)+eq(`x = ${fr(money(v.L),fac(F)+(beg?' × '+(1+r):''))}`)+res('החזר תקופתי',money(x))+res('סך כל ההחזרים',money(x*v.n),1)+res('מתוכם ריבית',money(x*v.n-v.L),1);},
splitpv(v){if(!need(v,['p1','n1','p2','n2','r']))return err(BAD);const r=v.r/100,a=v.p1*PVFA(r,v.n1),b=v.p2*PVFA(r,v.n2)*Math.pow(1+r,-v.n1);
 return eq(`${money(v.p1)} × PVFA(${pct(v.r)}%,${v.n1})`)+eq(`+ ${money(v.p2)} × PVFA(${pct(v.r)}%,${v.n2}) × ${pw(1+r,-v.n1)}`)+eq(`= ${money(a)} + ${money(b)}`)+res('ערך נוכחי, בזמן 0',money(a+b))+ln(`סדרה ב מתחילה בזמן ${n(v.n1+1)}, והנוסחה מובילה לזמן ${n(v.n1)}. לכן מהוונים ${n(v.n1)} תקופות, ולא ${n(v.n1+1)}.`);},
perp(v){if(!need(v,['pmt','r','g','f']))return err(BAD);const r=v.r/100,g=v.g/100;if(r<=g)return err('הריבית חייבת להיות גדולה משיעור הצמיחה. אחרת השווי שואף לאינסוף, והנוסחה חסרת משמעות כלכלית.');const land=v.f-1,base=v.pmt/(r-g),out=base*Math.pow(1+r,-land),show=+land.toFixed(4);
 return eq(`PV = ${fr(money(v.pmt),g?r+' − '+g:r)} = ${money(base)}`)+ln(`הנוסחה מובילה תקופה אחת לפני התזרים הראשון, לזמן <span class="n">${show<0?'−'+(-show):show}</span>.`)+(land?eq(`PV<sub>0</sub> = ${money(base)} × ${pw(1+r,+(-land).toFixed(4))}`):'')+res('ערך נוכחי, בזמן 0',money(out))+(land?res('לפני ההתאמה',money(base),1):'');}
};
window.__calc=C;
$$('.calc').forEach(box=>{const id=box.dataset.calc,out=$('#out-'+id),ins=$$('[data-k]',box);
 const run=()=>{const v={};ins.forEach(i=>{v[i.dataset.k]=i.tagName==='SELECT'?i.value:num(i.value);});try{out.innerHTML=C[id](v);}catch(e){out.innerHTML=err(BAD);}};
 ins.forEach(i=>{i.addEventListener('input',run);i.addEventListener('change',run);});run();});
})();
