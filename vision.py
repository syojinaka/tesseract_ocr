import requests
from base64 import b64encode
import json


def get_fullTextAnnotation(json_data):
    text_dict = json.loads(json_data)
    try:
        text = text_dict['responses'][0]['fullTextAnnotation']['text']
        return text
    except:
        print(None)
        return None


ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
KEY = ''

# OCR対象となるファイルのパス
image_filenames = {'images/test.png'}

img_requests = []
for imgname in image_filenames:
    with open(imgname, 'rb') as f:
        ctxt = b64encode(f.read()).decode('utf-8')
        img_requests.append({
            'image': {'content': ctxt},
            'features': [{
                'type': 'TEXT_DETECTION',
                'maxResults': 5
            }]
        })


response = requests.post(
                        ENDPOINT_URL,
                        data=json.dumps({"requests": img_requests}).encode(),
                        params={'key': KEY},
                        headers={'Content-Type': 'application/json'})


for idx, resp in enumerate(response.json()['responses']):
    print(get_fullTextAnnotation(response.text))
    # print(json.dumps(resp, indent=2))


