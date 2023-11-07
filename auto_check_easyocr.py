import os

import time
import easyocr
import pyautogui


def click_screenshot(img_save_path):
    """
    判断CMD窗体是否可以点击，是时点击并截图，不是时返回FALSE
    :return:
    """
    if not pyautogui.locateCenterOnScreen('./help.png'):
        print("没有找到terminal终端的 help 菜单!")
        x, y = pyautogui.size()  # current screen resolution width and height
        print("点击屏幕中央！")
        pyautogui.click(x / 2, y / 2)
        time.sleep(5)
        pyautogui.screenshot(img_save_path)
        time.sleep(5)
    else:
        print("找到terminal终端")
        x, y = pyautogui.locateCenterOnScreen('./help.png')
        pyautogui.click(x, y)
        time.sleep(5)
        pyautogui.screenshot(img_save_path)
        time.sleep(5)


def ocr_img(img_path):
    """
    对截图OCR识别
    :return:识别的文字列表
    """
    reader = easyocr.Reader(['en'], gpu=False)
    result_list = reader.readtext(img_path, detail=0)
    os.remove(img_path)  # 使用后删除图片
    return result_list


def judge_state(result_list):
    """
    判断测试是否结束
    :return:
    """
    for i in range(len(result_list) - 1, -1, -1):
        if "protoresultreporter" in result_list[i].lower():
            print(result_list[i])
            return True
        else:
            pass
    return False


def input_lr(img_save_path):
    """
    在命令行l d中输入l r，获取已有的报告
    :return: 识别的文字列表
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
    :return:识别的文字列表
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
    pass_exist = 0
    for i in range(len(result_list) - 1, -1, -1):
        if "2023" in result_list[i]:
            num_2023 = num_2023 + 1
            print(result_list[i])

        if "pass" in result_list[i].lower() or "fail" in result_list[i].lower() or "build" in result_list[i].lower():
            pass_exist = 1  # 只有当出现pass/fail/build时说明报告个数在cmd中全部显示，否则获取的个数不对
            print("找到的测试报告数为：" + str(num_2023))
            print("找到Pass/Fail/Build中的一个，退出报告计数")
            break
    if pass_exist == 1:
        return num_2023 - 1
    else:
        print("找到的测试报告数为：" + str(num_2023))
        print("测试报告数已经到达上限，停止测试")
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
    if num_online == num_available and num_online != 0:
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


if __name__ == "__main__":
    img_paths = "./imgs/screenshot.png"
    img_lr_path = "./imgs/lr.png"
    img_ld_path = "./imgs/ld.png"
    lr_num = 0
    ld_num = 0
    lr_num_list = []

    while 1:
        click_screenshot(img_paths)  # 点击命令行或屏幕中央并截图
        text_list = ocr_img(img_paths)  # 获取OCR后的文字
        if judge_state(text_list):  # 判断是否结束
            print("找到ProtoResultReporter")
            print("*********************测试结束**********************")
            for i in range(3):  # 识别正确时退出
                lr_list = input_lr(img_lr_path)
                lr_num = get_report_num(lr_list)
                lr_num_list.append(lr_num)  # 将获取到的数据记录在列表中

            for i in range(3):  # 识别正确时退出
                ld_list = input_ld(img_ld_path)
                ld_num = get_device_num(ld_list)
                if ld_num != -1:
                    break

            lr_num = max(lr_num_list)
            if lr_num != -1 and ld_num != -1:
                input_retry(lr_num, ld_num)
                print("输入的retry指令为: " + f'run retry --retry {lr_num} --shard-count {ld_num}')
                print("----------------------------开始下次测试--------------------------")
            else:
                print("获取的报告数已达上限或者设备数不对")  # 当获取的报告数与设备数不对时跳过
            lr_num_list = []
        else:
            print("test is going")  # 当未结束时跳过

        print("开始等待一小时")
        time.sleep(1800)  # 半小时查询一次
