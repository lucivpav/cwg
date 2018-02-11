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

    offset = 2;
    text_height = 7;
    xstart = xfrom+text_height+offset;

    curve = get_closed_summation_curve(xstart, yfrom, xto, yto);
    draw_summation_curve(canvas, curve);

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

def draw_summation_curve(canvas, curve):
    for subcurve in curve:
        canvas.bezier(*subcurve);

def get_closed_summation_curve(xfrom, yfrom, xto, yto):
    curve = list();
    ymid = (yfrom+yto)/2;
    curve.append(get_closed_curve(xfrom, ymid, xto, yto));
    curve.append(get_closed_curve(xfrom, ymid, xto, yfrom));
    return curve;

def get_opened_summation_curve(xfrom, yfrom, xto, yto):
    curve = list();
    xmid = (xfrom+xto)/2;
    ymid = (yfrom+yto)/2;
    curve.append(get_closed_curve(xfrom, ymid, xto, yfrom));
    curve.append(get_opened_curve(xfrom, ymid, xmid, yto));
    return curve;

def get_closed_curve(xfrom, yfrom, xto, yto):
    return [xfrom,yfrom, xto,yfrom, xfrom,yto, xto,yto];

def get_opened_curve(xfrom, yfrom, xto, yto):
    ymid = (yfrom+yto)/2;
    return [xfrom,yfrom, xto,yfrom, xto,ymid, xto,yto];

def summation_curve_demo(canvas):
    xfrom = 200;
    yfrom = 500;
    w = 20;
    h = 200;
    # full
    curve = get_closed_summation_curve(xfrom, yfrom, xfrom+w, yfrom+h);
    draw_summation_curve(canvas, curve);

    xfrom = xfrom + 30;
    ymid = yfrom+h/2;
    # buttom
    curve = get_opened_summation_curve(xfrom, yfrom, xfrom+w, ymid);
    draw_summation_curve(canvas, curve);

    # top
    curve = get_opened_summation_curve(xfrom, yfrom+h+1, xfrom+w, ymid+1);
    draw_summation_curve(canvas, curve);

    xfrom = xfrom + 30;
    # buttom
    curve = get_opened_summation_curve(xfrom, yfrom, xfrom+w, ymid);
    draw_summation_curve(canvas, curve);
    # opened top
    curve = [get_opened_curve(xfrom+w, yfrom+h+1, xfrom+w/2, ymid+1)];
    draw_summation_curve(canvas, curve);
    

#font_name = 'DejaVuSans'
#c = canvas.Canvas('test.pdf', A4);
#pdfmetrics.registerFont(TTFont(font_name, font_name + '.ttf'));
#draw_word_definition(c, font_name, 13, 10,500,30,700, ['work' , 'transaction (as in a computer database']);
#summation_curve_demo(c);
#c.showPage();
#c.save();
