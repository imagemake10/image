from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

def create_image_with_text(text1, text2, max_chars_in_line, spacing, bg_image_path, font_path, font_size=40):
    # 배경 이미지 열기
    image = Image.open(bg_image_path)
    draw = ImageDraw.Draw(image)

    # 첫 번째 텍스트 폰트 설정
    try:
        font1 = ImageFont.truetype(font_path, font_size)
    except IOError:
        font1 = ImageFont.load_default()

    # 두 번째 텍스트 폰트 설정 (첫 번째보다 10 작게)
    try:
        font2 = ImageFont.truetype(font_path, font_size - 10)
    except IOError:
        font2 = ImageFont.load_default()

    # 줄바꿈을 위한 함수
    def wrap_text(text, draw, font, max_width, max_chars_in_line=None):
        if max_chars_in_line is not None and len(text) <= max_chars_in_line:
            return [text]
        
        lines = []
        words = text.split()
        while words:
            line = ''
            while words and (draw.textsize(line + words[0], font=font)[0] <= max_width) and (max_chars_in_line is None or len(line) + len(words[0]) <= max_chars_in_line):
                line = line + (words.pop(0) + ' ')
            lines.append(line)
        return lines

    # 이미지의 너비 계산
    max_width = image.size[0] - 40  # 이미지의 너비에서 여백을 뺀 값
    lines1 = wrap_text(text1, draw, font1, max_width, max_chars_in_line)
    lines2 = wrap_text(text2, draw, font2, max_width)

    # 각 텍스트의 전체 높이 계산 (줄 간격 포함)
    text1_height = sum([draw.textsize(line, font=font1)[1] + 5 for line in lines1])
    text2_height = sum([draw.textsize(line, font=font2)[1] for line in lines2])
    total_height = text1_height + text2_height + spacing

    # 첫 번째 텍스트의 시작 y 좌표 계산
    y = (image.size[1] - total_height) / 2

    # 첫 번째 텍스트 그리기 (줄 간격 포함)
    for line in lines1:
        text_width, line_height = draw.textsize(line, font=font1)
        x = (image.size[0] - text_width) / 2
        draw.text((x, y), line, fill="black", font=font1)
        y += line_height + 5  # 줄 간격 추가

    # 두 번째 텍스트 시작 y 좌표에 간격 추가
    y += spacing

    # 두 번째 텍스트 그리기
    for line in lines2:
        text_width, line_height = draw.textsize(line, font=font2)
        x = (image.size[0] - text_width) / 2
        draw.text((x, y), line, fill="black", font=font2)
        y += line_height

    # 이미지 저장
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text1 = request.form['text1']
        text2 = request.form['text2']
        max_chars_in_line = int(request.form['max_chars_in_line'])
        spacing = int(request.form['spacing'])
        bg_image = request.files['bg_image']

        # 저장된 배경 이미지 경로
        bg_image_path = 'background.jpg'
        bg_image.save(bg_image_path)

        # 한글 폰트 경로
        font_path = 'NanumBarunGothicBold.ttf'

        img_byte_arr = create_image_with_text(text1, text2, max_chars_in_line, spacing, bg_image_path, font_path)

        return send_file(img_byte_arr, mimetype='image/jpeg', as_attachment=True, download_name=text2+'.jpg')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
