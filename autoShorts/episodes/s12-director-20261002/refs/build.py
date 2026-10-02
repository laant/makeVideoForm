from pathlib import Path
import json,shutil,subprocess,hashlib,math,html
W=Path(__file__).parent
SRC=Path('/Users/jlee/Documents/Dev/source/myNextSeason/autoShorts')
M=W/'autoshorts'; M.mkdir(exist_ok=True)
for d in ['scripts','assets','templates']:
 if not (M/d).exists(): shutil.copytree(SRC/d,M/d)
shutil.copy(SRC/'package.json',M/'package.json')
if not (M/'node_modules').exists(): (M/'node_modules').symlink_to(SRC/'node_modules',target_is_directory=True)
P=M/'episodes/s12-director-20261002'
for d in ['audio','media','scenes','vendor','refs']: (P/d).mkdir(parents=True,exist_ok=True)
for f in W.glob('scene-*.png'):shutil.copy(f,P/'media'/f.name)
for f in (W/'edge-audio').glob('*'):shutil.copy(f,P/'audio'/f.name)
for f in (SRC/'episodes/optimal-plan-codex-director/vendor').glob('*'):shutil.copy(f,P/'vendor'/f.name)
board=json.loads((W/'storyboard.json').read_text());scenes=[];elapsed=0
def run(a):subprocess.run(a,check=True,stdout=subprocess.DEVNULL)
def probe(f):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(f)]))
for s in board['scenes']:
 sid=s['id'];dur=math.ceil((probe(P/'audio'/f'{sid}.mp3')+.3)*30)/30
 words=[]
 for b in json.loads((P/'audio'/f'{sid}.boundaries.json').read_text()):
  d=b['Data'];words.append({'text':d['text']['Text'],'start':d['Offset']/1e7,'end':(d['Offset']+d['Duration'])/1e7})
 dur=math.ceil((words[-1]['end']+.45)*30)/30
 timing={'hash':hashlib.sha256(s['narration'].encode()).hexdigest(),'start':round(elapsed,3),'duration':round(dur,3),'speechEnd':words[-1]['end'],'words':words}
 scenes.append({'id':sid,'template':'title','narration':s['narration'],'onScreen':s,'timing':timing,'transitionOut':'cut','sfx':[{'name':'pop','at':.4,'volume':.2}]})
 run(['ffmpeg','-y','-loglevel','error','-i',str(P/'audio'/f'{sid}.mp3'),'-af',f'apad,atrim=duration={dur}',str(P/'audio'/f'{sid}.wav')]);elapsed+=dur
(P/'audio/concat.txt').write_text(''.join("file '"+str(P/'audio'/f"{s['id']}.wav")+"'\n" for s in scenes))
run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(P/'audio/concat.txt'),'-c:a','libmp3lame','-b:a','192k',str(P/'audio/narration.mp3')])
ep={'slug':P.name,'topic':'갤럭시 탭 S12, 큰 화면보다 내 작업부터','scenes':scenes,'transitionSeconds':0,'caption':'공식 발표 기반 자료 조사. 생성 장면은 제품 실물이나 실제 앱 화면이 아닙니다. https://pulluptech.blogspot.com/2026/10/s12.html','upload':{'youtube':False,'instagram':False,'channel':'tech','title':'갤럭시 탭 S12, 큰 화면보다 내 작업부터'},'voice_note':'External approved Microsoft Edge ko-KR-SunHiNeural +0%; timing imported from actual WordBoundary response, not estimated.'}
(P/'episode.json').write_text(json.dumps(ep,ensure_ascii=False,indent=2))
(P/'hyperframes.json').write_text(json.dumps({'paths':{'assets':'audio'}}))
css='''*{box-sizing:border-box;margin:0}html,body,#root{width:1080px;height:1920px;overflow:hidden;background:#edf3fa} @font-face{font-family:P;src:url('vendor/Pretendard-Bold.ttf')}#root{position:relative;font-family:P;color:#102749}.photo{position:absolute;width:1080px;height:1920px;object-fit:cover}.shade{position:absolute;inset:0;background:linear-gradient(180deg,#edf3faff 0%,#edf3faf0 25%,#edf3fa00 48%,#edf3fa00 61%,#102749df 82%,#102749 100%)}.label{position:absolute;left:74px;top:275px;font-size:29px;letter-spacing:3px;color:#365985}.title{position:absolute;left:72px;right:100px;top:335px;font-size:84px;line-height:1.13;letter-spacing:-3px}.note{position:absolute;left:74px;right:110px;top:570px;font-size:34px;line-height:1.4;color:#315784}.cards{position:absolute;left:74px;right:110px;top:720px;display:flex;gap:22px}.card{background:#f8fbffff;border:2px solid #bed1e6;border-radius:22px;padding:28px;flex:1;font-size:37px;color:#21466f;box-shadow:0 12px 45px #172d431a}.card b{display:block;font-size:79px;color:#17345c;letter-spacing:-3px;margin:13px 0}.card small{font-size:29px}.captions{position:absolute;left:70px;right:120px;top:1220px;height:130px;color:white;display:flex;align-items:center;justify-content:center;text-align:center}.cap{position:absolute;font-size:47px;line-height:1.3;background:#102749f5;padding:18px 27px;border-radius:16px;opacity:0;max-width:870px}.foot{display:none;position:absolute;top:1165px;left:74px;font-size:25px;color:#e3ecf5}.bar{position:absolute;left:74px;top:253px;width:898px;height:5px;background:#487aca;transform-origin:left}.steps{position:absolute;top:760px;left:74px;right:110px;display:flex;flex-direction:column;gap:20px}.step{padding:25px 32px;border-radius:19px;background:#f9fcfff2;font-size:48px;color:#16395f;border:2px solid #c9dbee}.badge{position:absolute;top:1020px;left:74px;background:#254d7c;color:white;border-radius:18px;padding:22px 30px;font-size:39px}'''
clips=[];srt=[]
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
for i,s in enumerate(scenes):
 sid=s['id'];t=s['timing'];o=s['onScreen'];dur=t['duration']; extra=''
 if i==5:o['image']='media/scene-tablets.png'
 if i==1:extra='<div class="cards"><div class="card">울트라<b>14.6형</b><small>화면 공간</small></div><div class="card">플러스<b>12.6형</b><small>휴대성 함께 고려</small></div></div>'
 if i==2:extra='<div class="cards"><div class="card">울트라<b>692g</b></div><div class="card">플러스<b>553g</b></div></div><div class="badge">Wi-Fi끼리 비교 · 139g 차이</div>'
 if i==3:extra='<div class="cards"><div class="card">모바일 프리미엄<b>4개월</b><small>PC 전체 기능·영구 이용권과 구분</small></div></div>'
 if i==4:extra='<div class="steps"><div class="step">01　내 파일 열기</div><div class="step">02　필요한 편집 적용</div><div class="step">03　원하는 형식으로 내보내기</div></div>'
 if i==5:extra='<div class="cards"><div class="card">책상 작업<b>공간</b></div><div class="card">잦은 이동<b>휴대성</b></div></div>'
 cues=[[(None,'갤럭시 탭 S12'),('큰','큰 화면보다 작업 방식부터')],[(None,'울트라 14.6형'),('플러스는','플러스 12.6형')],[(None,'Wi-Fi 기준 692g · 553g'),('매일','매일 들고 다닐 무게도 확인')],[(None,'모바일 프리미엄 4개월 체험'),('피씨용','PC 전체 기능·영구 이용권 아님')],[(None,'열기 → 편집 → 내보내기'),('키보드는','키보드는 별매')],[(None,'책상 작업은 화면 공간'),('이동이','이동이 많다면 휴대성'),('내','내 작업부터 선택하세요')]][i]
 starts=[]
 for anchor,txt in cues:
  starts.append(next((w['start'] for w in t['words'] if anchor and w['text'].startswith(anchor)),.1))
 caps='';anim=''
 for j,(_,txt) in enumerate(cues):
  st=starts[j];end=starts[j+1] if j+1<len(starts) else dur-.05
  caps+=f'<div class="cap c{j}">{html.escape(txt)}</div>'
  anim+=f"tl.set('.c{j}',{{opacity:1}},{st}).set('.c{j}',{{opacity:0}},{end});"
  srt.append(f'{len(srt)+1}\n{stamp(t["start"]+st)} --> {stamp(t["start"]+end)}\n{txt}\n')
 title=html.escape(o['headline']).replace('\n','<br>')
 text=f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><script src="vendor/gsap.min.js"></script><style>{css}</style></head><body><!-- autoshorts:custom s12-director --><div id="root" data-composition-id="{sid}" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920"><img class="photo" src="{o['image']}"><div class="shade"></div><div class="bar"></div><div class="label">끌어올리는 테크 상식　 /　{(i+1):02} · 06</div><h1 class="title">{title}</h1><div class="note">{o['note']}</div>{extra}<div class="captions">{caps}</div><div class="foot">2026.10.01 공식 발표 기준 · 자료 조사</div></div><script>const tl=gsap.timeline({{paused:true}});tl.to('.photo',{{scale:1.045,duration:{dur},ease:'none'}},0);tl.from('.title',{{y:24,opacity:0,duration:.35}},.05);tl.from('.card,.step,.badge',{{y:35,opacity:0,duration:.45,stagger:.2}},.5);tl.from('.bar',{{scaleX:0,duration:{dur},ease:'none'}},0);{anim}window.__timelines={{'{sid}':tl}};</script></body></html>'''
 (P/'scenes'/f'{sid}.html').write_text(text)
 clips.append(f'<div id="scene-{sid}" class="clip" data-composition-id="{sid}" data-composition-src="scenes/{sid}.html" data-start="{t["start"]}" data-duration="{dur}" data-track-index="0"></div>')
(P/'captions.srt').write_text('\n'.join(srt))
(P/'index.html').write_text(f'''<!doctype html><html><head><meta charset="utf-8"><script src="vendor/gsap.min.js"></script><style>body{{margin:0}}</style></head><body><div id="root" data-composition-id="main" data-start="0" data-duration="{round(elapsed,3)}" data-width="1080" data-height="1920">{''.join(clips)}<audio id="narration" src="audio/narration.mp3" data-start="0" data-duration="{round(elapsed,3)}" data-track-index="1"></audio></div><script>window.__timelines={{main:gsap.timeline({{paused:true}})}};</script></body></html>''')
print(P,elapsed)
