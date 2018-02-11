from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from combine_and_shorten_definition import combine_and_shorten_definition

# TODO: rename file to sth like draw.py

#TODO: remove
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter, A4

# centers the text to ymid
def draw_vertical_text(canvas, font_name, font_size, xto, ymid, text):
    tw = stringWidth(text, font_name, font_size);
    canvas.setFont(font_name, font_size);
    canvas.saveState();
    canvas.translate(xto, ymid - tw/2);
    canvas.rotate(90);
    canvas.drawString(0, 0, text);
    canvas.restoreState();

def draw_full_summation_curve(canvas, xfrom, yfrom, xto, yto):
    # assuming xfrom<xto and yfrom<yto
    curve = __get_closed_summation_curve(xfrom, yfrom, xto, yto);
    __draw_summation_curve(canvas, curve);

def draw_top_summation_curve(canvas, xfrom, yfrom, xto, yto):
    # assuming xfrom<xto and yfrom<yto
    curve = __get_opened_summation_curve(xfrom, yto, xto, yfrom);
    __draw_summation_curve(canvas, curve);

def draw_bottom_summation_curve(canvas, xfrom, yfrom, xto, yto):
    # assuming xfrom<xto and yfrom<yto
    curve = __get_opened_summation_curve(xfrom, yfrom, xto, yto);
    __draw_summation_curve(canvas, curve);

def draw_opened_top_summation_curve(canvas, xfrom, yfrom, xto, yto):
    # assuming xfrom<xto and yfrom<yto
    w = xto-xfrom;
    curve = [__get_opened_curve(xto, yto, xfrom+w/2, yfrom)];
    __draw_summation_curve(canvas, curve);

def __draw_summation_curve(canvas, curve):
    for subcurve in curve:
        canvas.bezier(*subcurve);

def __get_closed_summation_curve(xfrom, yfrom, xto, yto):
    curve = list();
    ymid = (yfrom+yto)/2;
    curve.append(__get_closed_curve(xfrom, ymid, xto, yto));
    curve.append(__get_closed_curve(xfrom, ymid, xto, yfrom));
    return curve;

def __get_opened_summation_curve(xfrom, yfrom, xto, yto):
    curve = list();
    xmid = (xfrom+xto)/2;
    ymid = (yfrom+yto)/2;
    curve.append(__get_closed_curve(xfrom, ymid, xto, yfrom));
    curve.append(__get_opened_curve(xfrom, ymid, xmid, yto));
    return curve;

def __get_closed_curve(xfrom, yfrom, xto, yto):
    return [xfrom,yfrom, xto,yfrom, xfrom,yto, xto,yto];

def __get_opened_curve(xfrom, yfrom, xto, yto):
    ymid = (yfrom+yto)/2;
    return [xfrom,yfrom, xto,yfrom, xto,ymid, xto,yto];

# TODO: delete
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
