from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from combine_and_shorten_definition import combine_and_shorten_definition

#TODO: remove
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter, A4

# definition: list of translations (strings)
def draw_word_definition(canvas, font_name, font_size, xfrom, yfrom, xto, yto, definition):
    # assuming xfrom<xto, yfrom<yto

    # draw summation symbol
    text_height = 7;
    offset = 2;
    xmid = xfrom+text_height+offset;
    ymid = (yfrom+yto)/2;
    
    x1 = xmid;
    y1 = ymid;
    x2 = xto;
    y2 = ymid;
    x3 = xmid;
    y3 = yto;
    x4 = xto;
    y4 = yto;
    canvas.bezier(x1,y1, x2,y2, x3,y3, x4,y4);

    y2 = y2-2*(y2-ymid);
    y3 = y3-2*(y3-ymid);
    y4 = y4-2*(y4-ymid);
    canvas.bezier(x1,y1, x2,y2, x3,y3, x4,y4);

    # draw definition
    canvas.setFont(font_name, font_size);
    canvas.saveState();
    canvas.translate((xfrom+text_height), yfrom);
    canvas.rotate(90);
    w = yto - yfrom;
    text = combine_and_shorten_definition(definition, ', ', w, font_name, font_size)
    tw = stringWidth(text, font_name, font_size);
    canvas.drawString(w/2 - tw/2, 0, text);
    canvas.restoreState();

font_name = 'DejaVuSans'
c = canvas.Canvas('test.pdf', A4);
pdfmetrics.registerFont(TTFont(font_name, font_name + '.ttf'));
draw_word_definition(c, font_name, 13, 10,500,30,700, ['work' , 'transaction (as in a computer database']);
c.showPage();
c.save();
