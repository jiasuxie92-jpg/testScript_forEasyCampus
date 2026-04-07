import csv
import random
import time
import json
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# 测试已成功

class LoginTest:
    def __init__(self, headless=False):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.login_url = "http://localhost:8080/login.html"
        self.verification_code = "123456"
        self.auth_token = None
        self.phone = None

    def setup(self):
        edge_options = Options()
        if self.headless:
            edge_options.add_argument('--headless=new')
        edge_options.add_argument('--no-sandbox')
        edge_options.add_argument('--disable-dev-shm-usage')
        edge_options.add_argument('--window-size=1920,1080')

        service = Service("D:/Software/edgedriver_win64/msedgedriver.exe")
        self.driver = webdriver.Edge(service=service, options=edge_options)
        self.wait = WebDriverWait(self.driver, 10)

    def teardown(self):
        if self.driver:
            time.sleep(1)
            self.driver.quit()

    def login(self, phone):
        self.phone = phone
        self.auth_token = None
        try:
            self.driver.get(self.login_url)
            time.sleep(1)

            # 输入手机号
            phone_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='请输入手机号']"))
            )
            phone_input.clear()
            phone_input.send_keys(self.phone)

            # 点击发送验证码
            send_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.el-button--success"))
            )
            send_btn.click()
            time.sleep(1)

            # 输入验证码
            code_input = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder='请输入验证码']")
            code_input.clear()
            code_input.send_keys(self.verification_code)

            # 勾选协议
            self.driver.execute_script("""
                const radio = document.querySelector("input[name='readed']");
                if (radio) {
                    radio.checked = true;
                    radio.dispatchEvent(new Event('change', { bubbles: true }));
                }
            """)
            time.sleep(0.5)

            # 点击登录
            login_btn = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[.//span[contains(text(),'登录')]]"))
            )
            self.driver.execute_script("""
                arguments[0].scrollIntoView(true);
            """, login_btn)

            self.driver.requests.clear()
            actions = ActionChains(self.driver)
            actions.move_to_element(login_btn).click().perform()

            # 等 login 请求完成并捕获 token
            timeout = 10
            start = time.time()
            while time.time() - start < timeout:
                for request in self.driver.requests:
                    if "/api/user/login" in request.url and request.response:
                        body = request.response.body.decode('utf-8')
                        try:
                            data = json.loads(body)
                            self.auth_token = data.get("data")
                        except Exception as e:
                            print("⚠ 解析 JSON 失败:", e)
                        if self.auth_token:
                            return True
                time.sleep(0.5)
            return False
        except Exception as e:
            print(f"✗ 登录失败 ({phone}): {e}")
            return False

import random

def random_phone():
    """
    生成合法的随机中国手机号
    - 中国手机号一般 11 位
    - 号段规则：
      13x, 14[5,7,9], 15[0-3,5-9], 16[2,5-7], 17[0-8], 18x, 19[0-3,5-9]
    """
    prefixes = [
        '130','131','132','133','134','135','136','137','138','139',
        '145','147','149',
        '150','151','152','153','155','156','157','158','159',
        '162','165','166','167',
        '170','171','172','173','175','176','177','178',
        '180','181','182','183','184','185','186','187','188','189',
        '190','191','192','193','195','196','197','198','199'
    ]
    prefix = random.choice(prefixes)
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(11 - len(prefix))])
    return prefix + suffix

def main():
    num_accounts = 10  # 需要生成的手机号数量
    results = []

    test = LoginTest(headless=False)


    try:
        for _ in range(num_accounts):
            test.setup()
            phone = random_phone()
            success = test.login(phone)
            token = test.auth_token if success else ""
            print(f"{phone} -> {token}")
            results.append({"phone": phone, "auth_token": token})
            time.sleep(1)  # 每次登录间隔，可根据需要调整
            test.teardown()
    finally:
        test.teardown()

    # 保存 CSV
    csv_file = "auth_tokens.csv"
    with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["phone", "auth_token"])
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"\n✅ 已保存 {len(results)} 条 auth_token 到 {csv_file}")


if __name__ == "__main__":
    main()