from paddleocr import PaddleOCR
import time
import pyautogui


def click_screenshot(img_save_path):
    """
    判断CMD窗体是否可以点击，是时点击并截图，不是时返回FALSE
    :return:
    """
    if not pyautogui.locateCenterOnScreen('./help.png'):
        print("没有找到terminal终端的 help 菜单，请确认是否被遮挡")
        return False
    else:
        print("找到terminal终端")
        x, y = pyautogui.locateCenterOnScreen('./help.png')
        pyautogui.click(x, y)
        time.sleep(5)
        pyautogui.screenshot(img_save_path)
        time.sleep(5)
        return True


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


def judge_state(result_list):
    """
    判断测试是否结束
    :return:
    """
    for i in range(len(result_list) - 1, -1, -1):
        if "final logs:" in result_list[i] or "Total Tests" in result_list[i]:
            print("测试结束")
            return True
        else:
            pass
    print("test is going")
    return False


def input_lr(img_save_path):
    """
    在命令行中输入l r，获取已有的报告
    :return:
    """
    pyautogui.typewrite('l r')
    time.sleep(5)
    pyautogui.press('enter')
    time.sleep(5)
    click_screenshot(img_save_path)
    return ocr_img(img_save_path)


def input_ld(img_save_path):
    """
    在命令行中输入l r，获取已有的报告
    :return:
    """
    pyautogui.typewrite('l d')
    time.sleep(5)
    pyautogui.press('enter')
    time.sleep(5)
    click_screenshot(img_save_path)
    return ocr_img(img_save_path)


def get_report_num(result_list):
    """
    获取report的数字，在 run retry --retry 时使用
    :return:
    """

    num_2023 = 0
    num_of = 0
    pass_exist = 0
    for i in range(len(result_list) - 1, -1, -1):
        if "2023" in result_list[i]:
            num_2023 = num_2023 + 1
            print(result_list[i])
        if "2023." in result_list[i].lower():
            num_of = num_of + 1
            print(result_list[i])
        if "pass" in result_list[i].lower() or "fail" in result_list[i].lower() or "build" in result_list[i].lower():
            pass_exist = 1  # 只有当出现pass/fail/build时说明报告个数在cmd中全部显示，否则获取的个数不对
            print("找到Pass/Fail/Build中的一个，退出报告计数")
            break

    if num_2023 == num_of and pass_exist == 1:
        return num_2023 - 1
    else:
        return -1


def get_device_num(result_list):
    """
    获取 device的个数，在 run retry --retry 时使用
    :return:
    """
    num_online = 0
    num_available = 0
    for i in range(len(result_list) - 1, -1, -1):
        if "online" in result_list[i].lower():
            num_online = num_online + 1
            print(result_list[i])
        if "available" in result_list[i].lower():
            num_available = num_available + 1
            print(result_list[i])
        if "state" in result_list[i].lower() or "allocation" in result_list[i].lower() or "build" in result_list[
            i].lower():
            print("找到State/Allocation/Build中的一个，退出设备计数")
            break
    if num_online == num_available:
        return num_available
    else:
        return -1


def input_retry(lr_num_p, ld_num_p):
    """
    输入retry指令
    :return:
    """

    # 输入指令
    pyautogui.typewrite(f'run retry --retry {lr_num_p} --shard-count {ld_num_p}')
    time.sleep(5)
    pyautogui.press('enter')
    time.sleep(5)
    print("输入的retry指令为: " + f'run retry --retry {lr_num_p} --shard-count {ld_num_p}')


if __name__ == "__main__":
    img_paths = "./imgs/screenshot.png"
    img_lr_path = "./imgs/lr.png"
    img_ld_path = "./imgs/ld.png"

    while 1:
        if click_screenshot(img_paths):  # 判断是否可以点击命令行
            text_list = ocr_img(img_paths)  # 获取OCR后的文字
            if judge_state(text_list):  # 判断是否结束
                for i in range(3):  # 识别正确时退出
                    lr_list = input_lr(img_lr_path)
                    lr_num = get_report_num(lr_list)
                    if lr_num != -1:
                        break

                for i in range(3):  # 识别正确时退出
                    ld_list = input_ld(img_ld_path)
                    ld_num = get_device_num(ld_list)
                    if ld_num != -1:
                        break

                if lr_num != -1 and ld_num != -1:
                    input_retry(lr_num, ld_num)
                else:
                    pass  # 当获取的报告数与设备数不对时跳过

            else:
                pass  # 当未结束时跳过

        else:
            pass  # 当CMD不在主界面时跳过
        print("开始等待一小时")
        time.sleep(3600)  # 半小时查询一次
