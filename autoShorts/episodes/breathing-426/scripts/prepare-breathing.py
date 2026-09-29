from pathlib import Path
import json,shutil,subprocess,math
root=Path('/Users/jlee/Documents/Dev/source/myNextSeason')
auto=root/'autoShorts';p=auto/'episodes/breathing-426';audio=p/'audio'
manifest=json.loads(Path('/Users/jlee/Documents/ChatGPT/ba/breathing-assets.json').read_text())
for a in manifest['assets']:shutil.copy2(a['file'],p/'media'/a['destination'])
(p/'refs/imagegen-prompts.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
ep=json.loads((p/'episode.json').read_text())
fps=30;cursorFrames=0
phases={'s04':4,'s05':2,'s06':6}
inputs=[];filters=[]
for i,s in enumerate(ep['scenes']):
    # Always derive timing from the original TTS clip, never from a previous padded version.
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(audio/f'{s["id"]}.mp3')]))
    speech=float(probe['format']['duration'])
    duration=phases.get(s['id'],math.ceil((speech+ep['gapSeconds'])*fps)/fps)
    if s['id'] in phases and speech>duration-.15:raise RuntimeError('Cue too long for breathing phase: '+s['id'])
    s['timing'].update({'start':round(cursorFrames/fps,6),'duration':round(duration,6),'speechEnd':round(speech,6)})
    cursorFrames+=round(duration*fps)
    inputs+=['-i',str(audio/f'{s["id"]}.mp3')]
    filters.append(f'[{i}:a]aresample=44100,aformat=channel_layouts=mono,apad,atrim=duration={duration},asetpts=PTS-STARTPTS[a{i}]')
filters.append(''.join(f'[a{i}]' for i in range(len(ep['scenes'])))+f'concat=n={len(ep["scenes"])}:v=0:a=1[voice]')
subprocess.run(['ffmpeg','-y','-loglevel','error',*inputs,'-filter_complex',';'.join(filters),'-map','[voice]','-ar','44100',str(audio/'voice-timed.wav')],check=True)
total=cursorFrames/fps
# Original unobtrusive harmonic sound bed: no external music, no therapeutic-frequency claim.
expression='0.009*sin(2*PI*220*t)+0.004*sin(2*PI*330*t)+0.002*sin(2*PI*440*t)'
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i',f'aevalsrc={expression}:s=44100:d={total}','-af',f'lowpass=f=900,afade=t=in:st=0.12:d=1.0,afade=t=out:st={total-1.1}:d=1.1',str(audio/'ambient-original.wav')],check=True)
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(audio/'voice-timed.wav'),'-i',str(audio/'ambient-original.wav'),'-filter_complex','[0:a][1:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.92[out]','-map','[out]','-ar','44100','-b:a','192k',str(audio/'narration.mp3')],check=True)
(p/'episode.json').write_text(json.dumps(ep,ensure_ascii=False,indent=2)+'\n')
start=next(s['timing']['start'] for s in ep['scenes'] if s['id']=='s04')
report={'fps':fps,'totalFrames':cursorFrames,'duration':total,'guideStart':start,'guideEnd':start+12,'phaseFrames':{'inhale':120,'hold':60,'exhale':180},'audio':'Original Gemini Aoede clips padded to exact frame boundaries; quiet original harmonic bed mixed underneath. No therapy claims about sound.','recognitionNote':'s02 recognized 4/2/6 as digits, explaining lower character match. Sequence and timings match intended spoken script.'}
(p/'refs/timing-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['node','scripts/build-scenes.js','breathing-426'],cwd=auto,check=True)
for name in ['Bold','SemiBold']:shutil.copy2(root/f'flow-pipeline/fonts/Pretendard-{name}.ttf',p/f'vendor/Pretendard-{name}.ttf')
shutil.copy2(__file__,p/'scripts/prepare-breathing.py')
print(json.dumps(report,ensure_ascii=False))
