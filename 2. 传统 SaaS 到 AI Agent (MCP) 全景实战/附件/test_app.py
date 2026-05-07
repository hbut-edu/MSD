"""第 2 章附件应用的单元测试与性能测试。

这些测试覆盖三层内容：
1. 工具函数：验证每个本地业务能力是否能独立工作。
2. SaaS 控制器：验证传统固定流水线能否串起完整工资流程。
3. 集成工作流：验证“查询员工 -> 计算工资 -> 导出 CSV”的端到端链路。

运行方式：
    conda activate msd-agent-mcp
    python test_app.py
    python test_app.py --performance
"""

import unittest
import json
import os
from app import (
    get_employee_directory,
    calculate_payroll_and_tax,
    export_payroll_csv,
    saas_generate_payroll_api
)

class TestTools(unittest.TestCase):
    """测试三个可被 Agent 调用的底层工具函数。"""
    
    def test_get_employee_directory(self):
        """员工目录工具应返回非空 JSON 数组，并包含 Agent 后续计算所需字段。"""
        result = get_employee_directory()
        # 工具函数返回 JSON 字符串，因此测试先反序列化，再验证结构。
        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("id", data[0])
        self.assertIn("name", data[0])
        self.assertIn("level", data[0])
    
    def test_calculate_payroll_and_tax_with_valid_data(self):
        """有效员工数据应被正确计算为应发、扣除项和实发工资。"""
        # L1 基础工资是 10000；五险一金 20%，个税为扣除后金额的 5%。
        employees = json.dumps([{"id": "E01", "name": "张三", "level": "L1"}])
        result = calculate_payroll_and_tax(employees)
        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("应发工资", data[0])
        self.assertIn("五险一金扣除", data[0])
        self.assertIn("个税扣除", data[0])
        self.assertIn("实发工资", data[0])
        self.assertEqual(data[0]["应发工资"], 10000)
        self.assertEqual(data[0]["五险一金扣除"], 2000)
        self.assertEqual(data[0]["个税扣除"], 400)
        self.assertEqual(data[0]["实发工资"], 7600)
    
    def test_calculate_payroll_and_tax_with_empty_data(self):
        """空字符串参数应返回结构化 error，而不是抛出未捕获异常。"""
        result = calculate_payroll_and_tax("")
        data = json.loads(result)
        self.assertIn("error", data)
    
    def test_calculate_payroll_and_tax_with_invalid_json(self):
        """非法 JSON 应被业务函数捕获，并转成 Agent 可读的错误消息。"""
        result = calculate_payroll_and_tax("invalid json")
        data = json.loads(result)
        self.assertIn("error", data)
    
    def test_calculate_payroll_and_tax_with_missing_level(self):
        """缺少 level 字段时，该员工记录应带 error 字段，方便定位坏数据。"""
        employees = json.dumps([{"id": "E01", "name": "张三"}])
        result = calculate_payroll_and_tax(employees)
        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertIn("error", data[0])
    
    def test_calculate_payroll_and_tax_with_invalid_level(self):
        """未知职级不能静默按 0 元工资处理，应显式返回业务错误。"""
        employees = json.dumps([{"id": "E01", "name": "张三", "level": "L99"}])
        result = calculate_payroll_and_tax(employees)
        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertIn("error", data[0])
    
    def test_export_payroll_csv_with_valid_data(self):
        """有效工资明细应能导出 CSV，并返回文件路径和记录数量。"""
        payroll_data = json.dumps([
            {"id": "E01", "name": "张三", "level": "L1", "应发工资": 10000, "五险一金扣除": 2000, "个税扣除": 400, "实发工资": 7600}
        ])
        result = export_payroll_csv(payroll_data)
        data = json.loads(result)
        self.assertEqual(data.get("status"), "success")
        self.assertIn("file_path", data)
        self.assertIn("record_count", data)
        self.assertEqual(data["record_count"], 1)
        
        if "file_path" in data:
            # 这里只验证文件存在，不读取文件内容；字段写入逻辑由 csv.DictWriter 负责。
            self.assertTrue(os.path.exists(data["file_path"]))
    
    def test_export_payroll_csv_with_empty_data(self):
        """空工资数据不应生成空文件，应返回 error。"""
        result = export_payroll_csv("")
        data = json.loads(result)
        self.assertIn("error", data)
    
    def test_export_payroll_csv_with_invalid_json(self):
        """非法 JSON 不能进入文件写入阶段，避免生成不可解释的 CSV。"""
        result = export_payroll_csv("invalid json")
        data = json.loads(result)
        self.assertIn("error", data)

class TestSaaSController(unittest.TestCase):
    """测试传统 SaaS 固定流水线。"""
    
    def test_saas_generate_payroll_api(self):
        """控制器应一次性完成查询、计算、导出，并返回前端组件可消费的数据。"""
        table_data, file_path = saas_generate_payroll_api()
        # Gradio Dataframe 使用二维列表；File 组件使用本地文件路径。
        self.assertIsInstance(table_data, list)
        self.assertGreater(len(table_data), 0)
        self.assertIsNotNone(file_path)
        self.assertTrue(os.path.exists(file_path))

class TestIntegration(unittest.TestCase):
    """测试底层工具按 Agent 可能采用的顺序串联后是否仍然正确。"""
    
    def test_full_workflow(self):
        """端到端执行员工目录、工资计算、CSV 导出三个阶段。"""
        # 第一步：获取员工目录，并确认返回内容不是 error 对象。
        emp_result = get_employee_directory()
        emp_data = json.loads(emp_result)
        self.assertNotIn("error", emp_data)
        
        # 第二步：将员工目录原样传给工资计算工具，模拟 Agent 工具链传参。
        payroll_result = calculate_payroll_and_tax(emp_result)
        payroll_data = json.loads(payroll_result)
        self.assertNotIn("error", payroll_data)
        self.assertGreater(len(payroll_data), 0)
        
        # 第三步：将工资结果导出为 CSV，验证最终产物可生成。
        export_result = export_payroll_csv(payroll_result)
        export_data = json.loads(export_result)
        self.assertEqual(export_data.get("status"), "success")

def run_performance_tests():
    """运行轻量性能测试。

    这里不是严肃压测，而是给同学一个观察基线：
    纯 Python 业务函数通常极快，真正的耗时主要来自后续模型推理。
    """
    print("=" * 60)
    print("开始性能测试...")
    print("=" * 60)
    
    import time
    
    print("\n测试 get_employee_directory...")
    start_time = time.time()
    for i in range(100):
        # 读取内存模拟数据，不涉及模型调用，因此应接近瞬时完成。
        get_employee_directory()
    avg_time = (time.time() - start_time) / 100
    print(f"get_employee_directory 平均耗时: {avg_time:.4f} 秒")
    
    print("\n测试 calculate_payroll_and_tax...")
    employees = get_employee_directory()
    start_time = time.time()
    for i in range(100):
        # 重复计算相同员工集，用于观察 JSON 解析和简单薪酬计算的开销。
        calculate_payroll_and_tax(employees)
    avg_time = (time.time() - start_time) / 100
    print(f"calculate_payroll_and_tax 平均耗时: {avg_time:.4f} 秒")
    
    print("\n测试 export_payroll_csv...")
    payroll_data = calculate_payroll_and_tax(employees)
    start_time = time.time()
    for i in range(10):
        # 文件写入比纯内存计算慢，因此循环次数少一些，避免不必要的磁盘写入。
        export_payroll_csv(payroll_data)
    avg_time = (time.time() - start_time) / 10
    print(f"export_payroll_csv 平均耗时: {avg_time:.4f} 秒")
    
    print("\n" + "=" * 60)
    print("性能测试完成")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    # 命令行带 --performance 时运行性能观测，否则默认执行 unittest。
    if len(sys.argv) > 1 and sys.argv[1] == "--performance":
        run_performance_tests()
    else:
        unittest.main()
