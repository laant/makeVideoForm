from pathlib import Path
import json,subprocess,math,shutil
r=Path('/Users/jlee/Documents/Dev/source/myNextSeason');a=r/'autoShorts';p=a/'episodes/postmeal-walk';e=json.loads((p/'episode.json').read_text());inputs=[];filters=[];frames=0
for i,s in enumerate(e['scenes']):
 f=p/'audio'/f'{s["id"]}.mp3';speech=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(f)]))['format']['duration']);n=math.ceil((speech+.3)*30);d=n/30
 s['timing'].update(start=round(frames/30,6),duration=round(d,6),speechEnd=speech+(.06 if i==0 else 0));frames+=n
 if i==0:s['timing']['words']=[{**w,'start':round(w['start']+.06,4),'end':round(w['end']+.06,4)} for w in json.loads((p/'audio/s01.json').read_text())['words']]
 inputs+=['-i',str(f)];delay='adelay=60:all=1,' if i==0 else '';filters.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=mono,{delay}apad,atrim=duration={d},asetpts=PTS-STARTPTS[a{i}]')
filters.append(''.join(f'[a{i}]' for i in range(len(e['scenes'])))+f'concat=n={len(e["scenes"])}:v=0:a=1[out]')
subprocess.run(['ffmpeg','-y','-v','error',*inputs,'-filter_complex',';'.join(filters),'-map','[out]','-ar','44100','-b:a','192k',str(p/'audio/narration.mp3')],check=True)
(p/'episode.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['node','scripts/build-scenes.js','postmeal-walk'],cwd=a,check=True)
for name in ['Bold','SemiBold']:shutil.copy2(r/f'flow-pipeline/fonts/Pretendard-{name}.ttf',p/f'vendor/Pretendard-{name}.ttf')
(p/'refs/timing-manifest.json').write_text(json.dumps({'fps':30,'frames':frames,'duration':frames/30},indent=2))
shutil.copy2(__file__,p/'scripts/prepare-walk.py');print('Duration',frames/30)
