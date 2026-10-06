import wave,math,array,json
from pathlib import Path
p=Path('/Users/jlee/Documents/Dev/source/myNextSeason/autoShorts/episodes/google-messages-keep');e=json.loads((p/'episode.json').read_text());dur=sum(s['timing']['duration'] for s in e['scenes']);sr=22050
# Original unmetered ambient chord bed: no external recordings or licensed samples.
chords=[[130.81,164.81,196],[110,130.81,164.81],[87.31,110,130.81],[98,123.47,146.83]]
a=array.array('h')
for i in range(int(sr*dur)):
 t=i/sr;v=0
 for k,ch in enumerate(chords):
  phase=(t/8-k)%4;env=max(0,1-abs(phase-0.5)/0.7) if phase<1.2 else 0
  for f in ch:v+=env*(math.sin(2*math.pi*f*t)+.25*math.sin(4*math.pi*f*t))/12
 fade=min(1,t/2,(dur-t)/2);a.append(int(max(-1,min(1,v*.19*fade))*32767))
with wave.open(str(p/'audio/ambient-original.wav'),'wb') as w:w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes(a.tobytes())
(p/'refs/audio-design.json').write_text(json.dumps({'music':'Original algorithmically synthesized ambient chord bed; no third-party samples','beatSync':'Not applicable: unmetered ambient bed. Narration word sync takes priority.','visualRender':'Illustration-led HyperFrames, standard rendering; not full-frame code-motion category.'},indent=2))
