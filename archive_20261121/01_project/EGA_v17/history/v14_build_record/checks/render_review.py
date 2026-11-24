from pathlib import Path
import fitz
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parents[1]
sets={'book':('main.pdf',list(range(402,419))+[1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]),'report':('report.pdf',list(range(15,25))+[1,3,5])}
for kind,(fn,pages) in sets.items():
 out=R/'checks/final_render'/kind;out.mkdir(parents=True,exist_ok=True)
 d=fitz.open(R/fn)
 for p in pages:
  d[p-1].get_pixmap(matrix=fitz.Matrix(1.75,1.75),alpha=False).save(str(out/f'{p:04d}.png'))
 for j in range(0,len(pages),6):
  sheet=Image.new('RGB',(1260,1860),'#dddddd');draw=ImageDraw.Draw(sheet)
  for q,p in enumerate(pages[j:j+6]):
   im=Image.open(out/f'{p:04d}.png');im.thumbnail((600,570))
   x=(q%2)*630+(630-im.width)//2;y=(q//2)*620+30
   sheet.paste(im,(x,y));draw.text(((q%2)*630+15,(q//2)*620+8),f'{kind} PDF p{p}',fill='black')
  sheet.save(out/f'contact_{j//6+1}.jpg',quality=90)
 print(kind,len(pages),'pages rendered')
