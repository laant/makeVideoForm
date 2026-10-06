from pathlib import Path
import json,shutil
r=Path('/Users/jlee/Documents/Dev/source/myNextSeason');p=r/'autoShorts/episodes/google-messages-keep';e=json.loads((p/'episode.json').read_text());base=(r/'autoShorts/templates/scenes/_base.html').read_text()
css='''@font-face{font-family:Keep;src:url('vendor/Pretendard-Bold.ttf')}#root{font-family:Keep}.stage{inset:0;display:block}.glow,.progress,.captions{display:none}.photo{position:absolute;width:1080px;height:1920px;object-fit:cover}.shade{position:absolute;inset:0;background:linear-gradient(0deg,#faf4e8 8%,#faf4e8ee 21%,transparent 48%)}.eyebrow{position:absolute;top:300px;left:72px;background:#faf4e8ed;border-radius:12px;padding:8px 14px;font-size:27px;letter-spacing:2px}.title{position:absolute;left:70px;right:135px;top:370px;font-size:76px;line-height:1.15;letter-spacing:-3px}.card{position:absolute;left:70px;right:140px;top:1100px;background:#ffdc6c;border-radius:28px;padding:30px 34px;box-shadow:0 10px 0 #10284912}.card h2{font-size:47px;line-height:1.3}.line{font-size:37px;line-height:1.55;margin-top:12px}.note{position:absolute;top:1480px;left:73px;right:145px;font-size:25px;line-height:1.4;color:#536174}.step{display:flex;align-items:center;gap:24px;margin:12px 0;font-size:44px}.step b{background:#102849;color:#fff;border-radius:50%;width:55px;height:55px;display:grid;place-items:center;font-size:28px}.check{width:46px;height:46px;border:3px solid #102849;border-radius:10px;display:inline-grid;place-items:center;margin-right:18px}.tick{font-size:36px}.pair{display:flex;gap:24px}.mini{flex:1;background:#fff6d5;border-radius:18px;padding:22px;font-size:32px}.arrow{font-size:44px;text-align:center}.person{display:inline-block;background:#102849;color:white;border-radius:40px;padding:13px 22px;font-size:30px}.link{height:7px;background:#102849;margin:20px 30px}.original{position:absolute;left:0;top:480px;width:1080px;height:720px;object-fit:contain;background:#faf4e8}.s01 .title,.s07 .title{font-size:80px}.s03 .photo{height:1470px;object-position:50% 25%;}.s02 .photo,.s04 .photo,.s05 .photo,.s06 .photo{height:1640px;object-position:50% 0%}.s02 .title,.s04 .title,.s05 .title,.s06 .title{top:985px;font-size:62px}.s02 .card{top:1100px}.s04 .card,.s05 .card,.s06 .card{top:1110px}.s03 .title{top:990px;background:#faf4e8ee;border-radius:20px;padding:20px;font-size:60px}.s03 .card{top:1110px}.s07 .card{top:1245px}.s06 .card .line{font-size:35px}'''
content=[
'<div class="title">같이 쓰는<br>장보기 메모</div><div class="card"><h2>메시지 대신, 같은 목록</h2><div class="line">Google 메시지 × Keep</div></div>',
'<div class="title">대화에서 목록 보내기</div><div class="card"><div class="step a"><b>1</b>추가</div><div class="step b"><b>2</b>Keep 메모</div><div class="step c"><b>3</b>목록 작성 → 보내기</div></div>',
'<div class="title">샀다면, 직접 체크</div><div class="card"><div class="pair"><div class="mini">마트에서<br><br><span class="check"><span class="tick a">✓</span></span>우유</div><div class="mini">상대 목록에도<br><br><span class="check"><span class="tick b">✓</span></span>우유</div></div><div class="line c">수정하면 미리보기도 갱신</div></div>',
'<div class="title">수정이 안 된다면</div><div class="card"><h2 class="a">메모 주인에게</h2><div class="line b">수정 권한 요청하기</div><div class="arrow c">요청 → 확인</div></div>',
'<div class="title">단체방을 나가도…</div><div class="card"><span class="person a">방에서 나간 사람</span><div class="link"></div><h2 class="b">메모 접근은 남아요</h2><div class="line">채팅과 메모 권한은 별개</div></div>',
'<div class="title">공유를 끝내려면</div><div class="card"><h2 class="a">Keep → 공동작업자</h2><div class="line b">제외할 사람 삭제</div><div class="line c">→ 저장</div><div class="line" style="font-size:26px">메모 전체 삭제와 구분하세요</div></div>',
'<div class="title">내 대화창에서<br>먼저 확인하세요</div><div class="card"><h2>Keep 메모 메뉴 확인</h2><div class="line">자세한 방법은 블로그에</div></div>'
]
imgs=['couple','woman','man','permissions','permissions','permissions','end']
keys=[[],['추가','킵','보내면'],['체크','상대도','바뀐'],['주인','권한','요청'],['나가도','계속'],['공동작업자','삭제','저장'],[]]
for i,s in enumerate(e['scenes']):
 id=s['id'];d=s['timing']['duration'];note='Android 기준 · 실제 앱 UI가 아닌 설명용 그림'
 if i==4:note='출처: Google Keep 공식 도움말 · 그룹 채팅 공유 안내'
 if i==5:note='Keep → 작업 → 공동작업자 → 사용자 삭제 → 저장'
 if i==6:note='기기·계정별 메뉴 확인 · AI 이미지 및 음성 사용'
 htmlcontent=f'<div class="{id}"><div class="eyebrow">GOOGLE 메시지 × KEEP</div>'+content[i]+f'<div class="note">{note}</div></div>'
 js=f'document.getElementById("root").classList.add("{id}");stage.innerHTML='+json.dumps(htmlcontent,ensure_ascii=False)+';\n'
 js+="tl.fromTo('.photo',{scale:1},{scale:1.035,duration:S.duration,ease:'none'},0);tl.fromTo('.card',{y:22,opacity:0},{y:0,opacity:1,duration:.35,ease:'power3.out'},.12);"
 for j,key in enumerate(keys[i]):js+=f"tl.fromTo('.{chr(97+j)}',{{opacity:0,y:15}},{{opacity:1,y:0,duration:.25,ease:'power3.out'}},H.at('word:{key}'));"
 if i==4:js+="tl.to('.person',{x:120,duration:.45,ease:'power3.out'},H.at('word:나가도'));"
 bg=f'<img class="photo" src="media/{imgs[i]}.png"><div class="shade"></div>'
 if i==0:
  bg+='<img class="original" src="media/cover.webp">'
  js=js.replace("},.12);","},1.55);");js+="tl.fromTo('.title',{opacity:0},{opacity:1,duration:.3},1.55);tl.to('.original',{opacity:0,duration:.4},1.15);"
 vals={**e['theme'],'id':id,'renderDuration':str(round(d,3)),'marker':'autoshorts:custom keep-couple-v1','sceneJson':json.dumps({'id':id,'onScreen':s['onScreen'],'highlight':[],'showCaptions':False,'words':s['timing']['words'],'speechEnd':s['timing']['speechEnd'],'duration':d,'renderDuration':round(d,3),'globalStart':s['timing']['start'],'total':sum(x['timing']['duration'] for x in e['scenes'])},ensure_ascii=False),'templateStyle':css,'templateScript':js,'bgLayer':bg}
 out=base
 for k,v in vals.items():out=out.replace('{{'+k+'}}',v)
 out=out.replace('\"Pretendard\", \"Apple SD Gothic Neo\", \"Noto Sans KR\", system-ui, sans-serif','Keep, sans-serif')
 (p/f'scenes/{id}.html').write_text(out)
shutil.copy2(__file__,p/'scripts/direct-keep.py')
