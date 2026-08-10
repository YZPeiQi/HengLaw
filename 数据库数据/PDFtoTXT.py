import os
import PyPDF2
import tkinter as tk
from tkinter import filedialog

def select_folder(title):
    """Opens a dialog to select a folder."""
    print(title)
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_path = filedialog.askdirectory(title=title)
    return folder_path

def convert_pdf_to_txt(pdf_path, output_dir):
    """Converts a single PDF file to a TXT file in the specified output directory."""
    try:
        # Get the filename (without extension)
        file_name = os.path.splitext(os.path.basename(pdf_path))[0]
        # Create the full path for the output TXT file
        txt_path = os.path.join(output_dir, file_name + '.txt')

        # Open the PDF file
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Prepare a list to hold the text from all pages
            all_text = []
            
            # Iterate through each page
            for page in reader.pages:
                # Extract text using the PyPDF2 library
                text = page.extract_text()
                if text:
                    all_text.append(text)
            
            # Join the text from all pages
            merged_text = '\n'.join(all_text)
            
            # Write the merged text to the TXT file
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(merged_text)
        print(f"Successfully converted {os.path.basename(pdf_path)} to {os.path.basename(txt_path)}")
    except Exception as e:
        print(f"Could not convert {os.path.basename(pdf_path)}. Error: {e}")

def process_pdfs_in_folder(input_dir, output_dir):
    """Finds all PDF files in the input directory and converts them to TXT in the output directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # List all files in the input directory
    files = os.listdir(input_dir)
    
    # Filter for PDF files
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return

    print(f"Found {len(pdf_files)} PDF files to convert.")
    
    # Convert each PDF file
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        convert_pdf_to_txt(pdf_path, output_dir)

def main():
    # Prompt user to select input and output folders
    input_folder = select_folder("请选择包含PDF文件的文件夹")
    if not input_folder:
        print("未选择输入文件夹，程序退出。")
        return
        
    output_folder = select_folder("请选择用于存放TXT文件的文件夹")
    if not output_folder:
        print("未选择输出文件夹，程序退出。")
        return

    print(f"输入文件夹: {input_folder}")
    print(f"输出文件夹: {output_folder}")

    process_pdfs_in_folder(input_folder, output_folder)
    
    print('\n所有PDF文件转换完成！')

if __name__ == '__main__':
    main()