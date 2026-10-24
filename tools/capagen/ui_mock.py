"""
Mock-ups of the Terrassic UI (docs/IDENTIDADE.md): mirrors client/ui/TerrassicUi.java pixel for pixel at GUI scale 1
and writes, in the current folder, rules_new.png (the Rules screen at 427x240, scaled x3) and palette.png.
Used to review the look without starting the game. usage: python3 ui_mock.py
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','common','src','main','resources','assets','terrassic')+'/'
def c(h): h=h&0xFFFFFFFF; return ((h>>16)&255,(h>>8)&255,h&255,(h>>24)&255)
P=dict(BASALT_950=0xFF0E0B0E,BASALT_900=0xFF141014,BASALT_800=0xFF1C181E,BASALT_700=0xFF2A2329,BASALT_600=0xFF3A3036,BASALT_500=0xFF524550,
STONE_400=0xFF8A7C6A,STONE_300=0xFFB3A48C,STONE_200=0xFFD8CCB2,BONE_100=0xFFEFE6D2,AMBER_700=0xFFB9771C,AMBER_600=0xFFD9952C,AMBER_500=0xFFF2B544,AMBER_300=0xFFFFD27A,
RIFT_500=0xFFF07A1A,DUSK_700=0xFF3A2240,DUSK_500=0xFF5E3866,FERN_400=0xFF7FAF55,BLOOD_500=0xFFC4473A,SKY_400=0xFF8FB4C8,PAPER=0xFFE9DCBC,PAPER_DARK=0xFFD8C79E,LEATHER=0xFF5A3620,INK=0xFF3B2A1A,INK_SOFT=0xFF7A6448)
globals().update({k:v for k,v in P.items()})
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',8)
class G:
    def __init__(s,img): s.img=img; s.d=ImageDraw.Draw(img); s.d.fontmode="1"
    def fill(s,x0,y0,x1,y1,col):
        if x1<=x0 or y1<=y0: return
        col=c(col)
        if col[3]==255: s.d.rectangle([x0,y0,x1-1,y1-1],fill=col)
        else:
            ov=Image.new('RGBA',s.img.size,(0,0,0,0)); ImageDraw.Draw(ov).rectangle([x0,y0,x1-1,y1-1],fill=col); s.img.alpha_composite(ov)
    def text(s,t,x,y,col,shadow=True,center=False):
        w=s.d.textlength(t,font=FONT)
        if center: x=x-w/2
        if shadow: s.d.text((x+1,y),t,font=FONT,fill=(0,0,0,255))
        s.d.text((x,y-1),t,font=FONT,fill=c(col))
def stud(g,x,y): g.fill(x,y,x+3,y+3,AMBER_700); g.fill(x,y,x+2,y+2,AMBER_500); g.fill(x,y,x+1,y+1,AMBER_300)
def slab(g,x0,y0,x1,y1,fill=BASALT_800):
    g.fill(x0,y0,x1,y1,BASALT_950); g.fill(x0+1,y0+1,x1-1,y1-1,fill)
    g.fill(x0+1,y0+1,x1-1,y0+2,BASALT_500); g.fill(x0+1,y0+1,x0+2,y1-1,BASALT_600)
    g.fill(x0+1,y1-2,x1-1,y1-1,BASALT_900); g.fill(x1-2,y0+1,x1-1,y1-1,BASALT_900)
    mid=(x0+x1)//2; g.fill(x0+8,y0+4,mid-6,y0+5,AMBER_700); g.fill(mid+6,y0+4,x1-8,y0+5,AMBER_700); g.fill(mid-2,y0+3,mid+2,y0+6,AMBER_500)
    stud(g,x0+3,y0+3); stud(g,x1-6,y0+3); stud(g,x0+3,y1-6); stud(g,x1-6,y1-6)
def well(g,x0,y0,x1,y1,f=False):
    g.fill(x0,y0,x1,y1,AMBER_600 if f else BASALT_600); g.fill(x0+1,y0+1,x1-1,y1-1,BASALT_900); g.fill(x0+1,y0+1,x1-1,y0+2,BASALT_950); g.fill(x0+1,y0+1,x0+2,y1-1,BASALT_950)
def divider(g,x0,x1,y):
    g.fill(x0,y,x1,y+1,BASALT_950); g.fill(x0,y+1,x1,y+2,BASALT_600); m=(x0+x1)//2; g.fill(m-1,y,m+2,y+2,AMBER_600)
def button(g,x,y,w,h,label,active=True,hot=False,primary=False):
    if not active: face,text=BASALT_700,STONE_400
    elif primary: face,text=(AMBER_500 if hot else AMBER_600),BASALT_900
    else: face,text=(BASALT_600 if hot else BASALT_700),(AMBER_300 if hot else STONE_200)
    g.fill(x,y,x+w,y+h,BASALT_950); g.fill(x+1,y+1,x+w-1,y+h-1,face)
    g.fill(x+1,y+1,x+w-1,y+2,AMBER_300 if primary and active else BASALT_500); g.fill(x+1,y+h-2,x+w-1,y+h-1,AMBER_700 if primary and active else BASALT_900)
    if hot and active and not primary: g.fill(x+1,y+h-2,x+w-1,y+h-1,AMBER_600)
    g.text(label,x+w/2,y+(h-8)//2+1,text,shadow=not primary,center=True)
def tab(g,x,y,w,h,label,sel,hot=False):
    if sel: g.fill(x,y,x+w,y+h,BASALT_700); g.fill(x,y,x+w,y+1,BASALT_500); g.fill(x+2,y+h-2,x+w-2,y+h,AMBER_500)
    elif hot: g.fill(x,y,x+w,y+h,BASALT_700)
    g.text(label,x+w/2,y+(h-8)//2,AMBER_500 if sel else (STONE_200 if hot else STONE_400),center=True)
def slider(g,x,y,w,h,f,df,active=True,hot=False):
    mid=y+h//2; x0=x+4; x1=x+w-4; well(g,x0-1,mid-2,x1+1,mid+3)
    kx=x0+round(f*(x1-x0))
    if kx>x0: g.fill(x0,mid-1,kx,mid+2,AMBER_700); g.fill(x0,mid-1,kx,mid,AMBER_600)
    dx=x0+round(df*(x1-x0)); g.fill(dx,mid+4,dx+1,mid+7,STONE_400)
    col=AMBER_300 if hot else AMBER_500
    g.fill(kx-1,mid-5,kx+2,mid+6,BASALT_950); g.fill(kx-3,mid-3,kx+4,mid+4,BASALT_950); g.fill(kx-2,mid-3,kx+3,mid+4,col); g.fill(kx-1,mid-4,kx+2,mid+5,col); g.fill(kx-1,mid-3,kx,mid,0xFFFFF1C8)
def mark(g,x,y): g.fill(x,y,x+3,y+3,AMBER_500); g.fill(x,y,x+1,y+1,AMBER_300)

W,H=427,240
bg=Image.open(R+'textures/gui/title/background/panorama_0.png').convert('RGBA').resize((W,H)).filter(ImageFilter.GaussianBlur(2))
img=bg.copy(); g=G(img); g.fill(0,0,W,H,0x90100C10)
pw=380; ph=H-32; left=(W-pw)//2; top=16; listTop=top+58; listBottom=top+ph-34; right=left+pw; bottom=top+ph
slab(g,left,top,right,bottom)
g.text("Regras do Terrassic",left+14,top+9,AMBER_500)
g.text("Regras deste mundo",left+14,top+19,STONE_400,shadow=False)
tabs=["Geral","Criação","Ecossistema"]; tw=(pw-24)//3
for i,t in enumerate(tabs): tab(g,left+12+i*tw,top+30,tw-4,18,t,i==0,hot=(i==1))
divider(g,left+12,right-12,listTop-6); divider(g,left+12,right-12,listBottom+3)
rows=[("Nível de dificuldade","0.5",0.5,0.5,False),("Dano dos dinos","1.6",0.31,0.18,True),("Dano do jogador","1.0",0.18,0.18,False),("Dano de estruturas","1.0",0.2,0.2,False),("Resistência do jogador","1.0",0.18,0.18,False)]
y=listTop
for i,(n,v,f,df,ch) in enumerate(rows):
    if y+34>listBottom+4: break
    x=left+14
    g.text(n,x,y+1,STONE_200,shadow=False)
    if ch: mark(g,x+int(g.d.textlength(n,font=FONT))+4,y+3)
    well(g,x,y+12,x+44,y+26,f=(i==1)); g.text(v,x+4,y+16,BONE_100,shadow=False)
    sx=x+56; slider(g,sx,y+12,right-18-sx,14,f,df,hot=(i==1))
    y+=34
g.fill(right-9,listTop,right-6,listBottom,BASALT_900); g.fill(right-9,listTop,right-6,listTop+90,AMBER_700); g.fill(right-9,listTop,right-8,listTop+90,AMBER_500)
bw=(pw-32)//3; by=top+ph-26
button(g,left+12,by,bw,18,"Restaurar padrão"); button(g,left+16+bw,by,bw,18,"Cancelar",hot=True); button(g,left+20+bw*2,by,bw,18,"Salvar",primary=True)
img.resize((W*3,H*3),Image.NEAREST).save('rules_new.png')

# palette sheet
names=["BASALT_950","BASALT_900","BASALT_800","BASALT_700","BASALT_600","BASALT_500","STONE_400","STONE_300","STONE_200","BONE_100","AMBER_700","AMBER_600","AMBER_500","AMBER_300","RIFT_500","DUSK_700","DUSK_500","FERN_400","BLOOD_500","SKY_400","PAPER","PAPER_DARK","LEATHER","INK","INK_SOFT"]
cols=5; sw=150; sh=70
sheet=Image.new('RGBA',(cols*sw+20,((len(names)+cols-1)//cols)*sh+60),c(BASALT_900)); d=ImageDraw.Draw(sheet)
F2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',13); F3=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',11)
d.text((12,14),"Terrassic — paleta Âmbar e Basalto",font=F2,fill=c(AMBER_500))
for i,n in enumerate(names):
    x=10+(i%cols)*sw; y=44+(i//cols)*sh; v=P[n]
    d.rectangle([x,y,x+sw-10,y+40],fill=c(v),outline=c(BASALT_600))
    d.text((x,y+44),n,font=F3,fill=c(STONE_200)); d.text((x+90,y+44),"#%06X"%(v&0xFFFFFF),font=F3,fill=c(STONE_400))
sheet.save('palette.png')
