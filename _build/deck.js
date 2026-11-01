/* ===== navigation shell, reveals, multiple choice, glossary drawer ===== */
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const stage=$('#stage'), slides=$$('.slide');let cur=0;
function toast(t){const el=$('#toast');el.textContent=t;el.classList.add('show');clearTimeout(toast.t);toast.t=setTimeout(()=>el.classList.remove('show'),1600);}

/* ---------- click by click reveals: same data-n appears together ---------- */
function groups(s){const m=new Map();$$('.st',s).forEach(e=>{const n=+e.dataset.n||0;if(!m.has(n))m.set(n,[]);m.get(n).push(e);});return [...m.keys()].sort((a,b)=>a-b).map(k=>m.get(k));}
function pending(s){return groups(s).filter(g=>!g[0].classList.contains('show'));}
function shown(s){return groups(s).filter(g=>g[0].classList.contains('show'));}
function stepInfo(){const g=groups(slides[cur]),left=pending(slides[cur]).length;$('#stepn').textContent=g.length&&left?('נותרו '+left+' שלבים'):'';if(left===1)$('#stepn').textContent='נותר שלב אחד';}
function setAll(s,on){$$('.st',s).forEach(e=>e.classList.toggle('show',on));}

/* ---------- multiple choice checks ---------- */
$$('.mc').forEach(m=>{const a=+m.dataset.a;m.addEventListener('click',e=>{const o=e.target.closest('.o');if(!o||m.classList.contains('done'))return;const i=+o.dataset.i;m.classList.add('done');
 o.classList.add(i===a?'ok':'bad');if(i!==a)m.querySelectorAll('.o')[a].classList.add('ok');else toast('נכון');});});

/* ---------- glossary drawer ---------- */
const gk=Object.keys(G);const dr=$('#drawer');let dkey=null;
function openTerm(k){const g=G[k];if(!g)return;dkey=k;$('#dh').textContent=g.h;$('#den').textContent=g.en||'';$('#dex').innerHTML='<b>דוגמה: </b>'+g.ex;$('#dtr').innerHTML='<b>שימו לב: </b>'+g.tr;$('#drel').innerHTML='';setMode('p');dr.classList.add('open');closeOverlays(true);}
function setMode(m){$('#dp').innerHTML=m==='p'?G[dkey].p:G[dkey].f;$$('#drawer .tabs button').forEach(b=>b.classList.toggle('on',b.dataset.k===m));}
$$('#drawer .tabs button').forEach(b=>b.onclick=()=>setMode(b.dataset.k));$('#dx').onclick=()=>dr.classList.remove('open');
$('#gwrap').innerHTML=gk.map(k=>`<button class="gitem" data-t="${k}">${G[k].h}<div class="gen">${G[k].en}</div></button>`).join('');
$('#gpl').innerHTML=gk.map(k=>`<div class="gp"><b>${G[k].h}</b> (${G[k].en})<br>${G[k].p}<br>דוגמה: ${G[k].ex}</div>`).join('');

/* ---------- navigation ---------- */
function show(i,reveal){if(i<0||i>=slides.length)return;slides[cur].classList.remove('on');cur=i;slides[cur].classList.add('on');setAll(slides[cur],!!reveal);
 $('#cnt').textContent=(cur+1)+' / '+slides.length;$('#progi').style.width=((cur+1)/slides.length*100)+'%';
 try{history.replaceState(null,'','#'+slides[cur].id);}catch(e){}
 $$('.mcell').forEach((c,j)=>c.classList.toggle('cur',j===cur));stepInfo();}
function go(id){const i=slides.findIndex(s=>s.id===id);if(i>=0){closeOverlays();show(i);}}
function next(){const p=pending(slides[cur]);if(p.length){p[0].forEach(e=>e.classList.add('show'));stepInfo();return;}show(cur+1);}
function prev(){const s=shown(slides[cur]);if(s.length){s[s.length-1].forEach(e=>e.classList.remove('show'));stepInfo();return;}show(cur-1,true);}
$('#bNext').onclick=next;$('#bPrev').onclick=prev;
$('#prog').onclick=e=>{const r=e.currentTarget.getBoundingClientRect();const f=(r.right-e.clientX)/r.width;show(Math.min(slides.length-1,Math.floor(f*slides.length)));};
function closeOverlays(keepDrawer){$('#menu').classList.remove('open');$('#gloss').classList.remove('open');if(!keepDrawer)dr.classList.remove('open');}
$('#closex').onclick=()=>closeOverlays();
$('#bMenu').onclick=()=>{closeOverlays();$('#menu').classList.add('open');};
$('#bGloss').onclick=()=>{closeOverlays();$('#gloss').classList.add('open');};
$('#mgrid').innerHTML=slides.map((s,i)=>`<button class="mcell" data-go="${s.id}"><small>${i+1}</small>${s.dataset.title}</button>`).join('');
$('#bPrint').onclick=()=>{closeOverlays();setTimeout(()=>window.print(),150);};
$('#bFull').onclick=()=>{if(!document.fullscreenElement)document.documentElement.requestFullscreen&&document.documentElement.requestFullscreen();else document.exitFullscreen();};
const typing=e=>{const t=e.target;return t&&(t.tagName==='INPUT'||t.tagName==='SELECT'||t.tagName==='TEXTAREA');};
document.addEventListener('keydown',e=>{if(typing(e)){if(e.key==='Escape')e.target.blur();return;}
 if(e.key==='ArrowLeft'||e.key==='PageDown'||e.key===' '){if(e.target.tagName==='BUTTON'&&e.key===' ')return;e.preventDefault();next();}
 else if(e.key==='ArrowRight'||e.key==='PageUp'){e.preventDefault();prev();}
 else if(e.key==='Escape'){closeOverlays();}
 else if(e.key==='Home'){show(0);}else if(e.key==='End'){show(slides.length-1);}});
function fit(){const s=Math.min(innerWidth/1280,(innerHeight-44-14)/720);stage.style.setProperty('--sc',s);}
addEventListener('resize',fit);fit();
document.addEventListener('click',e=>{const t=e.target.closest('[data-t]');if(t&&G[t.dataset.t]){e.stopPropagation();openTerm(t.dataset.t);return;}
 const g=e.target.closest('[data-go]');if(g){go(g.dataset.go);return;}
 if(!e.target.closest('#drawer'))dr.classList.remove('open');
 /* a click on the empty part of a slide advances, as on a classroom board */
 if(e.target.closest('#stage')&&!e.target.closest('button,a,input,select,label,.mc,.calc,.term')&&!document.getSelection().toString())next();});

/* ---------- footers and boot ---------- */
slides.forEach((s,i)=>{if(s.id==='s-title'||s.id==='s-end'||s.classList.contains('pd'))return;const f=document.createElement('div');f.className='ft';f.innerHTML='<span>'+COURSE+' · שיעור 1</span><span><b>ד״ר שי צבאן</b> · <span class="n">'+(i+1)+'</span></span>';s.appendChild(f);});
(function(){const h=location.hash.slice(1);const hi=slides.findIndex(s=>s.id===h);show(hi>=0?hi:0);})();
window.__deck={show,next,prev,go,slides,groups,pending,setAll,openTerm,closeOverlays,cur:()=>cur};
