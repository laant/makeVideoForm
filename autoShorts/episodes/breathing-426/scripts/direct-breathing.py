from pathlib import Path
import json,shutil
root=Path('/Users/jlee/Documents/Dev/source/myNextSeason');auto=root/'autoShorts';p=auto/'episodes/breathing-426'
ep=json.loads((p/'episode.json').read_text());total=sum(s['timing']['duration'] for s in ep['scenes'])
base=(auto/'templates/scenes/_base.html').read_text().replace('"Pretendard", "Apple SD Gothic Neo", "Noto Sans KR", system-ui, sans-serif','BreathEditorial, sans-serif')
css='''
@font-face{font-family:BreathEditorial;src:url('vendor/Pretendard-Bold.ttf');font-weight:700 900}
@font-face{font-family:BreathEditorial;src:url('vendor/Pretendard-SemiBold.ttf');font-weight:400 600}
#root{font-family:BreathEditorial,sans-serif;color:#183e42;background:#f5f0e8}.stage{display:block;inset:0}.glow,.progress{display:none}
.photo{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:55% 58%}
.wash{position:absolute;inset:0;background:linear-gradient(180deg,#f7f1e988 0%,#f7f1e92c 42%,transparent 58%,#f5f0e855 70%,#f5f0e8 92%)}
.ambient{position:absolute;width:900px;height:900px;background:radial-gradient(circle,#d6e7e277,transparent 69%);right:-250px;top:600px}.ambient.two{background:radial-gradient(circle,#edc7ab55,transparent 69%);left:-340px;top:400px}
.eyebrow{position:absolute;left:78px;top:280px;font-size:27px;font-weight:600;letter-spacing:4px;color:#547879}.edition{position:absolute;right:99px;top:283px;font-size:25px;color:#688587;letter-spacing:2px}
.headline{position:absolute;top:370px;left:74px;right:100px;font-size:110px;font-weight:800;letter-spacing:-5px;line-height:1.13;word-break:keep-all}.headline em{font-style:normal;color:#3c7c7b}.hairline{position:absolute;left:78px;top:335px;width:65px;height:5px;background:#ba7756}.lede{position:absolute;left:78px;right:100px;top:645px;font-size:37px;line-height:1.5;letter-spacing:-1px;color:#486b6c}
.mini{display:inline-flex;align-items:center;gap:12px;border-radius:99px;padding:14px 23px;background:#f8f4e9ed;border:1px solid #acbeb388;font-size:32px;font-weight:700;color:#346869}
.captions{left:68px;right:100px;bottom:430px;height:110px}.cap{font-family:BreathEditorial,sans-serif;font-size:43px;font-weight:700;line-height:1.4;letter-spacing:-1px;text-shadow:none;color:#fdfaf3}.cap>span{display:block;background:#193e40f0;border-radius:16px;padding:15px 24px;box-shadow:0 8px 30px #14323616}.cap em{color:#eec39f}
.steps{position:absolute;left:77px;right:102px;top:734px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.step{height:410px;border:2px solid #c9d9d5;border-radius:130px 130px 25px 25px;background:#fbf9f3;padding:34px 12px;text-align:center;transform-origin:50% 90%;color:#365f60}.step b{font-size:176px;line-height:1.3;letter-spacing:-7px;display:block}.step span{font-size:39px;letter-spacing:-1px;display:block}.step small{font-size:27px;display:block;margin-top:18px;color:#647e7a}.step.two{background:#f1e7d7;border-color:#dfc8ad}.step.two b{color:#a36b4e}.step.three{background:#d9e7e2;border-color:#bdd2ca}.rhythm{position:absolute;left:82px;right:106px;top:1210px;display:flex;gap:8px;height:14px}.rhythm i{display:block;border-radius:10px;background:#78a5a1}.rhythm i:nth-child(2){background:#c99b75}.rhythm i:nth-child(3){background:#3c7c7b}.rhythm-label{position:absolute;top:1251px;left:82px;font-size:31px;color:#647e7a;letter-spacing:1px}
.posture-window{position:absolute;left:479px;top:639px;width:495px;height:616px;overflow:hidden;border-radius:230px 230px 28px 28px;background:#e5dfd1}.posture-window img{width:100%;height:100%;object-fit:cover;object-position:50% 65%}
.pointers{position:absolute;left:80px;top:710px;width:375px;display:flex;flex-direction:column;gap:49px}.pointer{font-size:38px;line-height:1.35;letter-spacing:-1.5px}.pointer small{display:block;font-size:26px;color:#647e7a;letter-spacing:-.5px;margin-top:12px}.pointer i{display:block;width:27px;height:5px;background:#a3beba;margin-bottom:18px}.safety{position:absolute;left:79px;right:103px;top:1280px;background:#e9dfd1;border:1px solid #d1bc9d;border-radius:15px;padding:20px 20px;text-align:center;font-size:32px;color:#704f3c;letter-spacing:-.5px}
.guide-title{position:absolute;left:65px;right:95px;top:376px;font-size:88px;line-height:1.2;letter-spacing:-4px;text-align:center;font-weight:800}.guide-hint{position:absolute;left:70px;right:100px;top:503px;text-align:center;font-size:31px;color:#5d7d7a;letter-spacing:-.6px}.breath-stage{position:absolute;left:510px;top:889px;width:0;height:0}.orbit{position:absolute;left:-285px;top:-285px;width:570px;height:570px;border:1.5px solid #b5cbc480;border-radius:50%}.orbit:after{content:'';position:absolute;inset:22px;border:1px solid #b5cbc440;border-radius:50%}.breath-disc{position:absolute;left:-275px;top:-275px;width:550px;height:550px;border-radius:50%;background:radial-gradient(circle at 35% 28%,#e5eee5,#b4d2c9 57%,#86b3ab);box-shadow:0 24px 60px #659f8c20,inset 0 1px 1px #fff;transform-origin:center}.countwrap{position:absolute;left:-220px;top:-135px;width:440px;height:240px;text-align:center}.count{position:absolute;inset:0;font-size:207px;line-height:1.1;font-weight:600;color:#194c4e;letter-spacing:-10px;opacity:0}.seconds{position:absolute;left:-100px;top:102px;width:200px;text-align:center;font-size:30px;color:#456d67;letter-spacing:3px}.phase-nav{position:absolute;left:79px;right:103px;top:1200px;display:grid;grid-template-columns:4fr 2fr 6fr;gap:10px}.phase-nav span{padding:17px 5px;border-top:5px solid #d4ded4;text-align:center;font-size:27px;color:#81918a;white-space:nowrap}.phase-nav .active{border-color:#3c7c7b;color:#234f50;font-weight:700}.guide-safety{position:absolute;left:60px;right:90px;top:1290px;text-align:center;color:#6f796f;font-size:24px;line-height:1.4}.guide-safety b{font-weight:700;color:#8e6147}.tiny-source{position:absolute;left:80px;right:105px;top:1322px;font-size:24px;color:#587b77;line-height:1.45}
.calm-window{position:absolute;left:75px;right:101px;top:691px;height:479px;border-radius:25px;overflow:hidden}.calm-window img{width:100%;height:100%;object-fit:cover;object-position:50% 58%}.evidence{position:absolute;left:78px;right:103px;top:1209px;border-top:1px solid #b6cbc2;padding-top:21px;display:flex;gap:18px;font-size:33px;letter-spacing:-.7px;color:#476e68}.evidence b{color:#a26648;font-weight:700}.return-note{position:absolute;left:77px;right:101px;top:1100px;border-radius:17px;background:#f8f3e8ed;padding:24px 27px;font-size:36px;line-height:1.45;color:#325f60;letter-spacing:-.9px}.save{position:absolute;left:78px;right:103px;top:1260px;display:flex;justify-content:space-between;align-items:center;background:#356f6e;color:#fff9ef;padding:23px 31px;border-radius:18px;font-size:38px;font-weight:700}.save strong{letter-spacing:9px;font-size:36px}.ending-first{position:absolute;inset:0}.ending-second{position:absolute;inset:0}
'''

scripts={
's01':'''stage.innerHTML=`<div class="eyebrow">잠깐, 숨 고르기</div><div class="edition">BREATH / 01</div><div class="hairline"></div><div class="headline">긴장될 때,<br><em>숨부터 천천히</em></div><div class="lede"><span class="mini">4 · 2 · 6 호흡</span></div>`;
tl.fromTo('.headline',{y:20},{y:0,duration:.65,ease:'power2.out'},0);tl.fromTo('.mini',{opacity:0,y:15},{opacity:1,y:0,duration:.5},.5);''',
's02':'''stage.innerHTML=`<div class="eyebrow">기억할 숫자는 세 가지</div><div class="edition">4 / 2 / 6</div><div class="hairline"></div><div class="headline" style="font-size:92px">들이쉬고, 멈추고,<br><em>길게 내쉬어요</em></div><div class="steps"><div class="step one"><b>4</b><span>들이마시기</span><small>코로 편안히</small></div><div class="step two"><b>2</b><span>잠깐 멈춤</span><small>무리하지 않기</small></div><div class="step three"><b>6</b><span>내쉬기</span><small>부드럽게</small></div></div><div class="rhythm"><i style="flex:4"></i><i style="flex:2"></i><i style="flex:6"></i></div><div class="rhythm-label">한 주기 = 12초</div>`;
['one','two','three'].forEach((c,i)=>tl.fromTo('.'+c,{opacity:.32,y:20},{opacity:1,y:0,duration:.5,ease:'power2.out'},[0,H.at('word:이',2.65),H.at('word:육',5.22)][i]));tl.fromTo('.rhythm',{scaleX:0,transformOrigin:'left'},{scaleX:1,duration:1.2},7.2);''',
's03':'''stage.innerHTML=`<div class="eyebrow">시작하기 전에</div><div class="edition">PREPARE</div><div class="hairline"></div><div class="headline" style="font-size:100px">편하게 앉고,<br><em>무리하지 않기</em></div><div class="posture-window"><img src="media/posture.png"></div><div class="pointers"><div class="pointer"><i></i>어깨는 편안하게<small>힘을 빼고 앉으세요</small></div><div class="pointer"><i></i>억지로 크게<br>쉬지 않기</div><div class="pointer"><i></i>멈춤이 불편하면<small>평소처럼 자연스럽게</small></div></div><div class="safety">어지럽거나 답답하면 중단하세요</div>`;
tl.fromTo('.pointer',{opacity:.5,x:-12},{opacity:1,x:0,duration:.5,stagger:.45},.1);tl.fromTo('.safety',{opacity:.4},{opacity:1,duration:.5},1);''',
's07':'''stage.innerHTML=`<div class="eyebrow">숫자보다 중요한 것</div><div class="edition">KEEP IT GENTLE</div><div class="hairline"></div><div class="headline" style="font-size:106px">천천히,<br><em>편안하게</em></div><div class="calm-window"><img src="media/calm.png"></div><div class="evidence"><span>스트레스 완화에 도움 가능</span></div><div class="tiny-source">호흡 훈련 연구 전반의 결과 · 426만의 효과 보장 아님</div>`;
tl.fromTo('.calm-window img',{scale:1.04},{scale:1.09,duration:S.duration,ease:'none'},0);tl.to('.evidence',{opacity:0,duration:.2},H.at('word:특별한',4.9)-.25);tl.call(()=>{},[],0);
const caveat=H.el('div','evidence',null,stage);caveat.innerHTML='<b>이완 연습</b><span>치료를 대신하지 않아요</span>';tl.fromTo(caveat,{opacity:0,y:10},{opacity:1,y:0,duration:.35},H.at('word:특별한',4.9));''',
's08':'''stage.innerHTML=`<div class="eyebrow">내 호흡에 맞게</div><div class="edition">SAVE & BREATHE</div><div class="hairline"></div><div class="headline" style="font-size:98px"><span class="end-a">불편하면,<br><em>평소 호흡으로</em></span><span class="end-b" style="position:absolute;left:0;top:0">편안했다면,<br><em>저장해 두세요</em></span></div><div class="return-note">어지럽거나 답답하면<br>중단하고 자연스럽게 쉬세요</div><div class="save"><span>필요할 때, 천천히</span><strong>4·2·6</strong></div>`;
tl.set('.end-b',{opacity:0},0);tl.to('.end-a',{opacity:0,y:-10,duration:.25},H.at('word:편안했다면',4.3));tl.fromTo('.end-b',{opacity:0,y:15},{opacity:1,y:0,duration:.4},H.at('word:편안했다면',4.3)+.2);tl.fromTo('.save',{opacity:0,y:20},{opacity:1,y:0,duration:.4},H.at('word:저장해',5.5));'''
}

def guide(s):
    phase=s['onScreen']['breathPhase'];d=s['onScreen']['phaseSeconds']
    idx={'inhale':0,'hold':1,'exhale':2}[phase]
    title=['들이마셔요','잠깐 멈춰요','천천히 내쉬어요'][idx]
    hint=['코로 편안히 들이마셔요','불편하면 멈춤 없이 자연스럽게','힘을 빼고 부드럽게 내쉬어요'][idx]
    begin,end=[(.48,1),(1,1),(1,.48)][idx]
    counts=''.join(f'<span class="count n{k}">{d-k}</span>' for k in range(d))
    nav=''.join(f'<span class="{"active" if j==idx else ""}">{t}</span>' for j,t in enumerate(['4초 들숨','2초 멈춤','6초 날숨']))
    return f'''stage.innerHTML=`<div class="eyebrow">함께 한 번 · 총 12초</div><div class="edition">FOLLOW YOUR BREATH</div><div class="guide-title">{title}</div><div class="guide-hint">{hint}</div><div class="breath-stage"><div class="orbit"></div><div class="breath-disc"></div><div class="countwrap">{counts}</div><div class="seconds">초</div></div><div class="phase-nav">{nav}</div><div class="guide-safety">멈춤이 불편하면 평소처럼 호흡하세요<br><b>어지럽거나 답답하면 중단</b></div>`;
tl.fromTo('.breath-disc',{{scale:{begin}}},{{scale:{end},duration:{d},ease:'none'}},0);
for(let k=0;k<{d};k++){{tl.set('.n'+k,{{opacity:1}},k);tl.set('.n'+k,{{opacity:0}},k+1);}}
window.__breathSpec={{phase:'{phase}',seconds:{d},frames:{d*30},initialScale:{begin},endScale:{end}}};
'''

for s in ep['scenes']:
    id=s['id'];duration=s['timing']['duration']
    data={'id':id,'onScreen':s['onScreen'],'highlight':[],'showCaptions':s['onScreen']['showCaptions'],'words':s['timing']['words'],'speechEnd':s['timing']['speechEnd'],'duration':duration,'renderDuration':round(duration,3),'globalStart':s['timing']['start'],'total':round(total,3)}
    photo={'s01':'pause.png','s08':'calm.png'}.get(id)
    bg=f'<img class="photo" src="media/{photo}"><div class="wash"></div>' if photo else '<div class="ambient"></div><div class="ambient two"></div>'
    script=guide(s) if 'breathPhase' in s['onScreen'] else scripts[id]
    if photo:script+="\ntl.fromTo('.photo',{scale:1.015},{scale:1.055,duration:S.duration,ease:'none'},0);"
    vals={**ep['theme'],'id':id,'renderDuration':str(round(duration,3)),'marker':'autoshorts:custom breathing-426 codex-director-v1','sceneJson':json.dumps(data,ensure_ascii=False),'templateStyle':css,'templateScript':script,'bgLayer':bg}
    html=base
    for k,v in vals.items():html=html.replace('{{'+k+'}}',v)
    (p/'scenes'/f'{id}.html').write_text('\n'.join(l.rstrip() for l in html.splitlines())+'\n')
shutil.copy2(__file__,p/'scripts/direct-breathing.py')
print('Authored eight scenes; s04/s05/s06 form one continuous 12-second guide.')
