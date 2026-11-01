import glob,os,sys
from PIL import Image,ImageDraw
d=sys.argv[1];fs=sorted(glob.glob(d+'/*.png'))
W,H=520,int(520*720/1280)
n=0
for i in range(0,len(fs),9):
    S=Image.new('RGB',(W*3+8,(H+4)*3),'#222')
    for k,f in enumerate(fs[i:i+9]):
        im=Image.open(f).convert('RGB').crop((12,8,1268,712)).resize((W,H),Image.LANCZOS)
        S.paste(im,((2-k%3)*(W+4),(k//3)*(H+4)))
        ImageDraw.Draw(S).text(((2-k%3)*(W+4)+4,(k//3)*(H+4)+2),os.path.basename(f)[:-4],fill='red')
    S.save(f'{d}/sheet{n:02d}.jpg',quality=88);n+=1
print(n)
