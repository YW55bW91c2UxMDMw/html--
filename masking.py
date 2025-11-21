from flask import Flask, render_template_string, request, send_file
from rembg import remove
from PIL import Image
import io

app = Flask(__name__)

# HTML 코드를 파이썬 안에 포함시켰습니다 (파일 관리를 쉽게 하기 위해)
HTML_PAGE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>루미의 누끼 공장</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding: 50px; background-color: #f0f2f5; }
        h1 { color: #333; }
        .container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); display: inline-block; }
        input[type="file"] { margin: 20px 0; }
        button { background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #0056b3; }
        #result { margin-top: 20px; max-width: 100%; border: 2px dashed #ccc; display: none; }
        .loading { display: none; color: #666; margin-top: 10px;}
    </style>
</head>
<body>
    <div class="container">
        <h1>✂️ 루미의 자동 누끼 따기 ✂️</h1>
        <p>이미지를 선택하고 버튼을 누르면 배경이 사라져요!</p>
        
        <form id="uploadForm" enctype="multipart/form-data">
            <input type="file" name="file" id="fileInput" accept="image/*" required>
            <br>
            <button type="button" onclick="uploadImage()">배경 제거하기</button>
        </form>

        <p class="loading" id="loadingMsg">루미가 열심히 작업 중... 🦊💦</p>
        <br>
        <img id="result" alt="결과 이미지">
        <br>
        <a id="downloadLink" style="display:none;">[다운로드]</a>
    </div>

    <script>
        async function uploadImage() {
            const fileInput = document.getElementById('fileInput');
            const resultImg = document.getElementById('result');
            const loadingMsg = document.getElementById('loadingMsg');
            const downloadLink = document.getElementById('downloadLink');

            if(fileInput.files.length === 0) {
                alert("이미지를 먼저 선택해주세요!");
                return;
            }

            // 로딩 표시
            loadingMsg.style.display = 'block';
            resultImg.style.display = 'none';
            downloadLink.style.display = 'none';

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            try {
                // 파이썬 서버로 전송
                const response = await fetch('/remove', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error("서버 오류!");

                // 결과를 받아서 이미지로 변환
                const blob = await response.blob();
                const imageUrl = URL.createObjectURL(blob);

                // 화면에 표시
                resultImg.src = imageUrl;
                resultImg.style.display = 'block';
                
                // 다운로드 링크 설정
                downloadLink.href = imageUrl;
                downloadLink.download = "rumi_no_bg.png";
                downloadLink.style.display = 'inline-block';
                
            } catch (error) {
                alert("오류가 발생했습니다: " + error.message);
            } finally {
                loadingMsg.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/remove', methods=['POST'])
def remove_background():
    if 'file' not in request.files:
        return '파일이 없습니다', 400
    
    file = request.files['file']
    if file.filename == '':
        return '파일을 선택하지 않았습니다', 400

    # 이미지 읽기
    input_image = file.read()
    
    # 배경 제거 (기존 코드 활용)
    output_image = remove(input_image)
    
    # 결과를 메모리에 저장해서 바로 브라우저로 전송 (파일 저장 안함)
    return send_file(
        io.BytesIO(output_image),
        mimetype='image/png'
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)