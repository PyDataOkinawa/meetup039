import base64
from copy import deepcopy
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests


def b64_encode(pillow_img):
    # vision apiへ送信するためには画像をbase64へエンコードする必要がある
    # 一度Pythonのbytes型に変更.
    _bytes = BytesIO()
    pillow_img.save(_bytes, format='jpeg')

    # bytes型をbase64でエンコード.
    bencoded = base64.b64encode(_bytes.getvalue()).decode('utf-8')
    
    return bencoded


def request_vision_api(bencoded_img, api_key):
    endpoint_url = 'https://vision.googleapis.com/v1/images:annotate'
    # postするデータの作成
    # jsonにする
    _data = {'requests': {
        'image': {
            'content': bencoded_img
        },
        'features': [{
            # vision apiのtypeを指定する
            # いろいろあるが、OCRしたいなら 'TEXT_DETECTION'
            'type': 'TEXT_DETECTION',
            # docには"この機能の種類で返される結果の最大数。API が返す結果の数はこれより少ない場合もあります"
            # とあるけど、値変更しても返り値に変化がないのでよくわからない
            'maxResults': 5
        }]
    }}

    # json文字列に変更する.
    json_data = json.dumps(_data)
    params = {'key': api_key}
    headers = {'Content-Type': 'application/json'}
    
    
    res = requests.post(endpoint_url,
                    data=json_data,
                    params=params,
                    headers=headers)
    
    return res


def draw(pillow_img, text_annotations):
    img2 = deepcopy(pillow_img)
    draw = ImageDraw.Draw(img2)
    # text_annotationsの0番目は全体のテキストなのでいらない.
    for index, text_annotation in enumerate(text_annotations[1:]):
        text = text_annotation['description']
        vertices = text_annotation['boundingPoly']['vertices']
        lt, rt, rb, lb = vertices
        start = (lt['x'], lt['y'])
        end = (rb['x'], rb['y'])

        r = 0.9
        text_size = abs(end[1] - start[1]) * r
        font = ImageFont.truetype('./ipaexg00301/ipaexg.ttf', int(text_size))

        draw.rectangle((start, end), outline=(200), fill=(200))
        draw.text((start[0] + 5, start[1] + 5), text, font=font, fill=(0))
        
    return img2