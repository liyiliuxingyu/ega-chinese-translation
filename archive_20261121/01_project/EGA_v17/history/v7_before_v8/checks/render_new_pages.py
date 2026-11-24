from pathlib import Path
import fitz,json
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[1]
out=root/'checks/rendered'; out.mkdir(exist_ok=True)
book=fitz.open(root/'main.pdf');report=fitz.open(root/'report.pdf')
print('report sections')
for i,p in enumerate(report):
 t=p.get_text()
 if '历史核查记录：第六版' in t or '第七版：19.5' in t:print(i+1,t[:180])
# Main: cover, front matter, all altered old pages, new section and end boundary.
selections={'book':[1,3,4,5]+list(range(270,297)),'audit':list(range(1,31))}
for name,doc in [('book',book),('audit',report)]:
 imgs=[]
 for n in selections[name]:
  page=doc[n-1]; pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
  target=out/f'{name}_{n:03}.png';pix.save(target)
  im=Image.open(target).convert('RGB');im.thumbnail((270,400))
  tile=Image.new('RGB',(290,430),'white');tile.paste(im,((290-im.width)//2,22))
  ImageDraw.Draw(tile).text((10,5),f'{name} PDF {n}',fill='black')
  imgs.append(tile)
 for start in range(0,len(imgs),12):
  batch=imgs[start:start+12];sheet=Image.new('RGB',(290*4,430*3),'#cccccc')
  for j,im in enumerate(batch):sheet.paste(im,((j%4)*290,(j//4)*430))
  sheet.save(out/f'{name}_contact_{start//12+1}.png')
(root/'checks/render_selection.json').write_text(json.dumps(selections,indent=2))
