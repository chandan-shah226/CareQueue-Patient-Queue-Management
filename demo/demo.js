/* ═══════════════════════════════════════════════════════════════
   CareQueue Demo Engine v4 — Ahmedabad + Specializations + Maps
   ═══════════════════════════════════════════════════════════════ */

const SCENES = [
  { id:'intro',    dur:13000,
    voice:"CareQueue is a smart digital queue management system designed to improve patient experience and reduce physical waiting time in clinics across your city.",
    sub:"CareQueue is a smart digital queue management system designed to improve patient experience and reduce physical waiting time in clinics across your city." },
  { id:'problem',  dur:10000,
    voice:"Traditional clinic queues force patients to wait for unpredictable durations without any visibility into queue progress.",
    sub:"Traditional clinic queues force patients to wait for unpredictable durations without any visibility into queue progress." },
  { id:'login',    dur:10000,
    voice:"Patients can securely access the system using a simple mobile-based login process with a four digit PIN.",
    sub:"Patients can securely access the system using a simple mobile-based login process with a 4-digit PIN." },
  { id:'clinics',  dur:12000,
    voice:"Patients can easily browse specialized doctors across your city, compare clinics by expertise, and navigate directly using integrated Google Maps support.",
    sub:"Patients can browse specialized doctors across your city, compare clinics by expertise, and navigate directly via Google Maps." },
  { id:'token',    dur:10000,
    voice:"Once a patient joins the queue, the system instantly generates a digital token and tracks their live position.",
    sub:"Once a patient joins the queue, the system instantly generates a digital token and tracks their live position." },
  { id:'sync',     dur:17000,
    voice:"When the doctor updates the queue, all connected patient interfaces receive updated queue information instantly. This is the core real-time synchronization feature of CareQueue.",
    sub:"When the doctor updates the queue, all connected patient interfaces receive updated queue information instantly." },
  { id:'opd',      dur:11000,
    voice:"Doctors can dynamically control O P D availability while patients receive live status updates on their devices.",
    sub:"Doctors can dynamically control OPD availability while patients receive live status updates." },
  { id:'tech',     dur:10000,
    voice:"The system uses Flask APIs, SQLite database management, and real-time frontend updates for lightweight and efficient operation.",
    sub:"The system uses Flask APIs, SQLite database management, and real-time frontend updates for lightweight and efficient operation." },
  { id:'complete', dur:10000,
    voice:"After consultation, the queue progresses automatically while patients receive confirmation updates.",
    sub:"After consultation, the queue progresses automatically while patients receive confirmation updates." },
  { id:'outro',    dur:10000,
    voice:"CareQueue can simply work throughout your city, making healthcare access easier for every patient and every doctor.",
    sub:"CareQueue can simply work throughout your city, making healthcare access easier for every patient and every doctor." }
];

let cur=-1, timer=null, playing=false;
const $=id=>document.getElementById(id);
const bar=$('progressBar'),counter=$('sceneCounter');
const subbar=$('subtitleBar'),overlay=$('playOverlay');

/* ═══ AUDIO ENGINE ═══ */
let audioCtx=null, bgGain=null;
function initAudio(){
  audioCtx=new(window.AudioContext||window.webkitAudioContext)();
  bgGain=audioCtx.createGain(); bgGain.gain.value=0; bgGain.connect(audioCtx.destination);
  const o1=audioCtx.createOscillator(); o1.type='sine'; o1.frequency.value=174; o1.connect(bgGain); o1.start();
  const o2=audioCtx.createOscillator(); o2.type='sine'; o2.frequency.value=261;
  const g2=audioCtx.createGain(); g2.gain.value=0.4; o2.connect(g2); g2.connect(bgGain); o2.start();
  bgGain.gain.linearRampToValueAtTime(0.06,audioCtx.currentTime+2);
}
function playClick(){if(!audioCtx)return;const o=audioCtx.createOscillator(),g=audioCtx.createGain();o.type='sine';o.frequency.value=1200;g.gain.value=0.08;g.gain.exponentialRampToValueAtTime(0.001,audioCtx.currentTime+0.12);o.connect(g);g.connect(audioCtx.destination);o.start();o.stop(audioCtx.currentTime+0.12)}
function playTransition(){if(!audioCtx)return;const o=audioCtx.createOscillator(),g=audioCtx.createGain();o.type='sine';o.frequency.value=600;o.frequency.linearRampToValueAtTime(900,audioCtx.currentTime+0.25);g.gain.value=0.05;g.gain.exponentialRampToValueAtTime(0.001,audioCtx.currentTime+0.3);o.connect(g);g.connect(audioCtx.destination);o.start();o.stop(audioCtx.currentTime+0.3)}

/* ═══ VOICEOVER ═══ */
let chosenVoice=null;
function pickVoice(){
  const v=speechSynthesis.getVoices();
  const p=['Google UK English Male','Google US English','Google UK English Female','Microsoft Mark','Microsoft David','Microsoft Zira','Daniel','Samantha'];
  for(const n of p){const f=v.find(x=>x.name.includes(n));if(f){chosenVoice=f;return;}}
  chosenVoice=v.find(x=>x.lang.startsWith('en'))||v[0]||null;
}
if(speechSynthesis.onvoiceschanged!==undefined) speechSynthesis.onvoiceschanged=pickVoice;
pickVoice();
function speak(text){
  speechSynthesis.cancel();if(!text)return;
  const u=new SpeechSynthesisUtterance(text);
  if(chosenVoice)u.voice=chosenVoice; u.rate=0.92; u.pitch=1.0; u.volume=1.0;
  if(bgGain&&audioCtx)bgGain.gain.linearRampToValueAtTime(0.025,audioCtx.currentTime+0.3);
  u.onend=()=>{if(bgGain&&audioCtx)bgGain.gain.linearRampToValueAtTime(0.06,audioCtx.currentTime+0.5);};
  speechSynthesis.speak(u);
}

/* ═══ SCENE ENGINE ═══ */
function start(){overlay.classList.add('hidden');playing=true;initAudio();pickVoice();next();}
overlay.addEventListener('click',start);
function next(){
  if(!playing)return; cur++;
  if(cur>=SCENES.length){cur=SCENES.length-1;if(bgGain&&audioCtx)bgGain.gain.linearRampToValueAtTime(0,audioCtx.currentTime+3);return;}
  document.querySelectorAll('.scene').forEach(s=>s.classList.remove('active'));
  const sc=SCENES[cur],el=$('scene-'+sc.id);
  if(el)el.classList.add('active');
  bar.style.width=((cur+1)/SCENES.length*100)+'%';
  counter.textContent=(cur+1)+' / '+SCENES.length;
  if(sc.sub){subbar.textContent=sc.sub;subbar.classList.add('visible');}else subbar.classList.remove('visible');
  playTransition();
  setTimeout(()=>speak(sc.voice),600);
  anim(sc.id);
  clearTimeout(timer); timer=setTimeout(next,sc.dur);
}
document.addEventListener('keydown',e=>{if(e.key===' '||e.key==='Enter'){e.preventDefault();if(!playing)start();else next();}});

/* ═══ ANIMATIONS ═══ */
function anim(id){
  switch(id){
    case 'login':animLogin();break;case 'clinics':animClinics();break;
    case 'token':animToken();break;case 'sync':animSync();break;
    case 'opd':animOPD();break;case 'complete':animComplete();break;
  }
}
function animLogin(){
  const ph=$('mockPhone'),btn=$('loginBtn');
  const pins=[$('pin1'),$('pin2'),$('pin3'),$('pin4')];
  if(!ph)return; ph.value='';ph.classList.remove('typing');
  pins.forEach(p=>{if(p)p.value='';});
  if(btn){btn.textContent='Login';btn.classList.remove('success-state');}
  const d='9876543210';let i=0;
  setTimeout(()=>{ph.classList.add('typing');
    const iv=setInterval(()=>{if(i<d.length){ph.value+=d[i];i++;playClick();}
    else{clearInterval(iv);ph.classList.remove('typing');
      pins.forEach((p,x)=>{setTimeout(()=>{if(p){p.value='●';playClick();}},300+x*200);});
      setTimeout(()=>{if(btn){btn.textContent='✓ Login Successful';btn.classList.add('success-state');}playTransition();},1500);
    }},150);
  },1000);
}
function animClinics(){
  const cards=document.querySelectorAll('.clinic-card-light');
  const map=$('mapPreview');
  cards.forEach(c=>c.classList.remove('selected'));
  if(map)map.classList.remove('show');
  let i=0;
  const iv=setInterval(()=>{
    cards.forEach(c=>c.classList.remove('selected'));
    if(map)map.classList.remove('show');
    if(i<cards.length){cards[i].classList.add('selected');playClick();i++;}
    else if(i===cards.length){
      // Show map preview
      if(map){map.classList.add('show');playTransition();}
      i++;
    }else clearInterval(iv);
  },2200);
}
function animToken(){
  const el=$('tokenNum');if(!el)return;el.textContent='—';
  setTimeout(()=>{let n=0;const iv=setInterval(()=>{n+=Math.ceil(Math.random()*2);if(n>=7){n=7;clearInterval(iv);playTransition();}el.textContent='#'+String(n).padStart(3,'0');},140);},1200);
}
function animSync(){
  const dRows=document.querySelectorAll('#syncScene .dq-row');
  const pS=$('pServing'),pA=$('pAhead'),pW=$('pWait'),fl=$('phoneFlash');
  dRows.forEach(r=>{r.classList.remove('served');const b=r.querySelector('.dq-badge');if(b&&r.dataset.orig){b.textContent=r.dataset.orig;b.className='dq-badge '+r.dataset.origcls;}});
  let sv=3,ah=4,wt=20;
  if(pS)pS.textContent='#003';if(pA)pA.textContent='4';if(pW)pW.textContent='~20 min';
  let step=0;
  const iv=setInterval(()=>{step++;if(step>3){clearInterval(iv);return;}
    const row=dRows[step-1];
    if(row){row.classList.add('served');const b=row.querySelector('.dq-badge');if(b){b.textContent='Done';b.className='dq-badge dq-done';}}
    if(dRows[step]){const nb=dRows[step].querySelector('.dq-badge');if(nb){nb.textContent='Serving';nb.className='dq-badge dq-serving';}}
    sv++;ah=Math.max(0,ah-1);wt=Math.max(0,wt-5);
    if(pS)pS.textContent='#00'+sv;if(pA)pA.textContent=String(ah);
    if(pW)pW.textContent=ah===0?'🟢 Almost now!':'~'+wt+' min';
    if(fl){fl.classList.add('active');setTimeout(()=>fl.classList.remove('active'),400);}
    playClick();
  },3500);
}
function animOPD(){
  const badge=$('opdBadge'),patB=$('patOpdBadge'),patM=$('patOpdMsg');
  if(!badge)return;
  const st=[
    {t:'Open',c:'ui-badge open',pt:'Open',pc:'ui-badge open',m:''},
    {t:'Break',c:'ui-badge brk',pt:'Break',pc:'ui-badge brk',m:'⏸ Clinic is on break'},
    {t:'Closed',c:'ui-badge closed',pt:'Closed',pc:'ui-badge closed',m:'Clinic is currently closed'},
    {t:'Open',c:'ui-badge open',pt:'Open',pc:'ui-badge open',m:''}
  ];
  let i=0;badge.textContent=st[0].t;badge.className=st[0].c;
  if(patB){patB.textContent=st[0].pt;patB.className=st[0].pc;}if(patM)patM.textContent='';
  const iv=setInterval(()=>{i++;if(i>=st.length){clearInterval(iv);return;}
    const s=st[i];badge.textContent=s.t;badge.className=s.c;
    if(patB){patB.textContent=s.pt;patB.className=s.pc;}if(patM)patM.textContent=s.m;playClick();
  },2800);
}
function animComplete(){
  const p=$('completionMock');if(!p)return;p.style.display='none';
  setTimeout(()=>{p.style.display='flex';playTransition();},2000);
}
