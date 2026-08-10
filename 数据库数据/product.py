import json
import os
import mysql.connector
from typing import List, Dict, Any

CASE_FIELDS = [
    "case_title",
    "case_type",
    "case_date",
    "case_region",
    "court",
    "cited_laws",
    "case_summary",
    "judgment_result",
    "judgment_reason",
    "key_points",
    "similar_cases",
    "case_text",
]

class CaseLibraryExporter:
    """从 MySQL 数据库导出案例库数据。"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "demo001",
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        print("[初始化] 导出器已配置。")

    def connect(self):
        """连接到 MySQL 数据库。"""
        try:
            print("[连接] 正在连接到数据库...")
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            # 使用字典光标以获取带列名的结果
            self.cursor = self.connection.cursor(dictionary=True)
            print("[连接] 成功连接到数据库。")
            return True
        except mysql.connector.Error as err:
            print(f"[错误] 数据库连接失败: {err}")
            return False

    def fetch_all_cases(self) -> List[Dict[str, Any]]:
        """从 case_library 表中获取所有记录。"""
        if not self.cursor:
            print("[错误] 未连接到数据库。")
            return []
        
        try:
            print("[查询] 正在从 'case_library' 表中获取数据...")
            fields_sql = ", ".join(CASE_FIELDS)
            self.cursor.execute(f"SELECT {fields_sql} FROM case_library")
            results = self.cursor.fetchall()
            print(f"[查询] 成功获取 {len(results)} 条记录。")
            
            # 对结果进行后处理，以确保所有字段都是可序列化的
            for row in results:
                for key, value in row.items():
                    # 将 datetime 或 date 对象转换为 ISO 格式字符串
                    if hasattr(value, 'isoformat'):
                        row[key] = value.isoformat()
                    # 尝试解析 JSON 字符串字段
                    if key in ('cited_laws', 'similar_cases') and isinstance(value, str):
                        try:
                            row[key] = json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            # 如果解析失败，保留原始字符串
                            pass
            return results
        except mysql.connector.Error as err:
            print(f"[错误] 查询数据失败: {err}")
            return []

    def export_to_json(self, output_path: str):
        """将所有案例数据导出到指定的 JSON 文件。"""
        if not self.connect():
            return

        cases = self.fetch_all_cases()
        if not cases:
            print("[导出] 没有数据可导出。")
            self.close()
            return

        try:
            print(f"[导出] 正在将数据写入到: {output_path}")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(cases, f, ensure_ascii=False, indent=4)
            print(f"[导出] 数据成功导出到 {output_path}")
        except IOError as e:
            print(f"[错误] 写入文件失败: {e}")
        finally:
            self.close()

    def close(self):
        """关闭数据库连接。"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("[连接] 数据库连接已关闭。")


if __name__ == "__main__":
    # 获取脚本所在的目录
    script_dir = os.path.dirname(__file__)
    
    # 定义输出文件的路径
    output_file_path = os.path.join(script_dir, "exported_cases.json")

    # 创建导出器实例 (如有需要，请修改这里的数据库连接参数)
    exporter = CaseLibraryExporter(
        host="localhost",
        port=3306,
        user="root",
        password="123456",  # 您的数据库密码
        database="demo001"   # 您的数据库名称
    )

    # 执行导出
    exporter.export_to_json(output_file_path)
