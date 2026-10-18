(function(){
var E='cubic-bezier(.2,.8,.2,1)',reduce=matchMedia('(prefers-reduced-motion: reduce)').matches,$=function(i){return document.getElementById(i)};
var page=document.body.dataset.page;document.documentElement.classList.add('js');
document.querySelectorAll('nav a').forEach(function(a){if(a.dataset.p===(document.body.dataset.nav||page))a.setAttribute('aria-current','page')});
function letters(h,words){h.textContent='';var n=0;words.forEach(function(w){var s=document.createElement('span');s.className='ln';s.setAttribute('aria-hidden','true');w.split('').forEach(function(c){var l=document.createElement('span');l.className='l';l.style.setProperty('--i',n++);l.textContent=c;s.appendChild(l)});h.appendChild(s)})}
var U='<svg viewBox="0 0 14 14" aria-hidden="true"><circle cx="7" cy="7" r="5.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="1 3" stroke-linecap="round"/></svg>',
P='<svg viewBox="0 0 14 14" aria-hidden="true"><circle cx="7" cy="7" r="5.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="4 2.5"/></svg>',
H='<svg viewBox="0 0 14 14" aria-hidden="true"><circle cx="7" cy="7" r="5.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M7 1.5a5.5 5.5 0 0 1 0 11z" fill="currentColor"/></svg>',
V='<svg viewBox="0 0 14 14" aria-hidden="true"><circle cx="7" cy="7" r="6" fill="currentColor"/><path d="m3.5 7 2.2 2.2 4.8-5" fill="none" stroke="var(--bg,#fff)" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
D={live:'<svg viewBox="0 0 14 14" aria-hidden="true"><circle cx="7" cy="7" r="5.5" fill="currentColor"/></svg>Live',dev:'<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M2 7h10M8 3l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>In development',soon:'<svg viewBox="0 0 14 14" aria-hidden="true"><circle cx="7" cy="7" r="5.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M7 4v3l2 1" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>Coming soon'};
var DL={live:'Live',dev:'In development',soon:'Coming soon'};
if(page==='home'){
letters($('nm'),['Miracle','Agbebaku']);
var top=$('top'),bot=$('bot'),sc=$('sc'),T=[];
var claims=[["Separates planning from execution",1],["Production-ready",0],["WhatsApp assistant",1],["Fully autonomous",0],["Approval for sensitive actions",1],["Secure",0]];
function later(f,ms){T.push(setTimeout(f,ms))}
function tag(c,t){var e=document.createElement('em');e.textContent=t;c.appendChild(e)}
function setup(){T.forEach(clearTimeout);T=[];top.textContent='';bot.textContent='';top.style.minHeight='';top.style.padding='';
var ch=claims.map(function(c){var s=document.createElement('span');s.className='chip';s.innerHTML='<b>'+c[0]+'</b>';top.appendChild(s);return s});
top.style.minHeight=top.offsetHeight+'px';return ch}
function scan(s){var r=s.getBoundingClientRect(),w=sc.parentNode.getBoundingClientRect();sc.style.left=Math.max(0,r.left-w.left-20)+'px';sc.animate([{opacity:0},{opacity:1},{opacity:0}],{duration:520,easing:E})}
function collapse(){if(!top.querySelector('.chip:not([hidden])')){top.style.minHeight='0';top.style.padding='0'}}
function run(){var ch=setup();
if(reduce){ch.forEach(function(s,i){if(claims[i][1]){bot.appendChild(s);s.className='chip ok';tag(s,'Unverified')}else s.hidden=true});collapse();return}
ch.forEach(function(s,i){var t=900+i*620;
later(function(){s.classList.add('chk');scan(s)},t);
later(function(){s.classList.remove('chk');
if(claims[i][1]){var a=s.getBoundingClientRect();bot.appendChild(s);var b=s.getBoundingClientRect();s.className='chip ok';tag(s,'Unverified');s.animate([{transform:'translate('+(a.left-b.left)+'px,'+(a.top-b.top)+'px)'},{transform:'none'}],{duration:700,easing:E})}
else{s.className='chip no';tag(s,'No evidence supplied');s.animate([{transform:'translateX(0)'},{transform:'translateX(-6px)'},{transform:'translateX(6px)'},{transform:'translateX(-4px)'},{transform:'none'}],{duration:380});
later(function(){s.animate([{opacity:1},{opacity:0}],{duration:500,fill:'forwards'});later(function(){s.hidden=true;collapse()},520)},1100)}},t+420)})}
$('rp').addEventListener('click',function(){letters($('nm'),['Miracle','Agbebaku']);run()});
run();
}
if(page==='projects'){
var ul=$('ix'),cnt=$('cnt'),f='all';
PROJECTS.forEach(function(p,i){var li=document.createElement('li');li.className='pr'+(p.e==='p'?' pl':p.e==='h'?' pt':'');li.dataset.d=p.d;
li.innerHTML='<button class="row" aria-expanded="false" aria-controls="d'+i+'"><span class="nm"'+(p.cs?' style="view-transition-name:p-'+p.cs.replace('.html','')+'"':'')+'>'+p.n+'</span><span class="sts"><span>'+(p.n==='ELLA'?'<span data-ella-status aria-live="polite">Checking…</span>':D[p.d])+'</span><span>'+(p.e==='p'?P+'Planned':p.e==='h'?H+'Partial':p.e==='v'?V+'Verified':U+'Unverified')+'</span></span></button><div class="dt" id="d'+i+'"><div><p>'+p.t+'</p>'+(p.cs?'<a class="btn" href="'+p.cs+'">Read more</a>':'')+(p.url?'<a class="btn" href="'+p.url+'" target="_blank" rel="noopener noreferrer">Open deployment<span class="sr">(opens in a new tab)</span></a>':'')+'</div></div>';
li.querySelector('.row').addEventListener('click',function(e){var b=e.currentTarget;b.setAttribute('aria-expanded',b.getAttribute('aria-expanded')==='true'?'false':'true')});ul.appendChild(li)});
function apply(){var n=0;ul.querySelectorAll('li').forEach(function(li){var show=f==='all'||li.dataset.d===f;li.hidden=!show;if(show)n++});cnt.textContent=n+(n===1?' project':' projects')+(f==='all'?'':' · '+DL[f])}
document.querySelectorAll('.filters button').forEach(function(b){b.addEventListener('click',function(){f=b.dataset.f;document.querySelectorAll('.filters button').forEach(function(x){x.setAttribute('aria-pressed',x===b)});apply()})});
apply();
}
function refreshProjectStatus(name,selector,endpoint){
var nodes=document.querySelectorAll(selector);
if(!nodes.length)return;
function show(label,state){nodes.forEach(function(n){n.textContent=label;n.dataset.status=state;n.setAttribute('aria-label',name+' website status: '+label)})}
show('Checking…','checking');
fetch(endpoint,{cache:'no-store',headers:{Accept:'application/json'}}).then(function(r){if(!r.ok)throw new Error('Status endpoint unavailable');return r.json()}).then(function(s){if(s.status==='live')show('Live','live');else if(s.status==='down')show('Down','down');else show('Status unavailable','unknown')}).catch(function(){show('Status unavailable','unknown')});
}
refreshProjectStatus('ELLA','[data-ella-status],#ella-deployment-status','/api/ella-status');
refreshProjectStatus('NEXUS CORE','[data-nexus-status],#nexus-deployment-status','/api/nexus-status');
var m=['miracleagbebaku122','gmail.com'],w='2349021637905',x='MiracleTechX',ig='miracle001992',gh='Miraclebot15';
var map={mail:'mailto:'+m.join('@'),wa:'https://wa.me/'+w,x:'https://x.com/'+x,ig:'https://www.instagram.com/'+ig+'/',gh:'https://github.com/'+gh};
document.querySelectorAll('[data-c]').forEach(function(l){l.href=map[l.dataset.c];if(l.dataset.c!=='mail'){l.target='_blank';l.rel='noopener noreferrer'}});
document.querySelectorAll('.stg .row').forEach(function(b){b.addEventListener('click',function(){b.setAttribute('aria-expanded',b.getAttribute('aria-expanded')==='true'?'false':'true')})});
var et=$('evt');if(et)et.addEventListener('click',function(){var on=document.documentElement.classList.toggle('ev');et.setAttribute('aria-pressed',on)});
var pp=$('pipe');if(pp){if(reduce||!('IntersectionObserver' in window))pp.classList.add('in');else{new IntersectionObserver(function(es,o){es.forEach(function(e){if(e.isIntersecting){pp.classList.add('in');o.disconnect()}})},{threshold:.15}).observe(pp)}}
})();
