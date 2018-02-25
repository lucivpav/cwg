from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from combine_and_shorten_definition import combine_and_shorten_definition

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
