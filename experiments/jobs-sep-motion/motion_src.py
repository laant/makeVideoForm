from PIL import Image, ImageDraw, ImageFont, ImageFilter
from functools import lru_cache
import numpy as np,subprocess,os,sys,json,math
R=os.path.dirname(__file__);W,H=1080,1920;FPS=30
BG='#0B1422';FG='#F5F7FB';MUT='#A5B2C5';LINE='#253447';YELLOW='#F4C76B';RED='#FF8A70';TEAL='#68DACB';BLUE='#93BFFF'
REG='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';BOLD='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def ease(x):x=max(0,min(1,x));return 1-(1-x)**3
def prog(t,delay=0,dur=.6):return ease((t-delay)/dur)
@lru_cache(None)
def font(s,b):return ImageFont.truetype(BOLD if b else REG,s,index=1)
@lru_cache(None)
def glyph(s,size,c,b):
 f=font(size,b);box=f.getbbox(s);im=Image.new('RGBA',(int(f.getlength(s))+8,size*2),(0,0,0,0));d=ImageDraw.Draw(im);d.text((0,0),s,font=f,fill=c);return im.crop((0,0,im.width,box[3]+3))
def txt(im,x,y,s,size=48,c=FG,b=False,t=10,delay=0,dur=.65,dx=0,dy=36,scale=False):
 p=prog(t,delay,dur)
 if p<=0:return
 a=glyph(s,size,c,b)
 if scale and p<1:
  k=.86+.14*p;a=a.resize((round(a.width*k),round(a.height*k)),Image.Resampling.LANCZOS)
 if p<1:a=a.copy();a.putalpha(a.getchannel('A').point(lambda v:int(v*p)))
 im.paste(a,(int(x+dx*(1-p)),int(y+dy*(1-p))),a)
def card(im,box,col,t,delay=0):
 p=prog(t,delay,.65)
 if p<=0:return
 x,y,x2,y2=box;y+=int(38*(1-p));y2+=int(38*(1-p))
 layer=Image.new('RGBA',(x2-x+40,y2-y+40));d=ImageDraw.Draw(layer)
 d.rounded_rectangle((10,16,x2-x+22,y2-y+22),24,fill=(0,0,0,75));d.rounded_rectangle((0,0,x2-x,y2-y),24,fill=col)
 if p<1:layer.putalpha(layer.getchannel('A').point(lambda v:int(v*p)))
 im.paste(layer,(x,y),layer)
@lru_cache(None)
def bg(n):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);c=[BLUE,YELLOW,RED,TEAL,BLUE][n-1]
 d.rectangle((0,0,16,H),fill=c)
 for x in range(90,916,55):d.line((x,450,x,1480),fill='#0E1929',width=1)
 for y in range(450,1480,55):d.line((90,y,915,y),fill='#0E1929',width=1)
 txt(im,90,185,'미국 고용보고서',34,MUT);txt(im,90,238,'2026년 9월',42,FG,True);txt(im,830,240,f'0{n} / 05',29,MUT)
 d.line((90,330,915,330),fill=LINE,width=2)
 txt(im,90,382,['36초 핵심 요약','01  일자리 증가','02  이전 두 달 수정','03  시간당 평균임금','종합 의견'][n-1],34,c,True)
 d.line((90,1510,915,1510),fill=LINE,width=2);txt(im,90,1540,'출처: BLS · 2026.10.02 발표',28,MUT);txt(im,90,1585,'발표값 기준 · 향후 수정 가능',28,MUT)
 return im

def frame(n,t):
 im=bg(n).copy();d=ImageDraw.Draw(im);c=[BLUE,YELLOW,RED,TEAL,BLUE][n-1]
 # five-segment progress system and an eased accent rule
 durations=[5,8,8,8,7]
 for i in range(5):
  x=90+i*167;d.rounded_rectangle((x,1700,x+145,1707),3,fill=LINE)
  frac=1 if i<n-1 else max(0,min(1,t/durations[n-1])) if i==n-1 else 0
  if frac>0:d.rounded_rectangle((x,1700,x+max(3,int(145*frac)),1707),3,fill=c)
 if n==1:
  txt(im,90,485,'미국 고용,',88,FG,True,t,.1,dy=75)
  txt(im,90,600,'무엇이 달라졌나',80,FG,True,t,.4,dx=-55,dy=0)
  txt(im,90,766,'숫자 3개로 쉽게 보기',48,MUT,t=t,delay=.85)
  for j,(y,col,num,label) in enumerate([(945,YELLOW,'01','일자리 증가'),(1110,RED,'02','이전 수치 수정'),(1275,TEAL,'03','임금 상승률')]):
   st=1.05+j*.4;card(im,(90,y,915,y+132),'#152337',t,st);txt(im,124,y+30,num,46,col,True,t,st+.05);txt(im,235,y+30,label,47,FG,True,t,st+.18,dx=35,dy=0)
 elif n==2:
  txt(im,90,480,'+2.9만',156,YELLOW,True,t,.15,scale=True);txt(im,690,571,'개',56,YELLOW,True,t,.3)
  txt(im,90,698,'9월 비농업 일자리 · 전월 대비',40,MUT,t=t,delay=.4)
  card(im,(90,803,915,904),'#342D20',t,2.6);txt(im,120,823,'주의 · 고용 증가 둔화',47,YELLOW,True,t,2.8)
  for y,delay,width,color,label,value in [(1015,.6,665,'#56718C','8월 수정값','+13.3만'),(1220,1.45,145,YELLOW,'9월 발표값','+2.9만')]:
   txt(im,90,y,label,36,MUT,t=t,delay=delay);p=prog(t,delay+.15,1.05)
   if p>0:d.rounded_rectangle((90,y+65,90+max(8,int(width*p)),y+123),8,fill=color)
   txt(im,90+width+20,y+60,value,30 if width>200 else 34,MUT if width>200 else YELLOW,True,t,delay+.25,dy=0)
  txt(im,90,1413,'늘긴 했지만, 증가 폭은 작아졌어요',37,FG,t=t,delay=3.1)
 elif n==3:
  txt(im,90,480,'−6만',156,RED,True,t,2.35,scale=True);txt(im,590,571,'개',56,RED,True,t,2.5)
  txt(im,90,698,'7·8월 고용 증감 합계 하향 수정',39,MUT,t=t,delay=2.55)
  card(im,(90,803,915,904),'#36251F',t,3);txt(im,120,823,'부정적 · 고용 흐름 약화',46,RED,True,t,3.15)
  for y,st,month,before,after in [(1010,.2,'7월','+2.1만','−1만'),(1160,.65,'8월','+16.2만','+13.3만')]:
   txt(im,90,y,month,43,FG,True,t,st);txt(im,285,y,before,44,MUT,True,t,st+.15)
   txt(im,533,y,'→',45,RED,True,t,st+.7,dx=-30,dy=0);txt(im,635,y,after,44,FG,True,t,st+1.1,dx=45,dy=0)
   p=prog(t,st+.95,.5)
   if p>0:d.line((285,y+67,285+int((195 if month=='8월' else 170)*p),y+67),fill=RED,width=3)
  d.line((90,1275,915,1275),fill=LINE,width=2)
  txt(im,90,1330,'과거 발표치를 고친 숫자예요',40,FG,t=t,delay=3.5)
  txt(im,90,1402,'9월에 6만 명이 해고됐다는 뜻은 아니에요',33,MUT,t=t,delay=3.8)
 elif n==4:
  txt(im,90,480,'+0.1%',156,TEAL,True,t,.15,scale=True)
  txt(im,90,698,'9월 임금 상승률 · 전월 대비',41,MUT,t=t,delay=.45)
  card(im,(90,803,915,941),'#18332F',t,1.1);txt(im,120,819,'긍정적',44,TEAL,True,t,1.3);txt(im,120,880,'물가 압력 완화 관점',37,TEAL,True,t,1.7)
  txt(im,90,1030,'임금은 완만하게 올랐어요',48,FG,True,t,2.3)
  txt(im,90,1150,'임금발 물가 압력에는',43,FG,t=t,delay=2.8);txt(im,90,1220,'안도할 수 있는 숫자',43,FG,t=t,delay=3.15)
  p=prog(t,3.5);d.line((90,1335,90+int(825*p),1335),fill=LINE,width=2)
  txt(im,90,1380,'물가 상승률 자체를 측정한 수치는 아니에요',33,MUT,t=t,delay=3.65)
 else:
  txt(im,90,495,'고용 흐름은',80,FG,True,t,.1,dx=-55,dy=0);txt(im,90,610,'약해졌어요',92,YELLOW,True,t,.5,scale=True)
  card(im,(90,819,915,1166),'#152337',t,1.1)
  txt(im,124,865,'하지만 이것만으로',47,FG,True,t,1.35)
  txt(im,124,955,'금리 인하·주가 상승',50,FG,True,t,1.7,dx=40,dy=0)
  txt(im,124,1050,'단정은 어려워요',50,BLUE,True,t,2.1,dx=-35,dy=0)
  txt(im,90,1250,'다음 물가·고용 지표까지 확인',45,FG,True,t,2.6)
  txt(im,90,1370,'색상 평가는 각 지표의 해석 관점입니다',32,MUT,t=t,delay=2.9)
  txt(im,90,1420,'주식 매수 신호가 아닙니다',32,MUT,t=t,delay=3.1)
 # thin color swipe confined to the left gutter, never crosses the text
 if t<.6:
  p=prog(t,0,.6);d.rectangle((16,int(-300+2200*p),28,int(-40+2200*p)),fill=c)
 return im

def render(filename,segments,audio=True):
 total=sum(b-a for n,a,b in segments)
 temp=R+'/output/'+filename+'-silent.mp4'
 cmd=['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-threads','4','-pix_fmt','yuv420p',temp]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for n,a,b in segments:
  for i in range(round((b-a)*FPS)):p.stdin.write(frame(n,a+i/FPS).tobytes())
 p.stdin.close()
 if p.wait()!=0:raise RuntimeError('Encode failed')
 out=R+'/output/'+filename+'.mp4'
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-i',temp,'-i',R+'/music-original.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','128k','-t',str(total),'-movflags','+faststart',out],check=True)
 return out
if __name__=='__main__':
 mode=sys.argv[1] if len(sys.argv)>1 else 'preview'
 if mode=='preview':
  for n,t in [(2,.9),(2,3.5),(3,4.5),(4,4.5),(5,4.5)]:frame(n,t).save(f'{R}/preview/scene-{n}-{t}.png')
  sheet=Image.new('RGB',(1440,640))
  for i,(n,t) in enumerate([(2,.9),(2,3.5),(3,4.5),(5,4.5)]):sheet.paste(frame(n,t).resize((360,640)),(i*360,0))
  sheet.save(R+'/preview/motion-contact.jpg',quality=95)
  print(render('motion-sample-10s',[(2,0,5),(3,0,5)]))
 elif mode=='full':print(render('2026-09-us-jobs-motion-v2',[(1,0,5),(2,0,8),(3,0,8),(4,0,8),(5,0,7)]))
