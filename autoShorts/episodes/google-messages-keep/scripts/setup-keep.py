from pathlib import Path
import json,shutil
r=Path('/Users/jlee/Documents/Dev/source/myNextSeason');p=r/'autoShorts/episodes/google-messages-keep';src=Path('/Users/jlee/Documents/ChatGPT/ba/output/google-messages-keep')
for d in ['refs','media','scripts']: (p/d).mkdir(parents=True,exist_ok=True)
e=json.loads((r/'autoShorts/episodes/postmeal-walk/episode.json').read_text())
e.update(slug='google-messages-keep',topic='같이 쓰는 장보기 메모',audience='Android 생활 기능에 관심 있는 시청자',tone='친근한 한국어 구어체',cta='내 앱에서 Keep 메모 확인',theme={'bg':'#faf4e8','fg':'#102849','accent':'#efbd35','muted':'#68707a'},gapSeconds=.3,transitionSeconds=0)
e['voice'].update(prompt='',provider='gemini',modelId='gemini-3.1-flash-tts-preview',voiceId='Aoede')
e['reference']={'url':'https://pulluptech.blogspot.com/2026/10/google-messages-keep-notes.html','notes':'대본·프롬프트 사용자 승인 2026-10-05'}
e['brief']={'goal':'커플의 장보기 상황으로 공유 메모와 권한을 설명','lengthSec':45,'visual':'첫 이미지 커플 일관성, B안','avoid':'가짜 앱 화면, 자동 구매 추적, 전체 배포 완료 주장'}
texts=['장보기 메시지, 이제 같은 목록에서 확인하세요.','구글 메시지 대화에서 추가, 킵 메모를 눌러 목록을 보내면 돼요.','우유를 샀다면 직접 체크. 상대도 바뀐 목록을 볼 수 있어요.','수정이 안 되면, 메모 주인에게 권한을 요청하세요.','그런데 단체방을 나가도, 공유 메모는 계속 볼 수 있어요.','공유를 끝내려면 킵에서 공동작업자를 확인하고, 제외할 사람을 삭제한 뒤 저장하세요.','내 대화창에 킵 메모가 있는지, 먼저 확인해 보세요.']
e['scenes']=[dict(id=f's{i+1:02}',template='title',narration=t,onScreen={'title':'같이 쓰는 장보기 메모','showCaptions':False},sfx=[],transitionOut='cut',effects=[]) for i,t in enumerate(texts)]
e['caption']='Google 메시지에서 Keep 메모로 장보기 목록을 함께 확인하세요. Android 기준이며 내 앱에 메뉴가 있는지 먼저 확인하세요. 수정 권한을 요청해야 할 수 있습니다. 단체방을 나간 뒤에도 공유 메모 접근은 남으므로 Keep의 공동작업자를 확인하세요.\n원문: https://pulluptech.blogspot.com/2026/10/google-messages-keep-notes.html\n공식 안내: https://support.google.com/keep/answer/18080385?hl=ko\n공유 관리: https://support.google.com/keep/answer/6101196?hl=ko\nAI 이미지·음성 사용. 화면은 설명용 개념도이며 실제 앱 UI나 실사용 후기가 아닙니다.'
e['hashtags']=['#구글메시지','#구글킵','#장보기','#공유메모','#안드로이드','#테크팁','#쇼츠'];e['upload']={'title':'장보기 목록 같이 쓰기, 단체방을 나가도 남는 것','channel':'tech','youtube':False,'instagram':False};e['cards']={'footer':'Google 메시지 × Keep · 사용 전 권한 확인'}
(p/'episode.json').write_text(json.dumps(e,ensure_ascii=False,indent=2))
shutil.copy2(src/'treatment.md',p/'refs/treatment-approved.md');shutil.copy2(src/'refs/couple-cover.webp',p/'media/cover.webp')
ids=['68aa34eb-0dcb-4e33-bd47-90faeb33d653','99c483f9-20b2-4b8f-9759-e87fafdb96d8','687e188d-6e53-4dae-b556-d3741b57f5a1','384ac6e7-599f-40b2-a536-6da897383fce','519dd5b3-9f72-4ad4-91a8-4db1c1f83a47']
for name,id in zip(['couple','woman','man','permissions','end'],ids):shutil.copy2(Path('/Users/jlee/.codex/generated_images/01a0ebac-aac9-7e70-9377-62ab4ec1199e')/f'exec-{id}.png',p/f'media/{name}.png')
print(p)
