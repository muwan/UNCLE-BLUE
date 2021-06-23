# -*- encoding=utf8 -*-
__author__ = "henly"

from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from airtest.aircv import *
from pathlib import Path
import logging

logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)


connect_device("android://127.0.0.1:5037/4f74b1cc?cap_method=MINICAP_STREAM&&ori_method=MINICAPORI&&touch_method=MINITOUCH")

poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

screenWidth, screenHeight = poco.get_screen_size()
# script content
print("start...")

def start_chuanda():
    print("便遍历当穿搭前页面元素...")
    freeze_poco = poco.freeze()
    user_list = freeze_poco("com.sina.weibo:id/lv_content").children()
    for user in user_list:
        searchbar = user.offspring("com.sina.weibo:id/lySearchInput")
        if searchbar.exists():
            print("跳过搜索按钮...")
            continue
        else:
            user.click()
            print("点进主页...")
            scrape_fans()
            return
            # keyevent("BACK")
            print("返回下一个...")
        return


def scrape_fans():
    sleep(3)
    # 点击粉丝
    fans_btn = poco("com.sina.weibo:id/tvFansCountVideo")
    if fans_btn.exists():
        print("找到粉丝按钮...")
        fans_btn.click()
        print("进入他的粉丝页面...")
        sleep(3)
        scroll_only("./weibo_app_fans_end.png")


def scroll_only(image_name):
    print("🤖：我是个没有感情的滚动机器人️，一直下滑...")
    # 首先清除上一次滑动的图片
    path = Path(image_name)
    if path.exists():
        path.unlink()
        print("删除已经存在的图片...")

    print("图片已经清除，开始滚动..")
    while True:
        sleep(5)
        src_image = capture_image()
        is_same = adjudge_same_image(src_image,image_name)
        # 存在相同图片，需要二次确认，防止没加载出来默认图片
        if is_same:
            second_image = capture_image()
            second_same = adjudge_same_image(second_image,image_name)
            if second_same:
                # 二次确认也相同，说明到底部了，返回上个页面
                print("到底部了，返回上一个...")
                sleep(3)
                # keyevent("BACK")
            else:
                save_image(second_image,image_name)
        else:
            save_image(src_image,image_name)



def save_image(image,image_name):
    end_user = cv2_2_pil(image)
    end_user.save(image_name)
    print("图片已留存，继续下滑...")


def capture_image():
    swipe((screenWidth * 0.5, screenWidth * 0.9), vector=[0, -1.5])
    sleep(5)
    print("先滚动加载，再截图...")
    src_image = crop_image(G.DEVICE.snapshot(), (0, screenHeight / 2, 450, screenHeight / 2 + 250))
    return src_image



def adjudge_same_image(src_image,original_img_name):
    path = Path(original_img_name)
    sleep(1)
    # 如果存在图片，就对比是否一致，如果不存在图片说明是第一次对比
    if path.exists():
        local_image = Template(original_img_name, threshold=0.90)
        is_same = local_image.match_in(src_image)
        return is_same
    return False

def start_weibo_app():
    start_app("com.sina.weibo")
    sleep(2)

    while True:
        start_chuanda()
        return
        # 当前页面滚动结束，判断是否进入下一页
        image_name = "./weibo_app_chuanda.png"
        same_image = capture_image()
        is_same = adjudge_same_image(same_image,image_name)
        if is_same:
            second_img = capture_image()
            second_same = adjudge_same_image(second_img,image_name)
            if second_same:
                print("结束了，搞完了")
            else:
                save_image(image_name)
                print("保存当前页面图片，下一个")



if __name__ == '__main__':
    start_weibo_app()
    
    
# generate html report
# from airtest.report.report import simple_report
# simple_report(__file__, logpath=True)