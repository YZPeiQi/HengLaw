import json
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Dict, Optional

import mysql.connector

class CaseLibraryImporter:
    """案例库 JSONL 到 MySQL 导入器。"""
    REQUIRED_TABLES = {"case_library"}

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "demo001",
        logger: Optional[Callable[[str], None]] = None,
        auto_prepare: bool = True,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.logger = logger
        self.connection = None
        self.cursor = None

        self.connect()
        if auto_prepare:
            self.prepare_database()

    def _log(self, message: str):
        if self.logger:
            self.logger(message)
        else:
            print(message)

    def connect(self):
        try:
            self._log("[连接] 正在连接数据库服务器...")
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                autocommit=False,
            )
            self.cursor = self.connection.cursor()
            self._log("[连接] 已连接到 MySQL 服务器")
        except mysql.connector.Error as err:
            self._log(f"[错误] 数据库连接失败: {err}")
            raise

    def prepare_database(self):
        self.create_database(self.database)
        self.use_database(self.database)
        self.create_tables()

    def create_database(self, database_name: str):
        try:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            self._log(f"[数据库] {database_name} 已准备就绪")
        except mysql.connector.Error as err:
            self._log(f"[错误] 创建数据库时出错: {err}")
            raise

    def use_database(self, database_name: str):
        try:
            self.connection.database = database_name
            self._log(f"[数据库] 已切换到数据库: {database_name}")
        except mysql.connector.Error as err:
            self._log(f"[错误] 切换数据库失败: {err}")
            raise

    def create_tables(self):
        create_tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS case_library (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                case_title VARCHAR(200) COMMENT '案例标题',
                case_type VARCHAR(50) COMMENT '案例类型',
                case_date DATE COMMENT '案件发生时间',
                case_region VARCHAR(100) COMMENT '案件发生地域',
                court VARCHAR(100) COMMENT '法院',
                cited_laws JSON COMMENT '引用法条',
                case_summary TEXT COMMENT '案例摘要',
                judgment_result TEXT COMMENT '判决结果',
                judgment_reason TEXT COMMENT '判决理由',
                key_points TEXT COMMENT '关键要点',
                similar_cases JSON COMMENT '相似案例',
                case_text TEXT COMMENT '文本内容',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_case_type (case_type),
                INDEX idx_case_title (case_title),
                INDEX idx_case_date (case_date),
                UNIQUE KEY unique_case_title (case_title)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='案例库表';
            """
        ]
        
        self._log("[建表] 正在创建/校验表结构...")
        for sql in create_tables_sql:
            try:
                self.cursor.execute(sql)
                self._log("[建表] case_library 已准备")
            except mysql.connector.Error as err:
                self._log(f"[错误] 创建表失败: {err}")

        try:
            self.cursor.execute(
                """
                ALTER TABLE case_library
                MODIFY COLUMN judgment_result TEXT COMMENT '判决结果'
                """
            )
            self._log("[建表] judgment_result 字段已校验为 TEXT")
        except mysql.connector.Error as err:
            self._log(f"[错误] 修正 judgment_result 字段失败: {err}")
        
        self.connection.commit()

    def batch_process_jsonl_folder(self, folder_path: str, case_type: str, progress_callback: Optional[Callable[[int, int, str], None]] = None):
        if not os.path.exists(folder_path):
            self._log(f"[错误] 文件夹不存在: {folder_path}")
            return {"processed_files": 0, "total_files": 0, "inserted_records": 0}
        
        jsonl_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(".jsonl")]
        
        if not jsonl_files:
            self._log("[提示] 文件夹中没有找到 .jsonl 文件")
            return {"processed_files": 0, "total_files": 0, "inserted_records": 0}
        
        self._log(f"[导入] 找到 {len(jsonl_files)} 个 .jsonl 文件")
        
        total_files = len(jsonl_files)
        processed_files = 0
        total_inserted = 0
        
        for i, file_path in enumerate(jsonl_files, 1):
            try:
                file_name = os.path.basename(file_path)
                self._log(f"[导入] 处理文件 [{i}/{total_files}]: {file_name}")
                if progress_callback:
                    progress_callback(i - 1, total_files, file_name)

                inserted = self.process_single_jsonl_file(file_path, case_type)
                processed_files += 1
                total_inserted += inserted
                
                self._log(f"[导入] 完成: {file_name}")
            except Exception as e:
                self._log(f"[错误] 处理文件 {os.path.basename(file_path)} 时失败: {e}")

            if progress_callback:
                progress_callback(i, total_files, os.path.basename(file_path))
        
        self._log("[导入] 批量导入完成")
        return {"processed_files": processed_files, "total_files": total_files, "inserted_records": total_inserted}

    def process_single_jsonl_file(self, file_path: str, case_type: str):
        inserted_count = 0
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                # 将整个文件内容作为一个JSON对象加载
                content = json.load(file)
                
                # 检查内容是单个对象还是对象列表
                if isinstance(content, list):
                    # 如果是列表，遍历并插入每个对象
                    self._log(f"  文件包含 {len(content)} 条记录，准备逐条插入...")
                    for item in content:
                        if self.insert_case(item, case_type):
                            inserted_count += 1
                elif isinstance(content, dict):
                    # 如果是单个字典对象，直接插入
                    if self.insert_case(content, case_type):
                        inserted_count += 1
                else:
                    self._log(f"[警告] JSON文件根元素既不是对象也不是数组: {file_path}")

            except json.JSONDecodeError as e:
                self._log(f"[错误] 解析JSON文件失败: {e}")
            except Exception as e:
                self._log(f"[错误] 处理JSON文件时发生未知错误: {e}")

        self.connection.commit()
        return inserted_count

    def insert_case(self, data: Dict, default_case_type: str) -> bool:
        # 解析 extractions 列表
        extracted_data = {}
        if "extractions" in data and isinstance(data["extractions"], list):
            for item in data["extractions"]:
                # 1. 优先提取 attributes 中的精确结构化数据 (且只保留第一次出现的)
                if "attributes" in item and item["attributes"]:
                    for k, v in item["attributes"].items():
                        if k not in extracted_data:
                            extracted_data[k] = v
                
                # 2. 如果 attributes 没有对应的键，则降级保底使用 extraction_text (只保留第一次出现的)
                if "extraction_class" in item and "extraction_text" in item:
                    cls_name = item["extraction_class"]
                    text_val = item["extraction_text"]
                    if cls_name not in extracted_data:
                        extracted_data[cls_name] = text_val

        # 支持 jsonl 中提取出的各级别字段，优先从 extractions 里拿，拿不到再从外层拿
        case_title = extracted_data.get("case_title") or data.get("case_title") or data.get("title")
        # 由于我们使用 case_title 作为去重唯一键，如果不存在则不可插入
        if not case_title:
            return False

        case_type_val = extracted_data.get("case_type") or data.get("case_type", default_case_type) or default_case_type
        
        case_date = extracted_data.get("case_date") or data.get("case_date")
        if not case_date or str(case_date).strip() == "":
            case_date = None
            
        case_region = extracted_data.get("case_region") or data.get("case_region")
        court = extracted_data.get("court") or data.get("court")
        
        cited_laws = extracted_data.get("cited_laws")
        if not cited_laws:
            cited_laws = data.get("cited_laws", [])
        # 必须确保插入的是合法 JSON 字符串
        if isinstance(cited_laws, str):
            try:
                json.loads(cited_laws)
            except json.JSONDecodeError:
                cited_laws = json.dumps(cited_laws, ensure_ascii=False)
        else:
            cited_laws = json.dumps(cited_laws, ensure_ascii=False)
            
        case_summary = extracted_data.get("case_summary") or data.get("case_summary")
        judgment_result = extracted_data.get("judgment_result") or data.get("judgment_result")
        judgment_reason = extracted_data.get("judgment_reason") or data.get("judgment_reason")
        key_points = extracted_data.get("key_points") or data.get("key_points")
        case_text = data.get("text") # 获取 "text" 字段内容
        
        similar_cases = extracted_data.get("similar_cases")
        if not similar_cases:
            similar_cases = data.get("similar_cases", [])
        # 必须确保插入的是合法 JSON 字符串
        if isinstance(similar_cases, str):
            try:
                json.loads(similar_cases)
            except json.JSONDecodeError:
                similar_cases = json.dumps(similar_cases, ensure_ascii=False)
        else:
            similar_cases = json.dumps(similar_cases, ensure_ascii=False)

        sql = """
        REPLACE INTO case_library (
            case_title, case_type, case_date, case_region, court,
            cited_laws, case_summary, judgment_result, judgment_reason, key_points, similar_cases, case_text
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            self._log(f"[准备插入] {case_title} | 日期: {case_date}")
            self.cursor.execute(sql, (
                case_title, case_type_val, case_date, case_region, court,
                cited_laws, case_summary, judgment_result, judgment_reason, key_points, similar_cases, case_text
            ))
            return self.cursor.rowcount > 0
        except mysql.connector.Error as err:
            self._log(f"[插入错误] {case_title}: {err}")
            return False

    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None
        self._log("[连接] 数据库连接已关闭")


class CaseLibraryImporterGUI:
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "mysql_ui_config.json")

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("案例库 JSONL -> MySQL 导入工具")
        self.root.geometry("980x760")

        self.importer: Optional[CaseLibraryImporter] = None
        self.is_importing = False

        self.host_var = tk.StringVar(value="localhost")
        self.port_var = tk.StringVar(value="3306")
        self.user_var = tk.StringVar(value="root")
        self.password_var = tk.StringVar(value="")
        self.database_var = tk.StringVar(value="demo001")
        self.folder_var = tk.StringVar(value="")
        self.show_pwd_var = tk.BooleanVar(value=False)
        self.progress_var = tk.DoubleVar(value=0.0)
        self.case_type_var = tk.StringVar(value="合同纠纷")

        self._build_ui()
        self._load_config()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=14)
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(5, weight=1)

        conn_frame = ttk.LabelFrame(main, text="MySQL 连接配置", padding=10)
        conn_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        for idx in range(6):
            conn_frame.columnconfigure(idx, weight=1 if idx in (1, 3, 5) else 0)

        ttk.Label(conn_frame, text="主机:").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=4)
        ttk.Entry(conn_frame, textvariable=self.host_var).grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=4)

        ttk.Label(conn_frame, text="端口:").grid(row=0, column=2, sticky="w", padx=(0, 6), pady=4)
        ttk.Entry(conn_frame, textvariable=self.port_var, width=10).grid(row=0, column=3, sticky="ew", padx=(0, 12), pady=4)

        ttk.Label(conn_frame, text="用户:").grid(row=0, column=4, sticky="w", padx=(0, 6), pady=4)
        ttk.Entry(conn_frame, textvariable=self.user_var).grid(row=0, column=5, sticky="ew", pady=4)

        ttk.Label(conn_frame, text="密码:").grid(row=1, column=0, sticky="w", padx=(0, 6), pady=4)
        self.password_entry = ttk.Entry(conn_frame, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=4)

        ttk.Label(conn_frame, text="数据库:").grid(row=1, column=2, sticky="w", padx=(0, 6), pady=4)
        ttk.Entry(conn_frame, textvariable=self.database_var).grid(row=1, column=3, sticky="ew", pady=4)

        btn_row = ttk.Frame(conn_frame)
        btn_row.grid(row=2, column=0, columnspan=6, sticky="ew", pady=(8, 0))
        self.connect_btn = ttk.Button(btn_row, text="连接并初始化", command=self.connect_and_prepare)
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.disconnect_btn = ttk.Button(btn_row, text="断开连接", command=self.disconnect)
        self.disconnect_btn.pack(side=tk.LEFT, padx=(0, 8))

        source_frame = ttk.LabelFrame(main, text="数据源与配置", padding=10)
        source_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        source_frame.columnconfigure(1, weight=1)

        ttk.Label(source_frame, text="案件类型:").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=4)
        case_types = ["合同纠纷", "刑事案件", "婚姻家庭", "侵权责任", "劳动争议"]
        cb = ttk.Combobox(source_frame, textvariable=self.case_type_var, values=case_types, state="readonly")
        cb.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(source_frame, text="JSONL目录:").grid(row=1, column=0, sticky="w", padx=(0, 6))
        ttk.Entry(source_frame, textvariable=self.folder_var).grid(row=1, column=1, sticky="ew", padx=(0, 8))
        ttk.Button(source_frame, text="浏览", command=self.browse_folder, width=10).grid(row=1, column=2, sticky="w")

        action_frame = ttk.LabelFrame(main, text="操作", padding=10)
        action_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        self.import_btn = ttk.Button(action_frame, text="开始批量导入", command=self.start_import)
        self.import_btn.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(action_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT)

        status_frame = ttk.Frame(main)
        status_frame.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        status_frame.columnconfigure(0, weight=1)
        self.status_label = ttk.Label(status_frame, text="状态: 未连接", foreground="orange")
        self.status_label.grid(row=0, column=0, sticky="w")
        self.progress = ttk.Progressbar(status_frame, variable=self.progress_var, mode="determinate", maximum=100)
        self.progress.grid(row=1, column=0, sticky="ew", pady=(6, 0))

        log_frame = ttk.LabelFrame(main, text="日志", padding=8)
        log_frame.grid(row=5, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.log_text = tk.Text(log_frame, height=18, state="disabled", wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def _load_config(self):
        if not os.path.exists(self.CONFIG_PATH): return
        try:
            with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.host_var.set(data.get("host", self.host_var.get()))
            self.port_var.set(str(data.get("port", self.port_var.get())))
            self.user_var.set(data.get("user", self.user_var.get()))
            self.folder_var.set(data.get("folder", self.folder_var.get()))
            self.database_var.set(data.get("database", self.database_var.get()))
            self.case_type_var.set(data.get("case_type", self.case_type_var.get()))
        except Exception: pass

    def _save_config(self):
        data = {
            "host": self.host_var.get().strip(),
            "port": self.port_var.get().strip(),
            "user": self.user_var.get().strip(),
            "folder": self.folder_var.get().strip(),
            "database": self.database_var.get().strip(),
            "case_type": self.case_type_var.get().strip(),
        }
        try:
            with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception: pass

    def _toggle_password(self):
        self.password_entry.config(show="" if self.show_pwd_var.get() else "*")

    def log(self, msg: str):
        def _append():
            self.log_text.config(state="normal")
            self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state="disabled")
        self.root.after(0, _append)

    def set_status(self, text: str, color: str = "black"):
        self.root.after(0, lambda: self.status_label.config(text=f"状态: {text}", foreground=color))

    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state="disabled")

    def browse_folder(self):
        path = filedialog.askdirectory(title="选择 JSONL 文件夹")
        if path: self.folder_var.set(path)

    def connect_and_prepare(self):
        host, port_str, user, password, database = self.host_var.get(), self.port_var.get(), self.user_var.get(), self.password_var.get(), self.database_var.get()
        self.connect_btn.config(state="disabled")
        self.set_status("正在连接", "blue")
        
        def worker():
            try:
                if self.importer: self.importer.close()
                self.importer = CaseLibraryImporter(host=host, port=int(port_str), user=user, password=password, database=database, logger=self.log)
                self._save_config()
                self.set_status("已连接并完成初始化", "green")
            except Exception as exc:
                self.set_status("连接失败", "red")
                self.log(f"[错误] 连接失败: {exc}")
            finally:
                self.root.after(0, lambda: self.connect_btn.config(state="normal"))
        threading.Thread(target=worker, daemon=True).start()

    def disconnect(self):
        if self.importer:
            self.importer.close()
            self.importer = None
        self.set_status("未连接", "orange")

    def start_import(self):
        if self.is_importing or not self.importer: return
        folder = self.folder_var.get().strip()
        case_type = self.case_type_var.get()
        if not os.path.isdir(folder):
            messagebox.showerror("错误", "JSONL 文件夹不存在")
            return

        self.is_importing = True
        self.import_btn.config(state="disabled")
        self.progress_var.set(0)
        self.set_status("导入中", "blue")

        def _update(current, total, file_name):
            self.root.after(0, lambda: [self.progress_var.set((current/total)*100 if total else 0), self.status_label.config(text=f"导入中 {current}/{total}")])

        def worker():
            try:
                stats = self.importer.batch_process_jsonl_folder(folder, case_type, _update)
                self.set_status("导入完成", "green")
                self.log(f"[完成] 插入记录数: {stats['inserted_records']}")
                self.root.after(0, lambda: messagebox.showinfo("完成", f"导入完成！\n处理文件: {stats['processed_files']}\n插入记录: {stats['inserted_records']}"))
            except Exception as exc:
                self.set_status("导入失败", "red")
            finally:
                self.is_importing = False
                self.root.after(0, lambda: self.import_btn.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    def on_close(self):
        self._save_config()
        if self.importer: self.importer.close()
        self.root.destroy()

if __name__ == "__main__":
    app_root = tk.Tk()
    app = CaseLibraryImporterGUI(app_root)
    app_root.protocol("WM_DELETE_WINDOW", app.on_close)
    app_root.mainloop()
