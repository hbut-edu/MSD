import unittest
import json
import os
import tempfile
from app import (
    get_employee_directory,
    calculate_payroll_and_tax,
    export_payroll_csv,
    saas_generate_payroll_api
)

class TestTools(unittest.TestCase):
    """测试工具函数"""
    
    def test_get_employee_directory(self):
        """测试获取员工目录"""
        result = get_employee_directory()
        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("id", data[0])
        self.assertIn("name", data[0])
        self.assertIn("level", data[0])
    
    def test_calculate_payroll_and_tax_with_valid_data(self):
        """测试使用有效数据计算工资"""
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
        """测试使用空数据计算工资"""
        result = calculate_payroll_and_tax("")
        data = json.loads(result)
        self.assertIn("error", data)
    
    def test_calculate_payroll_and_tax_with_invalid_json(self):
        """测试使用无效 JSON 计算工资"""
        result = calculate_payroll_and_tax("invalid json")
        data = json.loads(result)
        self.assertIn("error", data)
    
    def test_calculate_payroll_and_tax_with_missing_level(self):
        """测试使用缺少 level 字段的数据计算工资"""
        employees = json.dumps([{"id": "E01", "name": "张三"}])
        result = calculate_payroll_and_tax(employees)
        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertIn("error", data[0])
    
    def test_calculate_payroll_and_tax_with_invalid_level(self):
        """测试使用无效职级计算工资"""
        employees = json.dumps([{"id": "E01", "name": "张三", "level": "L99"}])
        result = calculate_payroll_and_tax(employees)
        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertIn("error", data[0])
    
    def test_export_payroll_csv_with_valid_data(self):
        """测试使用有效数据导出 CSV"""
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
            self.assertTrue(os.path.exists(data["file_path"]))
    
    def test_export_payroll_csv_with_empty_data(self):
        """测试使用空数据导出 CSV"""
        result = export_payroll_csv("")
        data = json.loads(result)
        self.assertIn("error", data)
    
    def test_export_payroll_csv_with_invalid_json(self):
        """测试使用无效 JSON 导出 CSV"""
        result = export_payroll_csv("invalid json")
        data = json.loads(result)
        self.assertIn("error", data)

class TestSaaSController(unittest.TestCase):
    """测试 SaaS 控制器"""
    
    def test_saas_generate_payroll_api(self):
        """测试 SaaS 工资生成接口"""
        table_data, file_path = saas_generate_payroll_api()
        self.assertIsInstance(table_data, list)
        self.assertGreater(len(table_data), 0)
        self.assertIsNotNone(file_path)
        self.assertTrue(os.path.exists(file_path))

class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流"""
        emp_result = get_employee_directory()
        emp_data = json.loads(emp_result)
        self.assertNotIn("error", emp_data)
        
        payroll_result = calculate_payroll_and_tax(emp_result)
        payroll_data = json.loads(payroll_result)
        self.assertNotIn("error", payroll_data)
        self.assertGreater(len(payroll_data), 0)
        
        export_result = export_payroll_csv(payroll_result)
        export_data = json.loads(export_result)
        self.assertEqual(export_data.get("status"), "success")

def run_performance_tests():
    """运行性能测试"""
    print("=" * 60)
    print("开始性能测试...")
    print("=" * 60)
    
    import time
    
    print("\n测试 get_employee_directory...")
    start_time = time.time()
    for i in range(100):
        get_employee_directory()
    avg_time = (time.time() - start_time) / 100
    print(f"get_employee_directory 平均耗时: {avg_time:.4f} 秒")
    
    print("\n测试 calculate_payroll_and_tax...")
    employees = get_employee_directory()
    start_time = time.time()
    for i in range(100):
        calculate_payroll_and_tax(employees)
    avg_time = (time.time() - start_time) / 100
    print(f"calculate_payroll_and_tax 平均耗时: {avg_time:.4f} 秒")
    
    print("\n测试 export_payroll_csv...")
    payroll_data = calculate_payroll_and_tax(employees)
    start_time = time.time()
    for i in range(10):
        export_payroll_csv(payroll_data)
    avg_time = (time.time() - start_time) / 10
    print(f"export_payroll_csv 平均耗时: {avg_time:.4f} 秒")
    
    print("\n" + "=" * 60)
    print("性能测试完成")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--performance":
        run_performance_tests()
    else:
        unittest.main()
