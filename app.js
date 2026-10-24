(function(){
var d=document.documentElement,$=function(i){return document.getElementById(i)},$$=function(s,r){return[].slice.call((r||document).querySelectorAll(s))};
var $$=function(q,r){return [].slice.call((r||document).querySelectorAll(q))};
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
var targets=$$('.rv,.gate,.motifbox,.mo,.pipe,.pcard,.ph,.rcard');
if(!('IntersectionObserver' in window)||reduce){targets.forEach(function(t){t.classList.add('in')})}
else{var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}else if(e.target.classList.contains('gate')){e.target.classList.remove('in')}})},{threshold:.18});
targets.forEach(function(t){io.observe(t)});setTimeout(function(){$$('.ph').forEach(function(p){p.classList.add('in')})},2600)}

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

/* Live website status: polls the same-origin /api/*-status functions */
var chks=$$('[data-check]');
if(chks.length){var eps={};chks.forEach(function(c){(eps[c.dataset.check]=eps[c.dataset.check]||[]).push(c)});
function paint(list,st,time){list.forEach(function(c){c.className='chip '+(st==='live'?'live':st==='down'?'down':st==='checking'?'checking':'unknown');
c.querySelector('.lbl').textContent={live:'Live',down:'Down',checking:'Checking…'}[st]||'Status unavailable';c.title=time?'Checked '+time:'';c.dataset.status=st})}
function poll(){Object.keys(eps).forEach(function(u){fetch(u,{cache:'no-store',headers:{Accept:'application/json'}}).then(function(r){if(!r.ok)throw new Error('x');return r.json()}).then(function(s){paint(eps[u],s.status,new Date(s.checkedAt||Date.now()).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}))}).catch(function(){paint(eps[u],'unknown')})})}
Object.keys(eps).forEach(function(u){paint(eps[u],'checking')});poll();
setInterval(function(){if(document.visibilityState==='visible')poll()},60000);
document.addEventListener('visibilitychange',function(){if(document.visibilityState==='visible')poll()})}



/* Scrollable regions must be reachable by keyboard */
['.terminal-code','.terminal-output'].forEach(function(s){var el=document.querySelector(s);if(el&&!el.hasAttribute('tabindex'))el.setAttribute('tabindex','0')});


/* Header solid state once the page scrolls */
(function(){var h=document.querySelector('header.top');if(!h)return;function f(){h.classList.toggle('solid',scrollY>16)}f();addEventListener('scroll',f,{passive:true})})();

/* Hero: pointer spotlight, photo tilt and gentle parallax (fine pointers only) */
(function(){var hero=document.querySelector('[data-hero]');if(!hero||reduce)return;
var fig=hero.querySelector('.hero2-photo'),tilt=fig&&fig.querySelector('.tilt'),fine=matchMedia('(hover:hover) and (pointer:fine)').matches,raf=0,px=0,py=0;
if(fine){hero.addEventListener('pointermove',function(e){px=e.clientX;py=e.clientY;if(raf)return;raf=requestAnimationFrame(function(){raf=0;var r=hero.getBoundingClientRect();hero.style.setProperty('--mx',((px-r.left)/r.width*100).toFixed(1)+'%');hero.style.setProperty('--my',((py-r.top)/r.height*100).toFixed(1)+'%');
if(tilt){var b=fig.getBoundingClientRect(),dx=(px-(b.left+b.width/2))/(innerWidth/2),dy=(py-(b.top+b.height/2))/(innerHeight/2);tilt.style.setProperty('--ry',(dx*6).toFixed(2)+'deg');tilt.style.setProperty('--rx',(-dy*5).toFixed(2)+'deg')}})});
hero.addEventListener('pointerleave',function(){if(tilt){tilt.style.setProperty('--rx','0deg');tilt.style.setProperty('--ry','0deg')}})}
if(fig){var t=0;addEventListener('scroll',function(){if(t)return;t=requestAnimationFrame(function(){t=0;var y=scrollY;if(y<innerHeight*1.2)fig.style.transform='translateY('+(y*.07).toFixed(1)+'px)'})},{passive:true})}})();

/* Approach: scroll-driven story (pinned on large screens, static elsewhere) */
(function(){var story=document.querySelector('[data-story]');if(!story)return;
var steps=[].slice.call(story.querySelectorAll('.step')),flow=story.querySelector('.flow'),mq=matchMedia('(min-width:901px)'),raf=0;
function ty(p){return p<.33?128*(p/.33):p<.66?128:128+152*((p-.66)/.34)}
function paint(p,s){steps.forEach(function(el,i){el.classList.toggle('on',i===s)});flow.dataset.s=s;flow.style.setProperty('--ty',ty(p).toFixed(1)+'px')}
function update(){raf=0;if(!mq.matches||reduce){steps.forEach(function(el){el.classList.add('on')});flow.dataset.s=2;flow.style.setProperty('--ty','280px');return}
var r=story.getBoundingClientRect(),span=r.height-innerHeight,p=span>0?Math.min(1,Math.max(0,-r.top/span)):0;paint(p,p<.33?0:p<.66?1:2)}
function req(){if(!raf)raf=requestAnimationFrame(update)}
addEventListener('scroll',req,{passive:true});addEventListener('resize',req);update()})();

/* Project rail: buttons, progress bar, mouse drag, card spotlight */
(function(){var rail=document.getElementById('rail');if(!rail)return;
var bar=document.querySelector('.rail-bar i'),prev=document.querySelector('.rail-btn.prev'),next=document.querySelector('.rail-btn.next');
function upd(){var max=rail.scrollWidth-rail.clientWidth,vis=rail.clientWidth/rail.scrollWidth,p=max>0?rail.scrollLeft/max:0;bar.style.setProperty('--w',(vis*100).toFixed(1)+'%');bar.style.setProperty('--x',(p*(1/vis-1)*100).toFixed(1)+'%');prev.disabled=rail.scrollLeft<4;next.disabled=rail.scrollLeft>max-4}
function step(d){var c=rail.querySelector('.rcard');rail.scrollBy({left:d*(c.offsetWidth+18),behavior:reduce?'auto':'smooth'})}
prev.addEventListener('click',function(){step(-1)});next.addEventListener('click',function(){step(1)});
rail.addEventListener('scroll',function(){requestAnimationFrame(upd)},{passive:true});addEventListener('resize',upd);upd();
var down=false,sx=0,sl=0,moved=0;
rail.addEventListener('pointerdown',function(e){if(e.pointerType!=='mouse'||e.button!==0)return;down=true;moved=0;sx=e.clientX;sl=rail.scrollLeft});
addEventListener('pointermove',function(e){if(!down)return;var dx=e.clientX-sx;moved=Math.max(moved,Math.abs(dx));if(moved>5)rail.classList.add('drag');rail.scrollLeft=sl-dx});
addEventListener('pointerup',function(){if(!down)return;down=false;rail.classList.remove('drag')});
rail.addEventListener('click',function(e){if(moved>5){e.preventDefault();e.stopPropagation();moved=0}},true);
$$('.rcard',rail).forEach(function(c){c.addEventListener('pointermove',function(e){var r=c.getBoundingClientRect();c.style.setProperty('--mx',(e.clientX-r.left)+'px');c.style.setProperty('--my',(e.clientY-r.top)+'px')})})})();

/* Google Translate injects a banner and shifts the page: remove both as soon as they appear */
(function(){function kill(){document.querySelectorAll('iframe.skiptranslate,.skiptranslate>iframe,.VIpgJd-ZVi9od-ORHb-OEVmcd,#goog-gt-tt').forEach(function(n){n.style.setProperty('display','none','important')});if(document.body.style.top)document.body.style.setProperty('top','0','important')}
new MutationObserver(kill).observe(document.body,{childList:true,attributes:true,attributeFilter:['style']});kill()})();

/* Contact links are assembled here, not written in the HTML */
var m=['miracleagbebaku122','gmail.com'],w='2349021637905',x='MiracleTechX',ig='miracle001992',gh='Miraclebot15';
var map={mail:'mailto:'+m.join('@'),wa:'https://wa.me/'+w,x:'https://x.com/'+x,ig:'https://www.instagram.com/'+ig+'/',gh:'https://github.com/'+gh};
$$('[data-c]').forEach(function(l){l.href=map[l.dataset.c];if(l.dataset.c!=='mail'){l.target='_blank';l.rel='noopener noreferrer'}});
})();


(function(){
var $=function(i){return document.getElementById(i)},$$=function(q,r){return [].slice.call((r||document).querySelectorAll(q))},reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
/* About profile terminal: a local command interpreter, never a system shell. */
var twRoot=$('terminal');
if(twRoot){
var languages=[
['Python','py','#75b9e7','def build_with_intent():\n    focus = ["AI systems", "backend", "automation"]\n    principle = "understand before changing"\n    return {"focus": focus, "principle": principle}'],
['JavaScript','js','#f0d45c','const focus = ["AI systems", "backend", "automation"];\nconst principle = "understand before changing";\n\nexport function buildWithIntent() {\n  return { focus, principle };\n}'],
['TypeScript','ts','#68a7ed','type Focus = "AI systems" | "backend" | "automation";\n\nconst focus: Focus[] = ["AI systems", "backend", "automation"];\nconst principle = "understand before changing";\n\nexport const profile = { focus, principle };'],
['C','c','#9da9bd','const char *focus[] = {"AI systems", "backend", "automation"};\nconst char *principle = "understand before changing";\n\nint main(void) {\n    return 0;\n}'],
['C++','cpp','#a7b6d8','#include <array>\n#include <string_view>\n\nconstexpr std::array focus{\n    std::string_view{"AI systems"}, "backend", "automation"\n};\nconstexpr auto principle = "understand before changing";'],
['C#','cs','#b99bdf','using System;\n\nstring[] focus = { "AI systems", "backend", "automation" };\nstring principle = "understand before changing";\nConsole.WriteLine(principle);'],
['Java','java','#e8a46d','import java.util.List;\n\nvar focus = List.of("AI systems", "backend", "automation");\nvar principle = "understand before changing";\nSystem.out.println(principle);'],
['Go','go','#6ed8df','package main\n\nvar focus = []string{"AI systems", "backend", "automation"}\nvar principle = "understand before changing"\n\nfunc main() {}'],
['Rust','rs','#e7a36d','fn main() {\n    let focus = ["AI systems", "backend", "automation"];\n    let principle = "understand before changing";\n    println!("{principle}");\n}'],
['Ruby','rb','#e58b98','focus = ["AI systems", "backend", "automation"]\nprinciple = "understand before changing"\n\nputs principle'],
['PHP','php','#a5a8eb','<?php\n$focus = ["AI systems", "backend", "automation"];\n$principle = "understand before changing";\necho $principle;'],
['Swift','swift','#f19a73','let focus = ["AI systems", "backend", "automation"]\nlet principle = "understand before changing"\nprint(principle)'],
['Kotlin','kt','#b69af4','val focus = listOf("AI systems", "backend", "automation")\nval principle = "understand before changing"\nprintln(principle)'],
['Dart','dart','#74c9d8','const focus = ["AI systems", "backend", "automation"];\nconst principle = "understand before changing";\nvoid main() => print(principle);'],
['R','r','#8eb0e8','focus <- c("AI systems", "backend", "automation")\nprinciple <- "understand before changing"\nprint(principle)'],
['Julia','jl','#c9a0dd','focus = ["AI systems", "backend", "automation"]\nprinciple = "understand before changing"\nprintln(principle)'],
['SQL','sql','#8ab7b0','SELECT focus_area, principle\nFROM profile\nWHERE focus_area IN (\n  \'AI systems\', \'backend\', \'automation\'\n);'],
['Bash','sh','#a6c78b','focus=("AI systems" "backend" "automation")\nprinciple="understand before changing"\nprintf "%s\\n" "$principle"'],
['PowerShell','ps1','#83b4e6','$focus = @("AI systems", "backend", "automation")\n$principle = "understand before changing"\nWrite-Output $principle'],
['Lua','lua','#8fbbdb','local focus = {"AI systems", "backend", "automation"}\nlocal principle = "understand before changing"\nprint(principle)'],
['Perl','pl','#9b9bd8','my @focus = ("AI systems", "backend", "automation");\nmy $principle = "understand before changing";\nprint "$principle\\n";'],
['Scala','scala','#de8e8e','val focus = List("AI systems", "backend", "automation")\nval principle = "understand before changing"\nprintln(principle)'],
['Haskell','hs','#b69be5','focus = ["AI systems", "backend", "automation"]\nprinciple = "understand before changing"\nmain = putStrLn principle'],
['Elixir','ex','#c0a1dd','focus = ["AI systems", "backend", "automation"]\nprinciple = "understand before changing"\nIO.puts(principle)'],
['MATLAB','m','#d7a08d','focus = ["AI systems", "backend", "automation"];\nprinciple = "understand before changing";\ndisp(principle)'],
['Objective-C','m','#8ab8d9','NSString *principle = @"understand before changing";\nNSArray *focus = @[@"AI systems", @"backend", @"automation"];'],
['Groovy','groovy','#91b6b2','def focus = ["AI systems", "backend", "automation"]\ndef principle = "understand before changing"\nprintln principle'],
['Assembly','asm','#b4a68a','section .data\n    principle db "understand before changing", 0\nsection .text\n    global _start'],
['Solidity','sol','#a5b9c7','// Illustrative contract-level declaration\nstring public principle = "understand before changing";\nstring[] public focus;'],
['Visual Basic','vb','#a9a0dd','Dim focus = {"AI systems", "backend", "automation"}\nDim principle = "understand before changing"\nConsole.WriteLine(principle)'],
['F#','fs','#a4a1df','let focus = [ "AI systems"; "backend"; "automation" ]\nlet principle = "understand before changing"\nprintfn "%s" principle'],
['Fortran','f90','#9fc1a4','character(len=32) :: principle\nprinciple = "understand before changing"\nprint *, trim(principle)'],
['COBOL','cob','#9db4ad','       IDENTIFICATION DIVISION.\n       PROGRAM-ID. PROFILE.\n       PROCEDURE DIVISION.\n           DISPLAY "BUILD WITH INTENT".\n           STOP RUN.'],
['Prolog','pl','#d1a16e','focus(ai_systems).\nfocus(backend).\nfocus(automation).\nprinciple("understand before changing").'],
['Erlang','erl','#dca0a0','-module(profile).\n-export([principle/0]).\nprinciple() -> "understand before changing".'],
['OCaml','ml','#e5a578','let focus = ["AI systems"; "backend"; "automation"]\nlet principle = "understand before changing"'],
['Clojure','clj','#9abda0','(def focus ["AI systems" "backend" "automation"])\n(def principle "understand before changing")\n(println principle)'],
['Lisp','lisp','#b6a0d7','(defparameter *principle* "understand before changing")\n(print *principle*)'],
['Zig','zig','#e7ad78','const focus = [_][]const u8{ "AI systems", "backend", "automation" };\nconst principle = "understand before changing";'],
['Nim','nim','#c4c88a','let focus = @["AI systems", "backend", "automation"]\nlet principle = "understand before changing"\necho principle'],
['Crystal','cr','#8ec4d2','focus = ["AI systems", "backend", "automation"]\nprinciple = "understand before changing"\nputs principle'],
['V','v','#92c4a7','fn main() {\n    focus := ["AI systems", "backend", "automation"]\n    principle := "understand before changing"\n    println(principle)\n}'],
['TypeScript JSX','tsx','#6da4e7','type Props = { focus: string[] };\n\nexport function Profile({ focus }: Props) {\n  return <p>{focus.join(" · ")}</p>;\n}'],
['HTML','html','#e59a75','<main class="profile">\n  <h1>Miracle Agbebaku</h1>\n  <p>Build with intent.</p>\n</main>'],
['CSS','css','#c4a0e8','.profile {\n  color: var(--ink);\n  border-color: var(--rule);\n  transition: transform 240ms ease;\n}'],
['JSON','json','#c8b47b','{\n  "focus": ["AI systems", "backend", "automation"],\n  "principle": "understand before changing"\n}'],
['YAML','yaml','#b8a1d5','focus:\n  - AI systems\n  - backend\n  - automation\nprinciple: understand before changing'],
['XML','xml','#d4a17e','<profile>\n  <principle>understand before changing</principle>\n</profile>'],
['Markdown','md','#a7b9cb','# Miracle Agbebaku\n\nBuild with intent.\n\n- AI systems\n- Backend\n- Automation'],
['GraphQL','graphql','#dca0c5','query Profile {\n  profile {\n    focus\n    principle\n  }\n}'],
['Dockerfile','dockerfile','#a8b7a4','FROM scratch\nLABEL profile="Miracle Agbebaku"\n# A small illustrative configuration'],
['Nix','nix','#8eaed4','{\n  focus = [ "AI systems" "backend" "automation" ];\n  principle = "understand before changing";\n}'],
['WebAssembly','wat','#b4a3d9','(module\n  (func (export "main")\n    nop))']
];
var TOP=['Python','JavaScript','TypeScript','Go','Rust','C++','Java','SQL'];
var HASH={Python:1,Ruby:1,Bash:1,PowerShell:1,Perl:1,R:1,Julia:1,YAML:1,Dockerfile:1,Nix:1,Elixir:1,Crystal:1,Nim:1,GraphQL:1,Markdown:1};
var DASH={SQL:1,Haskell:1,Lua:1};
var PCT={Erlang:1,MATLAB:1,Prolog:1};
var SEMI={Lisp:1,Clojure:1,Assembly:1,WebAssembly:1};
var KW=/^(?:def|class|return|import|from|as|if|elif|else|for|while|in|not|and|or|is|lambda|with|try|except|finally|raise|yield|async|await|const|let|var|function|export|default|new|this|type|interface|enum|extends|implements|public|private|protected|static|final|void|int|long|float|double|bool|boolean|string|char|struct|impl|fn|func|pub|mut|use|mod|match|package|using|namespace|template|trait|where|select|group|order|by|limit|insert|into|values|update|set|delete|create|table|true|false|null|nil|none|self|val|fun|object|when|begin|end|do|then|unless|echo|print|let|rec|module|open|defmodule|defp|fun|record|include|section|data|division|program|procedure|pragma|contract|uint256|string|memory|mapping|event|emit|msg|require)$/i;
function esc(t){return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function hl(code,name){
var cm=HASH[name]?'#[^\\n]*':DASH[name]?'--[^\\n]*':PCT[name]?'%[^\\n]*':SEMI[name]?';[^\\n]*':'\\/\\/[^\\n]*|\\/\\*[\\s\\S]*?\\*\\/|#(?!include\\b)[^\\n]*';
var rx=new RegExp('("(?:\\\\.|[^"\\\\\\n])*"|\'(?:\\\\.|[^\'\\\\\\n])*\'|`(?:\\\\.|[^`\\\\])*`)|('+cm+')|(#include[^\\n]*)|(\\b\\d+(?:\\.\\d+)?\\b)|([A-Za-z_][A-Za-z0-9_]*)(?=\\()|(\\b[A-Za-z_][A-Za-z0-9_]*\\b)','g');
return code.replace(rx,function(m,s,c,inc,n,f,w){
if(s)return '<span class="s">'+esc(s)+'</span>';if(c)return '<span class="c">'+esc(c)+'</span>';if(inc)return '<span class="k">'+esc(inc)+'</span>';
if(n)return '<span class="n">'+n+'</span>';if(f)return KW.test(f)?'<span class="k">'+f+'</span>':'<span class="f">'+f+'</span>';
if(w&&KW.test(w))return '<span class="k">'+w+'</span>';return esc(m)})}
var pre=$('tw-pre'),codeEl=pre.querySelector('code'),gut=$('tw-gut'),fileEl=$('tw-file'),sel=$('tw-all'),pills=$('tw-pills'),outEl=$('tw-out'),form=$('tw-form'),inp=$('tw-in'),copyB=$('tw-copy'),stateEl=$('tw-state');
var current=languages[0],typeId=0;
languages.forEach(function(x){var o=document.createElement('option');o.value=x[0];o.textContent=x[0];sel.appendChild(o)});
TOP.forEach(function(n){var x=languages.find(function(l){return l[0]===n});if(!x)return;var b=document.createElement('button');b.type='button';b.className='tw-pill';b.textContent=n;b.setAttribute('aria-pressed','false');b.dataset.n=n;b.setAttribute('translate','no');pills.appendChild(b);b.addEventListener('click',function(){setLang(n,true)})});
function textNodes(el){var w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT),a=[],n;while(n=w.nextNode())a.push(n);return a}
function typeCode(){var id=++typeId,nodes=textNodes(codeEl),full=nodes.map(function(n){return n.nodeValue});if(reduce||!full.length)return;
var car=document.createElement('i');car.className='caret';nodes.forEach(function(n){n.nodeValue=''});var ni=0,ci=0;
(function step(){if(id!==typeId){car.remove();return}
var budget=7;while(budget--&&ni<nodes.length){var s=full[ni];ci=Math.min(s.length,ci+1);nodes[ni].nodeValue=s.slice(0,ci);if(ci>=s.length){ni++;ci=0}}
if(ni<nodes.length){nodes[ni].parentNode.insertBefore(car,nodes[ni]);requestAnimationFrame(step)}else{setTimeout(function(){if(id===typeId)car.remove()},1400)}})()}
function setLang(name,animate){var x=languages.find(function(l){return l[0]===name})||languages[0];current=x;
twRoot.style.setProperty('--lang-accent',x[2]);fileEl.textContent='profile.'+x[1];sel.value=x[0];
$$('.tw-pill',pills).forEach(function(b){b.setAttribute('aria-pressed',b.dataset.n===x[0])});
var src=x[3];codeEl.innerHTML=hl(src,x[0]);var n=src.split('\n').length,g='';for(var i=1;i<=n;i++)g+=i+(i<n?'\n':'');gut.textContent=g;
pre.setAttribute('aria-label',x[0]+' code sample');if(animate)typeCode()}
sel.addEventListener('change',function(){setLang(sel.value,true)});
copyB.addEventListener('click',function(){var t=current[3];function done(){copyB.textContent='Copied';setTimeout(function(){copyB.textContent='Copy'},1500)}
if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(done,function(){})}else{var ta=document.createElement('textarea');ta.value=t;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();try{document.execCommand('copy');done()}catch(e){}ta.remove()}});
var projects=[];try{projects=JSON.parse($('project-data').textContent)}catch(e){}
function addLine(parts,i){var p=document.createElement('p');p.style.setProperty('--i',i||0);(Array.isArray(parts)?parts:[parts]).forEach(function(x){if(typeof x==='string')p.appendChild(document.createTextNode(x));else if(x.mu){var s=document.createElement('span');s.className='mu';s.textContent=x.mu;p.appendChild(s)}else{var a=document.createElement('a');a.href=x.href;a.textContent=x.text;p.appendChild(a)}});outEl.appendChild(p)}
var CMDS={
help:function(){return [['Commands: help, about, projects, principles, now, links, clear'],[{mu:'Tab completes. Arrow keys move through history.'}]]},
about:function(){return [['Miracle Agbebaku, software developer focused on AI systems, agent orchestration, backend and full-stack engineering.']]},
projects:function(){return projects.map(function(p){return [{text:p.name,href:p.slug+'.html'},{mu:'  '+p.state}]}).concat([[{mu:'Open one to read what it is for.'}]])},
principles:function(){return [['Understand the system before changing it.'],['Keep boundaries explicit. Test assumptions and failure paths.'],['Prefer reliable behavior over flashy demos.']]},
now:function(){return [['Current focus: AI engineering, backend and full-stack product development, and automation.'],['Long-term direction: robotics and hardware-aware systems.']]},
links:function(){return [[{text:'Projects',href:'projects.html'}],[{text:'Resume',href:'resume.html'}],[{text:'Contact',href:'contact.html'}]]}};
var history=[],hi=0;
function run(raw){var cmd=raw.trim().toLowerCase();if(!cmd)return;history.push(raw.trim());hi=history.length;
if(cmd==='clear'){outEl.textContent='';return}
var p=document.createElement('p');var pr=document.createElement('span');pr.className='pr';pr.textContent='miracle@portfolio ~ $ ';p.appendChild(pr);p.appendChild(document.createTextNode(raw.trim()));outEl.appendChild(p);
var lines=CMDS[cmd]?CMDS[cmd]():[['Command not found: '+cmd+'. Type help to see what is available.']];lines.forEach(function(l,i){addLine(l,i+1)});
while(outEl.children.length>70)outEl.removeChild(outEl.firstChild);outEl.scrollTop=outEl.scrollHeight}
form.addEventListener('submit',function(e){e.preventDefault();run(inp.value);inp.value='';inp.focus()});
$$('.tw-chip').forEach(function(b){b.addEventListener('click',function(){run(b.dataset.cmd)})});
inp.addEventListener('keydown',function(e){
if(e.key==='ArrowUp'&&history.length){e.preventDefault();hi=Math.max(0,hi-1);inp.value=history[hi]||''}
else if(e.key==='ArrowDown'&&history.length){e.preventDefault();hi=Math.min(history.length,hi+1);inp.value=history[hi]||''}
else if(e.key==='Tab'&&inp.value){var m=Object.keys(CMDS).concat(['clear']).filter(function(c){return c.indexOf(inp.value.toLowerCase())===0});if(m.length===1){e.preventDefault();inp.value=m[0]}}});
setLang('Python',false);run('help');
}

/* Compact searchable website translation picker. */
var $=function(i){return document.getElementById(i)};
var langRoot=$('site-language'),langTrigger=$('site-language-trigger'),langPanel=$('site-language-panel'),langSearch=$('site-language-search'),langOptions=$('site-language-options'),langCurrent=$('site-language-current');
if(langRoot&&langTrigger&&langPanel&&langSearch&&langOptions){
var siteLanguages=[
['Afrikaans','af'],['Albanian','sq'],['Amharic','am'],['Arabic','ar'],['Armenian','hy'],['Azerbaijani','az'],['Basque','eu'],['Belarusian','be'],['Bengali','bn'],['Bosnian','bs'],['Bulgarian','bg'],['Catalan','ca'],['Chinese (Simplified)','zh-CN'],['Chinese (Traditional)','zh-TW'],['Croatian','hr'],['Czech','cs'],['Danish','da'],['Dutch','nl'],['English','en'],['Estonian','et'],['Filipino','tl'],['Finnish','fi'],['French','fr'],['Galician','gl'],['Georgian','ka'],['German','de'],['Greek','el'],['Gujarati','gu'],['Haitian Creole','ht'],['Hausa','ha'],['Hebrew','iw'],['Hindi','hi'],['Hungarian','hu'],['Icelandic','is'],['Indonesian','id'],['Irish','ga'],['Italian','it'],['Japanese','ja'],['Javanese','jw'],['Kannada','kn'],['Kazakh','kk'],['Khmer','km'],['Korean','ko'],['Kurdish','ku'],['Kyrgyz','ky'],['Lao','lo'],['Latin','la'],['Latvian','lv'],['Lithuanian','lt'],['Macedonian','mk'],['Malay','ms'],['Malayalam','ml'],['Maltese','mt'],['Maori','mi'],['Marathi','mr'],['Mongolian','mn'],['Myanmar (Burmese)','my'],['Nepali','ne'],['Norwegian','no'],['Pashto','ps'],['Persian','fa'],['Polish','pl'],['Portuguese','pt'],['Punjabi','pa'],['Romanian','ro'],['Russian','ru'],['Serbian','sr'],['Sinhala','si'],['Slovak','sk'],['Slovenian','sl'],['Somali','so'],['Spanish','es'],['Sundanese','su'],['Swahili','sw'],['Swedish','sv'],['Tajik','tg'],['Tamil','ta'],['Telugu','te'],['Thai','th'],['Turkish','tr'],['Ukrainian','uk'],['Urdu','ur'],['Uzbek','uz'],['Vietnamese','vi'],['Welsh','cy'],['Yiddish','yi'],['Yoruba','yo'],['Zulu','zu']
];
function activeTranslateSelect(){return document.querySelector('.goog-te-combo')}
function renderSiteLanguages(query){langOptions.textContent='';var q=(query||'').trim().toLowerCase(),filtered=siteLanguages.filter(function(x){return x[0].toLowerCase().includes(q)||x[1].toLowerCase().includes(q)});filtered.forEach(function(x){var b=document.createElement('button');b.type='button';b.className='site-language-option';b.setAttribute('role','option');b.textContent=x[0];b.dataset.code=x[1];b.addEventListener('click',function(){chooseSiteLanguage(x[1],x[0])});langOptions.appendChild(b)});if(!filtered.length){var p=document.createElement('p');p.className='site-language-empty';p.textContent='No languages found.';langOptions.appendChild(p)}}
function chooseSiteLanguage(code,name){if(code==='en'){document.cookie='googtrans=/en/en;path=/';document.cookie='googtrans=/en/en;path=/;domain='+location.hostname;location.reload();return}var combo=activeTranslateSelect();if(combo){combo.value=code;combo.dispatchEvent(new Event('change',{bubbles:true}));langCurrent.textContent=code.toUpperCase();langPanel.hidden=true;langTrigger.setAttribute('aria-expanded','false');langTrigger.focus()}else{var target='/en/'+code;document.cookie='googtrans='+target+';path=/';document.cookie='googtrans='+target+';path=/;domain='+location.hostname;location.reload()}}
function openLang(){langPanel.hidden=false;langTrigger.setAttribute('aria-expanded','true');renderSiteLanguages(langSearch.value);langSearch.focus()}
function closeLang(){langPanel.hidden=true;langTrigger.setAttribute('aria-expanded','false')}
renderSiteLanguages('');
langTrigger.addEventListener('click',function(){if(langPanel.hidden)openLang();else closeLang()});
langSearch.addEventListener('input',function(){renderSiteLanguages(langSearch.value)});
langSearch.addEventListener('keydown',function(e){if(e.key==='Escape'){closeLang();langTrigger.focus()}if(e.key==='ArrowDown'){var first=langOptions.querySelector('button');if(first)first.focus()}});
langPanel.addEventListener('keydown',function(e){if(e.key==='Escape'){closeLang();langTrigger.focus()}});
document.addEventListener('click',function(e){if(!langRoot.contains(e.target))closeLang()});
var cookieMatch=document.cookie.match(/(?:^|;\s*)googtrans=\/en\/([^;]+)/);if(cookieMatch&&langCurrent)langCurrent.textContent=cookieMatch[1].toUpperCase();
}

})();
