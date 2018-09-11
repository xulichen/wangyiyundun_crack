# -*- coding:utf-8 -*-
from cv2 import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
import time
import random
import requests
import os
import re
from PIL import Image


# url = 'https://www.adidas.com.cn/member/login?locale=zh_CN'
# browser = webdriver.Chrome()
# browser.get(url)
# b = browser.find_elements_by_xpath('//div[@class="yidun_bgimg"]/img')
# print b
# for i in b:
#     a = i.get_attribute('src')
#     print a


class AdidasSliderCrack(object):
    def __init__(self, buy_url=None):
        self.url = 'https://www.adidas.com.cn/member/login?locale=zh_CN'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 10)
        self.buy_url = buy_url

    def download_image(self):
        img_urls = self.browser.find_elements_by_xpath('//div[@class="yidun_bgimg"]/img')
        img_list = [img_url.get_attribute('src') for img_url in img_urls][2:]
        for url in img_list:
            response = requests.get(url=url, stream=True, timeout=(20, 20))
            with open('icon.{}'.format(url.split('.')[-1]), 'wb') as f:
                for chunk in response.iter_content(128):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()
        return img_list

    # def get_distance(self):
    #     cut_img = cv2.imread('icon1.jpg')
    #     back_img = cv2.imread('icon.jpg')
    #
    #     print cut_img.shape
    #     back_height, back_width, _ = back_img.shape
    #     cut_height, cut_width, _ = cut_img.shape
    #
    #     back_canny = get_back_canny(back_img)
    #     operator = get_operator(cut_img, cut_height, cut_width)
    #     pos_x, max_value = best_match(back_canny, operator)
    #     print pos_x
    #
    #     '''
    #     img1 = Image.open('icon.jpg')
    #     img2 = Image.open('icon.png')
    #     weight1, height1 = img1.size
    #
    #     weight2, height2 = img2.size
    #
    #     mid = (height1 - height2) / 2
    #     if height1 < height2:
    #         height1 = height2
        #
        # for i in range(60, weight1 - weight2):
        #     cut = img1.crop((i, mid, i + weight2, height1 - mid))
        #     cut.show()
        #     result = self.image_merge(cut, img2)
        #     if result:
        #         print i
        #         return i
        #
        # return 60
        # '''

    def is_px_equal(self, img1, img2, x, y):
        """
        判断两个像素是否相同
        :param img1: 图片1
        :param img2:图片2
        :param x:位置1
        :param y:位置2
        :return:像素是否相同
        """
        pix1 = img1.load()[x, y]
        pix2 = img2.load()[x, y]
        if pix2 == (0, 0, 0, 0):
            return False
        threshold = 60
        print pix1, pix2
        if abs(pix1[0] - pix2[0]) < threshold and abs(pix1[1] - pix2[1]) < threshold and abs(
                        pix1[2] - pix2[2]) < threshold:
            return True
        else:
            return False
    #
    def image_merge(self, full_img, block_img):
        """
        :param full_img: 图片切块
        :param block_img: 滑块
        :return:
        """
        count = 0
        for i in range(full_img.size[0]):
            for j in range(full_img.size[1]):
                if self.is_px_equal(full_img, block_img, i, j):
                    print i, j
                    count += 1
        # print count
        if count > 5000:
            return True

    def get_track(self, distance):
        """
        根据偏移量和手动操作模拟计算移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        tracks = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 时间间隔
        t = 0.2
        # 初始速度
        v = 0

        while current < distance:
            if current < mid:
                a = random.uniform(2, 5)
            else:
                a = -(random.uniform(12.5, 13.5))
            v0 = v
            v = v0 + a * t
            x = v0 * t + 1 / 2 * a * t * t
            current += x

            if 0.6 < current - distance < 1:
                x = x - 0.53
                tracks.append(round(x, 2))

            elif 1 < current - distance < 1.5:
                x = x - 1.4
                tracks.append(round(x, 2))
            elif 1.5 < current - distance < 3:
                x = x - 1.8
                tracks.append(round(x, 2))

            else:
                tracks.append(round(x, 2))

        print tracks
        return tracks

    def get_slider(self):
        """
        获取滑块
        :return:滑块对象
        """
        try:
            slider = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//div[@id="fastCaptcha"]//div[@class="yidun_slider"]')))
            return slider
        except TimeoutException:
            print('加载超时...')

    def move_to_gap(self, slider, tracks):
        """
        将滑块移动至偏移量处
        :param slider: 滑块
        :param tracks: 移动轨迹
        :return:
        """
        action = ActionChains(self.browser)
        action.click_and_hold(slider).perform()
        for x in tracks:
            action.move_by_offset(xoffset=x, yoffset=-1).perform()
            action = ActionChains(self.browser)
        time.sleep(0.6)
        action.release().perform()

    def success_check(self):
        """
        验证是否成功
        :return:
        """
        try:
            if re.findall('yidun yidun--light yidun--float yidun--jigsaw yidun--success', self.browser.page_source, re.S):
                print('验证成功！')
                return True
            else:
                print('验证失败！')
                return False
        except TimeoutException:
            print('加载超时...')
            # finally:
            #     self.browser.close()

    def input_name(self, name=''):
        change_login = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//a[@class="e-login-detial-account none-sm form-input-mobile-margin"]'))
        )
        change_login.click()

        name_tag = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@id="loginName"]'))
        )

        name_tag.send_keys(name)

    def input_passwd(self, passwd=''):
        passwd_tag = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@id="password"]'))
        )

        passwd_tag.send_keys(passwd)

    def press_button(self):
        button = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//a[@id="loginBtn"]'))
        )
        button.click()

    def login_page_process(self, login_dict):
        """
        :param login_dict: 登入字典
        :return:
        """
        name = login_dict['name']
        passwd = login_dict['passwd']
        self.input_name(name=name)
        self.input_passwd(passwd=passwd)
        self.press_button()

    def register(self, phone_number):
        # todo: finish register
        self.browser.get(self.url)

        phone_tag = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@id="loginMobile"]'))
        )
        phone_tag.send_keys(phone_number)

        validate_code = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//a[@class="events-btn-git-code"]'))
        )

        validate_code.click()

        while True:
            time.sleep(1)
            img_list = self.download_image()
            cut_image, back_image = read_img_file('icon.png', 'icon.jpg')
            distance = get_distance(back_img=back_image, cut_img=cut_image)
            # distance = distance * 382 / 480 + 16
            print distance
            if distance:
                tracks = self.get_track(distance)
                slider = self.get_slider()
                self.move_to_gap(slider=slider, tracks=tracks)
                # time.sleep(60)
            if self.success_check():
                break

        sms_code = raw_input('短信验证码： ')
        code_tag = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@id="smsCode"]'))
        )
        code_tag.send_keys(sms_code)

        self.press_button()

    def get_detail_process(self):
        time.sleep(0.2)
        self.browser.get(self.buy_url)
        self.info_select()

    def info_select(self):
        size_button = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="select-box"]//a[@class="btn"]'))
        )
        size_button.click()

        size_selector = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="overview product-size"]/ul/li[5]/a'))
        )

        size_selector.click()
        # size_button.click()
        close_cookies = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//a[@class="banner-close events-banner-close-foot"]/i'))
        )
        close_cookies.click()

        time.sleep(2)
        buy_button = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//a[@class="btn btn-gradient-blue btn-have-arrow btn-buy-it-now"]/span'))
        )

        # self.browser.execute_script("arguments[0].scrollIntoView();", buy_button)

        buy_button.click()

    def address_info(self):
        pp_button = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="checked-select-con font-size-12 none-sm privacy-policy"]/div/i'))
        )
        pp_button.click()

        payment_button = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//a[@class="btn btn-blue btn-have-arrow payment-button"]/span'))
        )

        self.browser.execute_script("arguments[0].scrollIntoView();", payment_button)
        payment_button.click()

    def run(self):
        self.browser.get(self.url)
        self.login_page_process({'name': '13262797993', 'passwd': 'xu123456'})
        self.get_detail_process()
        self.address_info()


def get_distance(back_img, cut_img, slider_width=20):
    back_height, back_width, _ = back_img.shape
    cut_height, cut_width, _ = cut_img.shape

    back_canny = get_back_canny(back_img)
    operator = get_operator(cut_img, cut_height, cut_width)
    pos_x, max_value = best_match(back_canny, operator, cut_width, back_width)
    pos_x = pos_x * 382 / back_width
    if 32 < pos_x < 310:
        pos_x = pos_x + 16 + slider_width
    elif pos_x > 300:
        pos_x = 310 + (pos_x - 310) * 2 + 16 + slider_width
    return pos_x


def read_img_file(cut_dir, back_dir):
    cut_image = cv2.imread(cut_dir)
    back_image = cv2.imread(back_dir)
    cut_height, cut_width, _ = cut_image.shape
    back_height, back_width, _ = back_image.shape

    mid = (back_height - cut_height) / 2
    if mid > 0:
        back_image = back_image[mid: back_height - mid, :]

    return cut_image, back_image


def best_match(back_canny, operator, cut_width, back_width):
    max_value, pos_x = 0, 0
    for x in range(cut_width, back_width - cut_width):
        block = back_canny[:, x:x + cut_width]
        value = (block * operator).sum()
        if value > max_value:
            max_value = value
            pos_x = x
    return pos_x, max_value


def get_back_canny(back_img):
    img_blur = cv2.GaussianBlur(back_img, (3, 3), 0)
    img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
    img_canny = cv2.Canny(img_gray, 100, 200)

    # cv2.imshow('Canny', img_canny)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return img_canny


def get_operator(cut_img, cut_height, cut_width):
    cut_gray = cv2.cvtColor(cut_img, cv2.COLOR_BGR2GRAY)

    _, cut_binary = cv2.threshold(cut_gray, 127, 255, cv2.THRESH_BINARY)
    # 获取边界
    _, contours, hierarchy = cv2.findContours(cut_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # 获取最外层边界
    contour = contours[-1]
    # operator矩阵
    operator = np.zeros((cut_height, cut_width))
    # 根据 contour填写operator
    for point in contour:
        operator[point[0][1]][point[0][0]] = 1

    # cv2.imshow('operator', operator)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return operator


if __name__ == '__main__':
    # check = AdidasSliderCrack(buy_url='https://www.adidas.com.cn/item/B37619?locale=zh_CN')
    # check.browser.maximize_window()
    # check.register('13967122154')

    cut_image, back_image = read_img_file('icon.png', 'icon.jpg')
    distance = get_distance(back_img=back_image, cut_img=cut_image)
    print distance
