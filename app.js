(function(){
var d=document.documentElement,$=function(i){return document.getElementById(i)},$$=function(s,r){return[].slice.call((r||document).querySelectorAll(s))};
var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
d.classList.add('js');

/* Theme */
var tt=$('theme');
if(tt){tt.setAttribute('aria-pressed',d.dataset.theme==='light');
tt.addEventListener('click',function(){var n=d.dataset.theme==='light'?'dark':'light';d.dataset.theme=n;try{localStorage.setItem('t',n)}catch(e){}tt.setAttribute('aria-pressed',n==='light')})}

/* Header: hide on scroll down, show on scroll up */
var hd=document.querySelector('header.top'),ly=0,tick=false,menu=$('menu'),mb=$('mb');
function menuOpen(){return menu&&menu.classList.contains('open')}
addEventListener('scroll',function(){if(tick)return;tick=true;requestAnimationFrame(function(){var y=scrollY;
if(y>ly+8&&y>140&&!menuOpen())hd.classList.add('hide');else if(y<ly-8||y<90)hd.classList.remove('hide');ly=y;tick=false})},{passive:true});
hd.addEventListener('focusin',function(){hd.classList.remove('hide')});

/* Full-screen menu */
function setMenu(o){menu.classList.toggle('open',o);mb.setAttribute('aria-expanded',o);document.body.style.overflow=o?'hidden':'';
if(o){setTimeout(function(){var f=menu.querySelector('a');if(f)f.focus()},350)}else mb.focus()}
if(menu&&mb){mb.addEventListener('click',function(){setMenu(true)});$('mx').addEventListener('click',function(){setMenu(false)});
menu.addEventListener('keydown',function(e){if(e.key==='Escape')setMenu(false)});
$$('a',menu).forEach(function(a){a.addEventListener('click',function(){setMenu(false)})})}

/* Reveal on scroll */
var targets=$$('.rv,.gate,.motifbox,.mo,.pipe,.pcard');
if(!('IntersectionObserver' in window)||reduce){targets.forEach(function(t){t.classList.add('in')})}
else{var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}else if(e.target.classList.contains('gate')){e.target.classList.remove('in')}})},{threshold:.18});
targets.forEach(function(t){io.observe(t)})}

/* Rotating typed word */
var rot=document.querySelector('.rot');
if(rot&&!reduce){var words=rot.dataset.w.split('|'),wi=0,ci=rot.textContent.length,del=true,pause=0;
(function loop(){var w=words[wi],t=70;
if(del){ci--;t=38;if(ci<=0){del=false;wi=(wi+1)%words.length;w=words[wi];t=260}}
else{ci++;t=75;if(ci>=w.length){del=true;t=1900}}
rot.textContent=words[wi].slice(0,Math.max(ci,0));setTimeout(loop,t)})()}

/* Typed code panel */
var cp=$('code');
if(cp){var tabs=$$('.tabs button',cp),panes=$$('pre.cb',cp),car=document.createElement('i'),run=0,skip=$('skip'),typed=false;car.className='caret';
function textNodes(p){var w=document.createTreeWalker(p,NodeFilter.SHOW_TEXT),a=[],n;while(n=w.nextNode())a.push(n);return a}
function typeIn(p){var id=++run,nodes=textNodes(p),full=nodes.map(function(n){return n.nodeValue});
if(reduce){return}
nodes.forEach(function(n){n.nodeValue=''});var ni=0,ci=0;skip.hidden=false;
function done(){nodes.forEach(function(n,i){n.nodeValue=full[i]});car.remove();skip.hidden=true}
skip.onclick=function(){run++;done()};
(function step(){if(id!==run)return;
if(ni>=nodes.length){skip.hidden=true;setTimeout(function(){if(id===run)car.remove()},1800);return}
var n=nodes[ni],s=full[ni];n.parentNode.insertBefore(car,n.nextSibling);
var ch=s.charAt(ci);n.nodeValue=s.slice(0,++ci);
if(ci>=s.length){ni++;ci=0}
setTimeout(step,ch==='\n'?60:(ch===' '?4:6+Math.random()*7))})()}
function show(i,play){tabs.forEach(function(t,j){t.setAttribute('aria-selected',j===i)});panes.forEach(function(p,j){p.hidden=j!==i});$('cfile').textContent=tabs[i].dataset.file;
if(play)typeIn(panes[i]);else{run++;car.remove();skip.hidden=true}}
tabs.forEach(function(t,i){t.addEventListener('click',function(){show(i,true)})});
$('replay').addEventListener('click',function(){var i=tabs.findIndex(function(t){return t.getAttribute('aria-selected')==='true'});show(i,true)});
if(reduce||!('IntersectionObserver' in window)){}
else{new IntersectionObserver(function(es,o){if(es[0].isIntersecting&&!typed){typed=true;o.disconnect();typeIn(panes[0])}},{threshold:.35}).observe(cp)}}

/* Marquee pause */
var pz=$('pause');
if(pz){pz.addEventListener('click',function(){var on=document.body.classList.toggle('paused');pz.setAttribute('aria-pressed',on);pz.querySelector('.lbl').textContent=on?'Play motion':'Pause motion'})}

/* Magnetic buttons */
if(!reduce&&matchMedia('(hover:hover) and (pointer:fine)').matches){$$('.mag').forEach(function(b){
b.addEventListener('pointermove',function(e){var r=b.getBoundingClientRect();b.style.transform='translate('+((e.clientX-r.left-r.width/2)*.16).toFixed(1)+'px,'+((e.clientY-r.top-r.height/2)*.22).toFixed(1)+'px)'});
b.addEventListener('pointerleave',function(){b.style.transform=''})})}

/* Project filters */
var fb=$$('.filters button');
if(fb.length){var cnt=$('cnt'),items=$$('.plist li');
fb.forEach(function(b){b.addEventListener('click',function(){var f=b.dataset.f,n=0;fb.forEach(function(x){x.setAttribute('aria-pressed',x===b)});
items.forEach(function(li){var s=f==='all'||li.dataset.d===f;li.hidden=!s;if(s)n++});
cnt.textContent=n+(n===1?' project':' projects')})})}

/* Architecture stages */
$$('.st .hb').forEach(function(b){b.addEventListener('click',function(){b.setAttribute('aria-expanded',b.getAttribute('aria-expanded')==='true'?'false':'true')})});

/* Contact links are assembled here, not written in the HTML */
var m=['miracleagbebaku122','gmail.com'],w='2349021637905',x='MiracleTechX',ig='miracle001992',gh='Miraclebot15';
var map={mail:'mailto:'+m.join('@'),wa:'https://wa.me/'+w,x:'https://x.com/'+x,ig:'https://www.instagram.com/'+ig+'/',gh:'https://github.com/'+gh};
$$('[data-c]').forEach(function(l){l.href=map[l.dataset.c];if(l.dataset.c!=='mail'){l.target='_blank';l.rel='noopener noreferrer'}});
})();
