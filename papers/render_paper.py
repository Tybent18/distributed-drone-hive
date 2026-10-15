"""Reproducible PDF renderer for the Markdown manuscript."""
from pathlib import Path
from html import escape
import re
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle

root=Path(__file__).resolve().parent
text=(root/'DRONE_HIVE_RESEARCH_MANUSCRIPT.md').read_text(encoding='utf-8')
blue=colors.HexColor('#17344b')
ss=getSampleStyleSheet()
st={
 'title':ParagraphStyle('ManuscriptTitle',parent=ss['Title'],fontName='Helvetica-Bold',fontSize=18,leading=22,textColor=blue,spaceAfter=16),
 'h2':ParagraphStyle('PaperH2',parent=ss['Heading2'],fontSize=12,leading=16,textColor=blue,spaceBefore=13,spaceAfter=7),
 'h3':ParagraphStyle('PaperH3',parent=ss['Heading3'],fontSize=10,leading=13,textColor=blue,spaceBefore=10,spaceAfter=5),
 'body':ParagraphStyle('PaperBody',parent=ss['BodyText'],fontSize=9,leading=13,spaceAfter=8),
 'bullet':ParagraphStyle('PaperBullet',parent=ss['BodyText'],fontSize=8.8,leading=12,leftIndent=14,firstLineIndent=-8,spaceAfter=4),
 'cell':ParagraphStyle('PaperCell',parent=ss['BodyText'],fontSize=7.5,leading=10),
}
def formatted(value):
 value=escape(value).replace('—',' - ').replace('↔',' to ')
 value=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',value)
 value=re.sub(r'\*([^*]+)\*',r'<i>\1</i>',value)
 return value
lines=text.splitlines()
story=[]
i=0
while i<len(lines):
 line=lines[i].strip()
 if not line:
  i+=1;continue
 if line.startswith('|'):
  raw=[]
  while i<len(lines) and lines[i].strip().startswith('|'):
   values=[z.strip() for z in lines[i].strip().strip('|').split('|')]
   if not all(re.fullmatch(r'[-: ]+',z) for z in values):
    raw.append([Paragraph(formatted(z),st['cell']) for z in values])
   i+=1
  if raw:
   t=LongTable(raw,colWidths=[490/len(raw[0])]*len(raw[0]),repeatRows=1)
   t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DDEBF3')),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#D0DFE8')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
   story.append(t);story.append(Spacer(1,9))
  continue
 if line.startswith('# '):story.append(Paragraph(formatted(line[2:]),st['title']))
 elif line.startswith('## '):story.append(Paragraph(formatted(line[3:]),st['h2']))
 elif line.startswith('### '):story.append(Paragraph(formatted(line[4:]),st['h3']))
 elif line.startswith('- '):story.append(Paragraph('&#8226; '+formatted(line[2:]),st['bullet']))
 else:
  group=[line]
  while i+1<len(lines) and lines[i+1].strip() and not lines[i+1].startswith(('#','|','- ')):
   i+=1;group.append(lines[i].strip())
  story.append(Paragraph(formatted(' '.join(group)),st['body']))
 i+=1
out=root/'Drone_Hive_Formal_Research_Paper.pdf'
doc=SimpleDocTemplate(str(out),pagesize=(612,792),leftMargin=60,rightMargin=60,topMargin=61,bottomMargin=56,title='Drone Hive Research Preprint',author='Drone Hive — authorship pending')
def footer(c,d):
 c.saveState();c.setStrokeColor(colors.HexColor('#A8C6D7'));c.line(60,746,552,746)
 c.setFont('Helvetica',7);c.setFillColor(blue);c.drawString(60,754,'DRONE HIVE  /  DRAFT RESEARCH MANUSCRIPT')
 c.drawString(60,34,'Software simulation only — not peer reviewed');c.drawRightString(552,34,str(d.page));c.restoreState()
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('Rendered',out)
