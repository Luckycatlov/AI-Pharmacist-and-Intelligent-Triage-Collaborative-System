"""
部署测试脚本 - 验证API服务是否正常工作
"""
import requests
import json
import time
from typing import Dict, Any

class APITester:
    """API测试类"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []

    def test_health_check(self) -> bool:
        """测试健康检查端点"""
        try:
            print("[测试1] 健康检查端点...")
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"  [OK] 系统状态: {data.get('status')}")
                print(f"  [信息] 版本: {data.get('version')}")
                print(f"  [信息] 组件状态: {data.get('components')}")
                self.results.append({"test": "健康检查", "status": "PASS", "response_time": response.elapsed.total_seconds()})
                return True
            else:
                print(f"  [失败] 状态码: {response.status_code}")
                self.results.append({"test": "健康检查", "status": "FAIL", "error": f"状态码: {response.status_code}"})
                return False
        except Exception as e:
            print(f"  [错误] 连接失败: {e}")
            self.results.append({"test": "健康检查", "status": "ERROR", "error": str(e)})
            return False

    def test_root_endpoint(self) -> bool:
        """测试根路径端点"""
        try:
            print("\n[测试2] 根路径信息端点...")
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"  [OK] 服务名称: {data.get('message')}")
                print(f"  [信息] 可用端点: {list(data.get('endpoints', {}).keys())}")
                self.results.append({"test": "根路径", "status": "PASS", "response_time": response.elapsed.total_seconds()})
                return True
            else:
                print(f"  [失败] 状态码: {response.status_code}")
                self.results.append({"test": "根路径", "status": "FAIL", "error": f"状态码: {response.status_code}"})
                return False
        except Exception as e:
            print(f"  [错误] 连接失败: {e}")
            self.results.append({"test": "根路径", "status": "ERROR", "error": str(e)})
            return False

    def test_qa_endpoint(self) -> bool:
        """测试问答端点"""
        try:
            print("\n[测试3] 医疗问答端点...")
            test_question = "小儿清热止咳合剂的主要成分是什么？"

            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/qa",
                json={"question": test_question},
                timeout=60
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                print(f"  [OK] 问答成功")
                print(f"  [回答] {answer[:100]}...")
                print(f"  [响应时间] {response_time:.2f}秒")
                self.results.append({
                    "test": "医疗问答",
                    "status": "PASS",
                    "response_time": response_time,
                    "answer_length": len(answer)
                })
                return True
            else:
                print(f"  [失败] 状态码: {response.status_code}")
                print(f"  [错误] {response.text}")
                self.results.append({
                    "test": "医疗问答",
                    "status": "FAIL",
                    "error": f"状态码: {response.status_code}"
                })
                return False
        except Exception as e:
            print(f"  [错误] 请求失败: {e}")
            self.results.append({"test": "医疗问答", "status": "ERROR", "error": str(e)})
            return False

    def test_multiple_questions(self) -> bool:
        """测试多个问题"""
        try:
            print("\n[测试4] 批量问答测试...")
            test_questions = [
                "2岁孩子发烧可以用阿司匹林吗？",
                "孕妇可以服用感冒药吗？"
            ]

            success_count = 0
            for i, question in enumerate(test_questions, 1):
                print(f"  [问题{i}] {question}")
                try:
                    response = requests.post(
                        f"{self.base_url}/qa",
                        json={"question": question},
                        timeout=60
                    )
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get('answer', '')
                        print(f"    [OK] 回答: {answer[:50]}...")
                        success_count += 1
                    else:
                        print(f"    [失败] 状态码: {response.status_code}")
                except Exception as e:
                    print(f"    [错误] {e}")

            success_rate = (success_count / len(test_questions)) * 100
            print(f"  [成功率] {success_rate:.1f}% ({success_count}/{len(test_questions)})")

            self.results.append({
                "test": "批量问答",
                "status": "PASS" if success_rate >= 50 else "PARTIAL",
                "success_rate": success_rate,
                "total": len(test_questions),
                "success": success_count
            })
            return success_count >= 1

        except Exception as e:
            print(f"  [错误] 批量测试失败: {e}")
            self.results.append({"test": "批量问答", "status": "ERROR", "error": str(e)})
            return False

    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("    测试报告")
        print("=" * 60)

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.get("status") == "PASS")
        failed_tests = sum(1 for r in self.results if r.get("status") in ["FAIL", "ERROR"])

        print(f"\n[总计] 测试数量: {total_tests}")
        print(f"[通过] {passed_tests} 个测试")
        print(f"[失败] {failed_tests} 个测试")
        print(f"[成功率] {(passed_tests/total_tests*100):.1f}%")

        print("\n[详细结果]")
        for i, result in enumerate(self.results, 1):
            status = result.get("status")
            status_symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "!"
            print(f"  {i}. {status_symbol} {result.get('test')}: {status}")

        # 保存JSON报告
        report_file = "deployment_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": passed_tests/total_tests*100,
                "results": self.results
            }, f, ensure_ascii=False, indent=2)
        print(f"\n[报告] 详细报告已保存: {report_file}")

        print("=" * 60)

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("    开始部署测试")
        print("=" * 60)
        print(f"[目标] {self.base_url}")
        print(f"[时间] {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 等待服务启动
        print("\n[等待] 等待服务启动...")
        time.sleep(2)

        # 运行测试
        self.test_health_check()
        self.test_root_endpoint()
        self.test_qa_endpoint()
        self.test_multiple_questions()

        # 生成报告
        self.generate_report()

def main():
    """主函数"""
    import sys

    # 可以从命令行参数指定API地址
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    print("[配置] API地址:", base_url)

    tester = APITester(base_url)
    tester.run_all_tests()

    # 返回退出码
    failed_count = sum(1 for r in tester.results if r.get("status") in ["FAIL", "ERROR"])
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())