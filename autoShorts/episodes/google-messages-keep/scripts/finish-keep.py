from pathlib import Path
import subprocess,json,shutil
p=Path('/Users/jlee/Documents/Dev/source/myNextSeason/autoShorts/episodes/google-messages-keep')
def run(a):subprocess.run(a,check=True)
# Keep original narration-only assembly and add original quiet ambient audio with ducking.
shutil.copy2(p/'final.mp4',p/'renders/narration-only.mp4')
run(['ffmpeg','-y','-v','error','-i',str(p/'renders/narration-only.mp4'),'-i',str(p/'audio/ambient-original.wav'),'-filter_complex','[0:a]asplit=2[n][sc];[1:a]volume=0.7[b];[b][sc]sidechaincompress=threshold=0.025:ratio=5:attack=15:release=250[duck];[n][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-18:TP=-2:LRA=9,volume=2dB[a]','-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','44100','-movflags','+faststart',str(p/'final.mp4')])
print('Final mix ready')
