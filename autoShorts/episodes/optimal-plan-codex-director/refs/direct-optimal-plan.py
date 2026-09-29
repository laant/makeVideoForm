from pathlib import Path
import json, shutil

root=Path('/Users/jlee/Documents/Dev/source/myNextSeason')
auto=root/'autoShorts'
dst=auto/'episodes/optimal-plan-codex-director'
ep=json.loads((dst/'episode.json').read_text())
base=(auto/'templates/scenes/_base.html').read_text()
shutil.copy2(root/'flow-pipeline/fonts/Pretendard-Bold.ttf',dst/'vendor/Pretendard-Bold.ttf')
shutil.copy2(root/'flow-pipeline/fonts/Pretendard-SemiBold.ttf',dst/'vendor/Pretendard-SemiBold.ttf')
css='''
@font-face{font-family:Editorial;src:url('vendor/Pretendard-Bold.ttf');font-weight:700 900}
@font-face{font-family:Editorial;src:url('vendor/Pretendard-SemiBold.ttf');font-weight:400 600}
#root{font-family:Editorial,sans-serif;background:#09281f;color:#f6f1e7}
.stage{display:block;inset:0}.glow{display:none}.progress{height:5px;top:255px;left:72px;width:900px;background:#a3e4bf}
.photo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:50% 65%}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(3,20,14,.55),rgba(3,20,14,.6) 34%,transparent 55%,rgba(3,20,14,.18) 68%,#072019 88%)}
.eyebrow{position:absolute;left:76px;top:290px;font-size:28px;font-weight:600;letter-spacing:5px;color:#a3e4bf}
.page{position:absolute;right:100px;top:290px;font-size:27px;color:#a3e4bf;letter-spacing:3px}
.headline{position:absolute;left:72px;right:100px;top:365px;font-size:106px;line-height:1.1;letter-spacing:-5px;font-weight:800;word-break:keep-all}
.headline em{font-style:normal;color:#a3e4bf}.rule{width:68px;height:8px;background:#d47c5f;margin-bottom:26px}
.pill{display:inline-block;border-radius:100px;padding:13px 23px;font-size:31px;line-height:1.2;letter-spacing:-1px;background:#a3e4bf;color:#0a2b20;font-weight:700}
.notice{position:absolute;left:86px;right:116px;top:1110px;padding:26px 30px;border:1px solid #b2cfc266;border-radius:23px;background:#09281ff2;box-shadow:0 20px 65px #0005;display:flex;align-items:center;gap:24px}
.notice-icon{width:72px;height:72px;border-radius:18px;background:#a3e4bf;color:#123529;display:grid;place-items:center;font-size:40px}
.notice small{display:block;font-size:26px;color:#bbccbf;margin-bottom:8px}.notice strong{font-size:43px;letter-spacing:-1px}
.captions{bottom:430px;left:65px;right:95px;height:110px}.cap{font-family:Editorial;font-size:43px;font-weight:700;letter-spacing:-1px;text-shadow:none;line-height:1.35}.cap>span{padding:14px 25px;border-radius:14px;background:#072019ed;border:1px solid #bbd0c329;box-shadow:0 8px 25px #0002}.cap em{color:#a3e4bf}
#root.paper{background:#f2eee4;color:#153b2b}.paper .eyebrow,.paper .page{color:#416854}.paper .progress{background:#396b4e}.paper .headline em{color:#427b57}.paper .shade{background:#f2eee4f0}.paper .photo{opacity:.17}
.window{position:absolute;left:74px;right:102px;top:760px;height:422px;overflow:hidden;border-radius:24px;background:#12392c}
.window img{width:100%;height:100%;object-fit:cover;object-position:50% 72%;transform:scale(1.02)}
.window:after{content:'';position:absolute;inset:0;box-shadow:inset 0 0 0 1px #24422b1a;border-radius:24px}
.subnote{position:absolute;left:76px;right:105px;top:1250px;font-size:31px;line-height:1.5;color:#52705e}
.period{position:absolute;left:74px;top:555px;display:flex;align-items:center;gap:24px}.period b{font-size:190px;letter-spacing:-14px;line-height:1;color:#1c593d}.period span{font-size:63px;letter-spacing:-3px;line-height:1.08}.period small{display:block;font-size:27px;letter-spacing:0;color:#52705e;margin-top:10px}
.months{position:absolute;right:108px;top:591px;display:flex;gap:7px;align-items:end;height:100px}.month{width:20px;background:#99c0a4;border-radius:5px 5px 0 0;transform-origin:bottom}.month:nth-child(4){background:#d47759}
.chips{position:absolute;left:74px;right:105px;top:1038px;display:flex;flex-direction:column;gap:18px}.chip{padding:23px 28px;border-radius:18px;font-size:43px;background:#f4efe5;color:#163b2b;box-shadow:0 10px 30px #0002;display:flex;justify-content:space-between;align-items:center}.chip span{font-size:27px;color:#8c4c36}.coral{color:#f1ab8e!important}
.checks{position:absolute;left:74px;right:103px;top:638px;display:flex;flex-direction:column;gap:23px}.checkrow{position:relative;height:207px;border-radius:22px;border:2px solid #d4dccf;background:#fffcf5;padding:28px;display:flex;gap:24px;align-items:center;box-shadow:0 10px 30px #21432d07}.checknum{font-size:34px;color:#6c9175;width:56px;align-self:flex-start;padding-top:7px}.checktext{color:#153b2b;font-size:49px;letter-spacing:-2px;line-height:1.15}.checktext small{display:block;font-size:28px;color:#6a7c6c;letter-spacing:-.5px;margin-top:15px}.checkmark{margin-left:auto;width:50px;height:50px;border-radius:50%;background:#256444;color:#fff;display:grid;place-items:center;font-size:30px}.peak{position:absolute;right:104px;bottom:31px;display:flex;align-items:end;gap:6px;height:55px}.peak i{display:block;width:13px;background:#a5c2a4}.peak i:nth-child(4){background:#cc7150}
.compare-head{font-size:99px}.scope{position:absolute;left:74px;right:102px;top:670px;display:grid;grid-template-columns:1fr 1.1fr;gap:25px;z-index:2}.scope-card{border-radius:20px;background:#e0e7da;padding:24px;font-size:34px;line-height:1.3;color:#32533b;border:2px solid #c6d5c6}.scope-card strong{font-size:41px;display:block;margin-bottom:10px;letter-spacing:-1px}.scope-card.wide{background:#20563b;color:#fcf7e9;border-color:#20563b}.scope-card small{font-size:29px}.scope-card.wide small{color:#c0e1c1}.scope-photo{top:872px;height:345px}.scope-note{position:absolute;top:1252px;left:76px;font-size:40px;letter-spacing:-1px;color:#234f34}.cta{position:absolute;left:75px;right:104px;top:1142px;padding:28px 34px;background:#c6e6bc;border-radius:19px;color:#123a27;font-size:45px;display:flex;justify-content:space-between;align-items:center}.cta b{font-size:52px}.tagline{position:absolute;left:76px;top:650px;font-size:35px;color:#c6d6c9}.footer-note{background:#08271fdd;padding:9px 13px;border-radius:8px;position:absolute;top:1310px;left:77px;font-size:25px;color:#adc1b2}
'''

scripts={
's01': '''
stage.innerHTML=`<div class="eyebrow">생활비를 읽는 법</div><div class="page">01 / 06</div><div class="headline"><div class="rule"></div>더 싼 요금제,<br><em>문자가 온다</em></div><div class="tagline"><span class="pill">10월 1일 시행</span></div><div class="notice"><div class="notice-icon">↘</div><div><small>내 사용량을 바탕으로</small><strong>요금제 추천 안내</strong></div></div>`;
tl.fromTo('.headline',{y:24,scale:1.02},{y:0,scale:1,duration:.6,ease:'power3.out'},0);
tl.fromTo('.notice',{opacity:0,y:70},{opacity:1,y:0,duration:.6,ease:'power3.out'},1.2);
tl.fromTo('.tagline',{opacity:0,y:15},{opacity:1,y:0,duration:.4},.3);
''',
's02': '''
stage.innerHTML=`<div class="eyebrow">추천이 오는 방식</div><div class="page">02 / 06</div><div class="headline" style="font-size:83px;top:366px">내 사용량을 보고</div><div class="period"><b>6</b><span>개월마다<small>SKT · KT · LG U+</small></span></div><div class="months">${[42,63,55,96,73,50].map(h=>`<div class="month" style="height:${h}px"></div>`).join('')}</div><div class="window"><img src="media/bg-s02.png"></div><div class="subnote"><b>사용량 분석</b> &nbsp; → &nbsp; 문자 안내<br><span style="font-size:26px">후불 가입자 대상 · 알뜰폰 제외</span></div>`;
tl.fromTo('.period b',{scale:.8},{scale:1,duration:.5,ease:'back.out(1.7)'},H.at('word:여섯',1));
tl.fromTo('.month',{scaleY:.1},{scaleY:1,stagger:.12,duration:.5,ease:'power2.out'},.4);
tl.fromTo('.window img',{scale:1.09},{scale:1.02,duration:S.renderDuration,ease:'none'},0);
tl.fromTo('.subnote',{opacity:0,y:20},{opacity:1,y:0,duration:.5},H.at('word:사용량',3));
''',
's03': '''
stage.innerHTML=`<div class="eyebrow coral">바꾸기 전, 잠깐</div><div class="page">03 / 06</div><div class="headline"><div class="rule"></div><div class="claim">무조건<br>이득일까?</div><div class="answer" style="position:absolute;top:34px;left:0">오히려<br><em class="coral">손해일 수도</em></div></div><div class="chips"><div class="chip c1">약정 위약금 <span>추가 부담 확인</span></div><div class="chip c2">가족 결합 할인 <span>유지 여부 확인</span></div></div>`;
tl.set('.answer',{opacity:0},0);tl.set('.chip',{opacity:0,y:30},0);
tl.to('.claim',{opacity:0,y:-15,duration:.23},2.65);tl.fromTo('.answer',{opacity:0,y:20},{opacity:1,y:0,duration:.35},2.85);
tl.to('.c1',{opacity:1,y:0,duration:.4},H.at('word:약정',3.53));tl.to('.c2',{opacity:1,y:0,duration:.4},H.at('word:가족',4.08));
''',
's04': '''
stage.innerHTML=`<div class="eyebrow">변경 전 체크리스트</div><div class="page">04 / 06</div><div class="headline" style="font-size:91px">문자를 받으면<br><em>세 가지 확인</em></div><div class="checks"><div class="checkrow r1"><div class="checknum">01</div><div class="checktext">최대 사용량<small>평균 사용량만 보지 않기</small></div><div class="peak">${[23,30,25,54,31].map(h=>`<i style="height:${h}px"></i>`).join('')}</div><div class="checkmark">✓</div></div><div class="checkrow r2"><div class="checknum">02</div><div class="checktext">약정 위약금<small>변경 시 추가 부담 확인</small></div><div class="checkmark">✓</div></div><div class="checkrow r3"><div class="checknum">03</div><div class="checktext">가족 결합 할인<small>인터넷 결합도 함께 확인</small></div><div class="checkmark">✓</div></div></div>`;
tl.set('.checkmark',{opacity:0,scale:.5},0);tl.set('.checkrow',{opacity:.45},0);
['최대','위약금','결합'].forEach((word,i)=>{let at=H.at('word:'+word,[3.99,6.01,7.04][i]);tl.to('.r'+(i+1),{opacity:1,borderColor:'#508263',backgroundColor:'#ffffff',duration:.28},at);tl.to('.r'+(i+1)+' .checkmark',{opacity:1,scale:1,duration:.3,ease:'back.out(2)'},at);});
tl.fromTo('.peak i',{scaleY:.15,transformOrigin:'bottom'},{scaleY:1,duration:.5,stagger:.07},3.8);
''',
's05': '''
stage.innerHTML=`<div class="eyebrow">비교 범위를 넓히세요</div><div class="page">05 / 06</div><div class="headline compare-head">추천이 곧<br><em>최저가는 아니다</em></div><div class="scope"><div class="scope-card"><strong>통신사 안내</strong><small>내 통신사 안에서</small></div><div class="scope-card wide"><strong>스마트초이스</strong><small>알뜰폰·타사까지</small></div></div><div class="window scope-photo"><img src="media/bg-s05.png"></div><div class="scope-note">한 곳의 추천 → 더 넓은 비교</div>`;
tl.set('.wide',{opacity:.12,y:20},0);tl.set('.scope-note',{opacity:0},0);
tl.to('.wide',{opacity:1,y:0,duration:.45,ease:'power3.out'},H.at('word:알뜰폰까지',4.36));tl.to('.scope-note',{opacity:1,duration:.4},H.at('word:스마트초이스',5.98));
tl.fromTo('.window img',{scale:1.1,x:15},{scale:1.02,x:0,duration:S.renderDuration,ease:'none'},0);
''',
's06': '''
stage.innerHTML=`<div class="eyebrow">마지막으로 확인</div><div class="page">06 / 06</div><div class="headline"><div class="rule"></div>나머지 두 가지는<br><em>설명란에</em></div><div class="tagline">바꾸기 전에, 한 번 더 확인하세요.</div><div class="cta"><span>확인 항목 이어 보기</span><b>↓</b></div><div class="footer-note">2026.09.29 기준 · 세부 안내는 달라질 수 있습니다</div>`;
tl.fromTo('.cta',{y:30,opacity:0},{y:0,opacity:1,duration:.5},.4);
tl.fromTo('.cta b',{y:-6},{y:7,duration:.55,repeat:3,yoyo:true,ease:'sine.inOut'},1.4);
'''
}
for i,s in enumerate(ep['scenes']):
    duration=s['timing']['duration']
    data={'id':s['id'],'onScreen':s['onScreen'],'highlight':s['onScreen'].get('highlight',[]),'words':s['timing']['words'],'speechEnd':s['timing']['speechEnd'],'duration':duration,'renderDuration':duration,'globalStart':s['timing']['start'],'total':39.773}
    script=scripts[s['id']]+"\ntl.fromTo('.photo',{scale:1.02},{scale:1.085,duration:S.renderDuration,ease:'none'},0);"
    vals={**ep['theme'],'id':s['id'],'renderDuration':str(duration),'marker':'autoshorts:custom codex-director-v1','sceneJson':json.dumps(data,ensure_ascii=False),'templateStyle':css,'templateScript':script,'bgLayer':f'<img class="photo" src="media/bg-{s["id"]}.png"><div class="shade"></div>'}
    html=base.replace('"Pretendard", "Apple SD Gothic Neo", "Noto Sans KR", system-ui, sans-serif', 'Editorial, sans-serif')
    for k,v in vals.items():html=html.replace('{{'+k+'}}',v)
    if s['id'] in ['s02','s04','s05']:html=html.replace('<div id="root" data-composition-id=', '<div id="root" class="paper" data-composition-id=')
    (dst/'scenes'/f'{s["id"]}.html').write_text(html)
shutil.copy2(__file__,dst/'refs/direct-optimal-plan.py')
(dst/'refs/ART-DIRECTION.md').write_text('''# Codex director cut

Original episode: optimal-plan. Original narration, timing and caption retained.
Built-in image_gen produced six original editorial photographs; prompts are in imagegen-prompts.json.
All text, diagrams, checks and transitions are deterministic HTML/GSAP. No new TTS or factual claims generated.
Visual system: forest green / warm ivory / restrained coral; alternating photography-led and explanation-led scenes.
Shots: notification → six-month interval → true-cost reversal → three checks → wider comparison → description CTA.
Fonts: existing project Pretendard files. Audio: existing optimal-plan narration and autoShorts SFX.
Rebuild custom scenes: run this refs/direct-optimal-plan.py after build-scenes.js. Do not use scenes --force afterward.
''')
print('Six bespoke narration-synchronized scenes authored.')
