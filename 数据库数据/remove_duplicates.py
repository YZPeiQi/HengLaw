import os
import json
import glob
import tkinter as tk
from tkinter import filedialog, messagebox
import threading

def process_file(filepath, output_folder, log_callback):
    """处理单个 JSONL 文件的去重逻辑并写入新文件夹"""
    filename = os.path.basename(filepath)
    output_path = os.path.join(output_folder, filename)
    
    output_lines = []
    modified = False

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                
                data = json.loads(line)
                if 'extractions' in data:
                    best_extractions = {}
                    
                    # 去重与优选逻辑
                    for ext in data['extractions']:
                        ext_class = ext.get('extraction_class')
                        if not ext_class:
                            continue
                        
                        if ext_class not in best_extractions:
                            best_extractions[ext_class] = ext
                        else:
                            existing_ext = best_extractions[ext_class]
                            # 如果之前存的是 char_interval 为 null，而当前的不是 null，则覆盖
                            if existing_ext.get('char_interval') is None and ext.get('char_interval') is not None:
                                best_extractions[ext_class] = ext
                    
                    # 组合成列表并按原有 index 排序
                    deduplicated = list(best_extractions.values())
                    deduplicated.sort(key=lambda x: x.get('extraction_index', 0))
                    
                    if len(deduplicated) != len(data['extractions']):
                        modified = True
                    
                    data['extractions'] = deduplicated
                    
                output_lines.append(json.dumps(data, ensure_ascii=False))
                
        # 写入到输出文件夹中
        with open(output_path, 'w', encoding='utf-8') as f:
            for out_line in output_lines:
                f.write(out_line + '\n')
        
        if modified:
            log_callback(f"✅ 已去重并保存: {filename}\n")
        else:
            log_callback(f"ℹ️ 无需去重原样保存: {filename}\n")
            
    except Exception as e:
        log_callback(f"❌ 处理 {filename} 时出错: {e}\n")


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("JSONL 提取数据去重工具")
        self.root.geometry("650x450")
        
        # --- 输入文件夹选择区 ---
        tk.Label(root, text="输入文件夹:").grid(row=0, column=0, padx=10, pady=15, sticky="e")
        self.input_var = tk.StringVar()
        tk.Entry(root, textvariable=self.input_var, width=60).grid(row=0, column=1, padx=5, pady=15)
        tk.Button(root, text="浏览...", command=self.browse_input).grid(row=0, column=2, padx=10, pady=15)
        
        # --- 输出文件夹选择区 ---
        tk.Label(root, text="输出文件夹:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.output_var = tk.StringVar()
        tk.Entry(root, textvariable=self.output_var, width=60).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(root, text="浏览...", command=self.browse_output).grid(row=1, column=2, padx=10, pady=5)
        
        # --- 操作按钮 ---
        self.run_btn = tk.Button(root, text="🚀 开始处理", command=self.run_process, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.run_btn.grid(row=2, column=1, pady=20)
        
        # --- 日志显示区 ---
        self.log_text = tk.Text(root, height=15, width=80, bg="#f4f4f4")
        self.log_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
        
    def browse_input(self):
        folder = filedialog.askdirectory(title="选择包含 JSONL 的输入文件夹")
        if folder:
            self.input_var.set(folder)
            
    def browse_output(self):
        folder = filedialog.askdirectory(title="选择保存结果的输出文件夹")
        if folder:
            self.output_var.set(folder)
            
    def log(self, message):
        """线程安全的日志更新"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        
    def run_process(self):
        input_folder = self.input_var.get().strip()
        output_folder = self.output_var.get().strip()
        
        if not input_folder or not os.path.isdir(input_folder):
            messagebox.showerror("路径错误", "请选择有效的输入文件夹！")
            return
        
        if not output_folder:
            messagebox.showerror("路径错误", "请指定输出文件夹！")
            return
            
        # 如果输出文件夹不存在则自动创建
        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
            except Exception as e:
                messagebox.showerror("创建文件夹失败", f"无法创建输出文件夹: {e}")
                return
        
        # 清空日志框，禁用按钮放重复点击
        self.log_text.delete(1.0, tk.END)
        self.run_btn.config(state=tk.DISABLED, text="⏳ 处理中...")
        
        # 在单独的线程中运行处理逻辑，避免卡死界面
        def task():
            search_pattern = os.path.join(input_folder, "*.jsonl")
            jsonl_files = glob.glob(search_pattern)
            
            if not jsonl_files:
                self.root.after(0, self.log, f"⚠️ 在输入文件夹中没有找到任何 .jsonl 文件。\n")
            else:
                self.root.after(0, self.log, f"🔍 找到 {len(jsonl_files)} 个 JSONL 文件，开始处理...\n\n")
                for filepath in jsonl_files:
                    # 使用 lambda 通过 after 方法安全地更新 GUI 
                    process_file(filepath, output_folder, lambda msg: self.root.after(0, self.log, msg))
                self.root.after(0, self.log, "\n🎉 所有文件处理完成！\n")
                
            # 恢复按钮状态
            self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL, text="🚀 开始处理"))
            
        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()