from pathlib import Path
import json,subprocess,shutil
r=Path('/Users/jlee/Documents/Dev/source/myNextSeason');p=r/'autoShorts/episodes/google-messages-keep';out=r/'output/28-google-messages-keep';out.mkdir(parents=True,exist_ok=True)
e=json.loads((p/'episode.json').read_text())
shutil.copy2(p/'final.mp4',out/'codex_final_send.mp4')
for n,t in [(1,2.7),(2,e['scenes'][4]['timing']['start']+3.8)]:subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(p/'final.mp4'),'-frames:v','1','-q:v','2',str(out/f'codex_final_send_thumb{n}.jpg')],check=True)
shutil.copytree(p/'cards',out/'cards',dirs_exist_ok=True)
shutil.copy2('/Users/jlee/Documents/ChatGPT/ba/output/google-messages-keep/refs/image-prompts.json',p/'refs/image-prompts.json')
shutil.copy2(p/'refs/treatment-approved.md',out/'treatment.md')
groups=[['3단계로 같이 쓰는 장보기 메모','장보기 목록 하나, 두 사람이 함께 확인','Google Keep 공유 전 확인할 2가지','메시지에서 목록 공유까지 3단계','장보기와 공유 권한, 39초로 정리'],['우유 샀어? 이제 같은 목록에서 확인할까?','단체방을 나가면 공유 메모도 끊길까?','구글 메시지에 Keep 메모가 보이나요?','같이 쓰는 메모, 누가 수정할 수 있을까?','장보기 목록을 메시지에서 함께 쓰려면?'],['장보기 목록 같이 쓰기, 단체방을 나가도 남는 것','우유 샀냐는 메시지 대신, 같은 목록','단체방 나갔다고 공유가 끝난 건 아니에요','장보기는 편하게, 공유 권한은 꼼꼼하게','같이 쓰는 메모의 편리함과 놓치기 쉬운 설정']]
text='★ 바이럴 1순위: '+groups[2][0]+'\n이유: 생활 활용과 접근 권한의 반전을 함께 전달.\n차점: '+groups[1][1]+'\n\n'
for label,items in zip(['숫자 포함형','질문형','감정 자극형'],groups):text+=label+'\n'+'\n'.join(f'{i+1}. {s}' for i,s in enumerate(items))+'\n\n'
text+='설명\n'+e['caption']+'\n'+' '.join(e['hashtags'])+'\n';(out/'titles.txt').write_text(text)
manifest={'duration':sum(s['timing']['duration'] for s in e['scenes']),'resolution':'1080x1920','fps':30,'source':e['reference']['url'],'referenceImage':'User-selected first blog illustration, marked AI-generated in source','generatedImages':'builtin image_gen, five identity-referenced variants','narration':e['voice'],'music':'Original procedural ambient, no third-party recording','publishing':'Not uploaded; current request is production only'}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));(p/'refs/asset-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
for f in ['finish-keep.py','deliver-keep.py','keep-music.py','keep-extras.cjs','qa-keep.cjs']:shutil.copy2(Path('/Users/jlee/Documents/ChatGPT/ba')/f,p/'scripts'/f)
f=r/'scripts/collect_outputs.py';s=f.read_text();line='    ("28-google-messages-keep", "codex"): ["autoShorts/episodes/google-messages-keep/final.mp4"],\n'
if line not in s:s=s.replace('MAPPING: dict[tuple[str, str], list[str]] = {\n','MAPPING: dict[tuple[str, str], list[str]] = {\n'+line)
# Preserve all existing entries and register companion cards.
import re
if '"28-google-messages-keep":' not in s:s=re.sub(r'(CARDS[^\n]*= \{\n)',r'\1    "28-google-messages-keep": "autoShorts/episodes/google-messages-keep/cards",\n',s,count=1)
f.write_text(s)
print(out)
