from seleniumwire import webdriver  # 用 selenium-wire 替代普通 selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import json


# 测试已成功

class LoginTest:
    def __init__(self, headless=False):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.base_url = "http://localhost:8080"
        self.login_url = "http://localhost:8080/login.html"
        self.verification_code = "123456"
        self.phone = "13812345689"

    def setup(self):
        edge_options = Options()
        if self.headless:
            edge_options.add_argument('--headless=new')
        edge_options.add_argument('--no-sandbox')
        edge_options.add_argument('--disable-dev-shm-usage')
        edge_options.add_argument('--window-size=1920,1080')

        service = Service("D:/Software/edgedriver_win64/msedgedriver.exe")

        print("🚀 启动 Edge 浏览器...")
        self.driver = webdriver.Edge(service=service, options=edge_options)
        self.wait = WebDriverWait(self.driver, 10)
        print("✅ 浏览器启动成功")

    def teardown(self):
        if self.driver:
            time.sleep(1)
            self.driver.quit()

    def login(self, phone=None):
        if phone:
            self.phone = phone

        try:
            print("\n" + "=" * 60)
            print("开始登录流程")
            print("=" * 60)

            # 1. 打开页面
            time.sleep(2)
            self.driver.get(self.login_url)
            time.sleep(1)

            # 2. 输入手机号
            phone_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='请输入手机号']"))
            )
            phone_input.clear()
            phone_input.send_keys(self.phone)
            print(f"✓ 输入手机号: {self.phone}")

            # 3. 发送验证码
            send_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.el-button--success"))
            )
            send_btn.click()
            time.sleep(1)
            print("✓ 点击发送验证码")

            # 4. 输入验证码
            code_input = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder='请输入验证码']")
            code_input.clear()
            code_input.send_keys(self.verification_code)
            print("✓ 输入验证码")

            # 5. 勾选协议
            self.driver.execute_script("""
                const radio = document.querySelector("input[name='readed']");
                if (radio) {
                    radio.checked = true;
                    radio.dispatchEvent(new Event('change', { bubbles: true }));
                }
            """)
            time.sleep(0.5)
            print("✓ 已尝试勾选协议")

            # 6. 找到登录按钮并点击
            login_btn = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[.//span[contains(text(),'登录')]]"))
            )
            self.driver.execute_script("""
                arguments[0].style.border = '3px solid red';
                arguments[0].scrollIntoView(true);
            """, login_btn)
            # 登录前清空请求
            self.driver.requests.clear()

            # 点击登录
            actions = ActionChains(self.driver)
            actions.move_to_element(login_btn).click().perform()
            print("✓ 已点击登录按钮（鼠标模拟点击）")

            # 等 login 请求完成
            auth_token = None
            time.sleep(3)
            # for request in self.driver.requests:
            #     if request.url.endswith("/api/user/login") and request.response:
            #         print(request.response.body.decode('utf-8'))
            #         return True
            for request in self.driver.requests:
                if request.url.endswith("/api/user/login") and request.response:
                    # 先解码得到 JSON 字符串
                    response_body = request.response.body.decode('utf-8')
                    print(response_body)  # 输出: {"success":true,"data":"ca35642239ee413f87f04f52d2c297cd"}

                    # 解析 JSON 字符串为字典
                    response_data = json.loads(response_body)

                    # 提取 data 字段
                    auth_token = response_data["data"]  # 或 response_data.get("data")
                    print("auth:", auth_token)
                    return True

        except Exception as e:
            print(f"✗ 登录失败: {e}")
            return False

    def run(self):
        try:
            self.setup()
            success = self.login()

            if success:
                print("\n" + "="*60)
                print("✓ 登录测试成功！")
            else:
                print("\n" + "="*60)
                print("✗ 登录测试失败！")

            print("="*60)
            print("\n⏳ 1秒后关闭浏览器...")
            time.sleep(1)

        finally:
            self.teardown()


def main():
    print("="*60)
    print("登录自动化测试（捕获 Authorization）")
    print("="*60)

    test = LoginTest(headless=False)
    test.run()


if __name__ == "__main__":
    main()