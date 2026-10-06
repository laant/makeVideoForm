from pathlib import Path
import json,subprocess,os,shutil
p=Path('/Users/jlee/Documents/Dev/source/myNextSeason/autoShorts/episodes/google-messages-keep')
ep=json.loads((p/'episode.json').read_text());report=[]
def probe(f):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,r_frame_rate,duration','-of','json',str(f)]))['streams'][0]
for s in ep['scenes']:
    f=p/'renders'/f'{s["id"]}.mp4';expected=round(s['timing']['duration']*30);v=probe(f);before=int(v['nb_frames'])
    if before<expected:raise RuntimeError(f'Insufficient frames: {s["id"]}: {before} < {expected}')
    if before>expected:
        tmp=f.with_name(f.stem+'-exact.mp4')
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(f),'-vf',f'trim=end_frame={expected},setpts=PTS-STARTPTS','-an','-c:v','libx264','-crf','16','-preset','fast','-pix_fmt','yuv420p','-r','30',str(tmp)],check=True)
        os.replace(tmp,f)
    after=probe(f);assert int(after['nb_frames'])==expected
    report.append({'scene':s['id'],'expectedFrames':expected,'beforeFrames':before,'finalFrames':int(after['nb_frames']),'duration':after['duration']})
(p/'refs/frame-verification.json').write_text(json.dumps({'reason':'Normalize sub-millisecond HTML duration rounding from HyperFrames to integer frame slots before assembly.','scenes':report,'totalFrames':sum(x['finalFrames'] for x in report)},indent=2)+'\n')
shutil.copy2(__file__,p/'scripts/normalize-keep.py')
print(json.dumps(report))
