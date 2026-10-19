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


/* About profile terminal: local command interpreter, never a system shell. */
var termLang=$('terminal-language'),termCode=$('terminal-code'),termFile=$('terminal-file'),termLabel=$('terminal-lang-label'),termOut=$('terminal-output'),termForm=$('terminal-form'),termInput=$('terminal-command');
if(termLang&&termCode&&termOut&&termForm){
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
languages.forEach(function(x){var o=document.createElement('option');o.value=x[0];o.textContent=x[0];termLang.appendChild(o)});
function renderCode(){var x=languages.find(function(l){return l[0]===termLang.value})||languages[0];termCode.textContent=x[3];termCode.style.setProperty('--lang-accent',x[2]);termFile.textContent='profile.'+x[1];termLabel.textContent=x[0].toUpperCase();document.querySelector('.terminal-shell').style.setProperty('--lang-accent',x[2])}
termLang.addEventListener('change',renderCode);renderCode();
var commandHelp='Available commands: help, about, projects, principles, now, clear.';
function terminalWrite(cmd,lines){var p=document.createElement('p'),prompt=document.createElement('span');prompt.className='term-muted';prompt.textContent='miracle@portfolio:~$ ';p.appendChild(prompt);p.appendChild(document.createTextNode(cmd));termOut.appendChild(p);lines.forEach(function(line){var out=document.createElement('p');out.textContent=line;termOut.appendChild(out)});termOut.scrollTop=termOut.scrollHeight}
function runCommand(raw){var cmd=raw.trim().toLowerCase();if(!cmd)return;if(cmd==='clear'){termOut.textContent='';return}var replies={
help:['Available commands: help, about, projects, principles, now, clear.'],
about:['Miracle Agbebaku — software developer focused on AI systems, agent orchestration, backend and full-stack engineering.'],
projects:['Explore the dedicated Projects page for current project descriptions and status.','Use the “Explore the projects” link beside this terminal.'],
principles:['Understand the system before changing it.','Keep boundaries explicit. Test assumptions and failure paths. Prefer reliable behavior over flashy demos.'],
now:['Current focus: AI engineering, backend/full-stack product development and automation.','Long-term direction: robotics and hardware-aware systems.']
};terminalWrite(raw,replies[cmd]||['Command not found: '+cmd+'. Type help to see available commands.'])}
termForm.addEventListener('submit',function(e){e.preventDefault();runCommand(termInput.value);termInput.value='';termInput.focus()});
var clearBtn=$('terminal-clear');if(clearBtn)clearBtn.addEventListener('click',function(){termOut.textContent='';termInput.focus()});
}
