import requests
import time
import json
from datetime import datetime

# 抢购秒杀优惠券1张
# 测试已成功
class SeckillTest:
    def __init__(self, base_url, authorization):
        self.base_url = base_url
        self.authorization = authorization
        self.headers = {
            'Authorization': authorization,
            'Content-Type': 'application/json'
        }

    def test_seckill(self, voucher_id):
        """
        测试秒杀接口

        Args:
            voucher_id: 优惠券ID

        Returns:
            dict: 包含测试结果的信息
        """
        url = f"{self.base_url}/voucher-order/seckill/{voucher_id}"

        result = {
            'voucher_id': voucher_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status_code': None,
            'response_data': None,
            'success': False,
            'error': None
        }

        try:
            print(f"\n{'='*50}")
            print(f"开始测试秒杀接口 - 优惠券ID: {voucher_id}")
            print(f"请求URL: {url}")
            print(f"请求时间: {result['timestamp']}")
            print(f"{'='*50}")

            start_time = time.time()

            response = requests.post(url, headers=self.headers, json={'id': voucher_id})

            elapsed_time = time.time() - start_time

            result['status_code'] = response.status_code
            result['response_time'] = f"{elapsed_time * 1000:.2f}ms"

            try:
                result['response_data'] = response.json()
            except json.JSONDecodeError:
                result['response_data'] = response.text

            if response.status_code == 200:
                result['success'] = True
                print(f"✓ 请求成功!")
                print(f"状态码: {response.status_code}")
                print(f"响应时间: {result['response_time']}")
                print(f"响应数据: {json.dumps(result['response_data'], ensure_ascii=False, indent=2)}")
            else:
                print(f"✗ 请求失败!")
                print(f"状态码: {response.status_code}")
                print(f"响应数据: {result['response_data']}")

        except requests.exceptions.ConnectionError as e:
            result['error'] = f"连接错误: {str(e)}"
            print(f"✗ 连接失败: {e}")
        except requests.exceptions.Timeout as e:
            result['error'] = f"请求超时: {str(e)}"
            print(f"✗ 请求超时: {e}")
        except Exception as e:
            result['error'] = f"未知错误: {str(e)}"
            print(f"✗ 发生错误: {e}")

        return result

    def batch_test(self, voucher_ids, interval=0.1):
        """
        批量测试秒杀接口

        Args:
            voucher_ids: 优惠券ID列表
            interval: 请求间隔时间(秒)

        Returns:
            list: 所有测试结果的列表
        """
        print(f"\n开始批量测试，共 {len(voucher_ids)} 个请求")
        print(f"请求间隔: {interval}秒")

        results = []
        success_count = 0
        fail_count = 0

        for voucher_id in voucher_ids:
            result = self.test_seckill(voucher_id)
            results.append(result)

            if result['success']:
                success_count += 1
            else:
                fail_count += 1

            if interval > 0:
                time.sleep(interval)

        print(f"\n{'='*50}")
        print(f"批量测试完成")
        print(f"总请求数: {len(voucher_ids)}")
        print(f"成功数: {success_count}")
        print(f"失败数: {fail_count}")
        print(f"成功率: {success_count/len(voucher_ids)*100:.2f}%")
        print(f"{'='*50}\n")

        return results


def main():
    # 配置参数
    BASE_URL = "http://localhost:8081/"
    AUTHORIZATION = "6c85ce3b2da64fa0844c541c0aafd242"

    # 创建测试实例
    tester = SeckillTest(BASE_URL, AUTHORIZATION)

    # 单个测试示例
    print("=== 单个测试示例 ===")
    voucher_id = 1  # 替换为你要测试的优惠券ID
    result = tester.test_seckill(voucher_id)

    # 批量测试示例
    print("\n=== 批量测试示例 ===")
    voucher_ids = [11]  # 替换为实际的优惠券ID列表
    results = tester.batch_test(voucher_ids, interval=0.1)

    # 保存测试结果到文件
    # with open('seckill_test_results.json', 'w', encoding='utf-8') as f:
    #     json.dump(results, f, ensure_ascii=False, indent=2)
    # print("测试结果已保存到 seckill_test_results.json")


if __name__ == "__main__":
    main()
