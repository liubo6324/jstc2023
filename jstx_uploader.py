#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2023-04-20 12:00
# @Author : HCB
import time
import requests
from PIL import Image
from pyzbar.pyzbar import decode
import urllib.parse
requests.packages.urllib3.disable_warnings()
# 设置fiddler代理方便查看，如不设置调成None
proxies = {
    "http": "http://127.0.0.1:8888",
    "https": "http://127.0.0.1:8888",
}
# proxies = None


def upload_2023(verify_token, filename):
    """
    upload a photo from local computer
    :param verify_token: the login token
    :param filename: the full path of photo
    :return:
    """
    url = "https://jstxcj.91job.org.cn/v2/camera/upload"
    headers = {
        'Content-Type': 'multipart/form-data; boundary=WABoundary+88B67366A0A9038FWA',
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.20(0x18001442) NetType/4G Language/zh_CN',
        'Authorization': f'Bearer {verify_token}',
        'Referer': 'https://servicewechat.com/wx9b3c613f1ddbf8c1/33/page-frame.html'
    }
    upload_data = f"--WABoundary+88B67366A0A9038FWA".encode("utf-8") \
                  + '\r\nContent-Disposition: form-data; name="file";\r\nfilename="tmp.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'.encode(
        "utf-8") \
                  + open(filename, "rb").read() \
                  + f"\r\n--WABoundary+88B67366A0A9038FWA--\r\n".encode("utf-8")
    res1 = requests.post(url, headers=headers, data=upload_data, verify=False, proxies=proxies)
    print(f"照片上传结果：\n{res1.text}\n")
    if "上传成功" not in res1.text:
        return

    url2 = "https://jstxcj.91job.org.cn/v2/camera/living"
    headers2 = {
        'Connection': 'keep-alive',
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': f'Bearer {verify_token}',
        'Accept-Encoding': 'gzip,compress,br,deflate',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.20(0x18001442) NetType/4G Language/zh_CN',
        'Referer': 'https://servicewechat.com/wx9b3c613f1ddbf8c1/33/page-frame.html'
    }
    res2 = requests.get(url2, headers=headers2, verify=False, proxies=proxies)
    print(f"活体检测结果：\n{res2.text}\n")
    if "活体检测成功" not in res2.text:
        return

    # 这步如果检测成功则会自动进入草稿箱
    url3 = "https://jstxcj.91job.org.cn/v2/camera/crop"
    res3 = requests.get(url3, headers=headers2, verify=False, proxies=proxies)
    print(f"最终检测结果：\n{res3.text}\n")


def extract_qrcode_string(image_path):
    """
    从本地图片提取二维码的字符串信息

    参数：
    - image_path: str，图片的路径
    - url_decode: bool，是否对字符串进行URL解码，默认为False

    返回值：
    - str，二维码的字符串信息，若未找到二维码则返回None
    """
    try:
        # 打开图片
        with Image.open(image_path) as img:
            # 解码二维码
            qrcode = decode(img)
            if qrcode:
                # 返回第一个二维码的字符串信息

                return urllib.parse.quote(qrcode[0].data.decode('utf-8'))
            else:
                print("未找到二维码")
                return None
    except Exception as e:
        print("提取二维码信息失败：", e)
        return None


def login(qr_string, wx_open_id):
    """
    gen the login token
    :param wx_open_id: from wechat mini program
    :param qr_string: qrcode info
    :return:
    """
    # 检测是否填入openId
    if not wx_open_id:
        tmp = input("请在此输入openid然后回车，或者在代码中填入~~")
        if tmp:
            wx_open_id = tmp
        else:
            print("未填入openid，即将退出")
            time.sleep(3)
            exit()

    url = "https://jstxcj.91job.org.cn/code/decode"
    headers = {
        'Connection': 'keep-alive',
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer ',
        'Accept-Encoding': 'gzip,compress,br,deflate',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.20(0x18001442) NetType/WIFI Language/zh_CN',
        'Referer': 'https://servicewechat.com/wx9b3c613f1ddbf8c1/33/page-frame.html'
    }
    payload = f"code={qr_string}&open_id={wx_open_id}"
    res = requests.post(url, headers=headers, data=payload, verify=False, proxies=proxies)
    tk = res.text.replace('"', '')
    return tk


if __name__ == "__main__":
    open_id = ""  # 个人微信号在江苏图采小程序的唯一标识，抓包获取，包的链接为https://jstxcj.91job.org.cn/code/decode

    # 获取二维码信息
    qr_path = r"C:\Users\Administrator\Desktop\1681958005637.png"  # 个人采样二维码图片的路径
    result = extract_qrcode_string(qr_path)

    # 登录，上传照片并检测
    token = login(result, open_id)
    photo = r'C:\Users\Administrator\Desktop\xjpic.jpg'  # 个人照片的路径
    upload_2023(token, photo)
