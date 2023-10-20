import time
import pyautogui
from paddleocr import PaddleOCR

def ocr_img(img_path):
    """
    对截图OCR识别
    :return:
    """
    # Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
    # 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`
    ocr = PaddleOCR(use_angle_cls=True, lang="en")  # need to run only once to download and load model into memory
    result = ocr.ocr(img_path, cls=True)
    result_list = []
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            result_list.append(line[1][0])
    print(result_list)
    return result_list


aaaa = ocr_img("./imgs/lr.png")
print("aa")