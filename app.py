from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)

def create_image_with_text(text1, text2, spacing, bg_image_path, font_path, font_size=40):
    image = Image.open(bg_image_path)
    draw = ImageDraw.Draw(image)
    try:
        font1 = ImageFont.truetype(font_path, font_size)
    except IOError:
        font1 = ImageFont.load_default()
    try:
        font2 = ImageFont.truetype(font_path, font_size - 10)
    except IOError:
        font2 = ImageFont.load_default()

    def wrap_text(text, draw, font, max_width):
        lines = []
        for paragraph in text.split('\n'):
            words = paragraph.split()
            while words:
                line = ''
                while words and (draw.textsize(line + words[0], font=font)[0] <= max_width):
                    line = line + (words.pop(0) + ' ')
                lines.append(line)
        return lines

    max_width = image.size[0] - 40
    lines1 = wrap_text(text1, draw, font1, max_width)
    lines2 = wrap_text(text2, draw, font2, max_width)
    text1_height = sum([draw.textsize(line, font=font1)[1] + 5 for line in lines1])
    text2_height = sum([draw.textsize(line, font=font2)[1] for line in lines2])
    total_height = text1_height + text2_height + spacing
    y = (image.size[1] - total_height) / 2
    for line in lines1:
        text_width, line_height = draw.textsize(line, font=font1)
        x = (image.size[0] - text_width) / 2
        draw.text((x, y), line, fill="black", font=font1)
        y += line_height + 10
    y += spacing
    for line in lines2:
        text_width, line_height = draw.textsize(line, font=font2)
        x = (image.size[0] - text_width) / 2
        draw.text((x, y), line, fill="black", font=font2)
        y += line_height
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text1 = request.form['text1']
        text2 = request.form['text2']
        spacing = int(request.form['spacing'])
        bg_image = request.files['bg_image']
        bg_image_path = 'background.jpg'
        bg_image.save(bg_image_path)
        font_path = 'NanumBarunGothicBold.ttf'
        img_byte_arr = create_image_with_text(text1, text2, spacing, bg_image_path, font_path)
        return send_file(img_byte_arr, mimetype='image/jpeg', as_attachment=True, download_name=text2+'.jpg')
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
