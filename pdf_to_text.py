import os
from pdfminer.high_level import extract_text

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def process_pdf_to_text(input_pdf_path):
    if not os.path.isfile(input_pdf_path):
        print(f"Error: File {input_pdf_path} not found.")
        return

    # Extract text from PDF
    text = extract_text(input_pdf_path)
    if not text:
        print("Error: Failed to extract text from PDF.")
        return

    # Prepare output file path
    output_txt_path = os.path.splitext(input_pdf_path)[0] + '.txt'

    # Save extracted text to a .txt file
    with open(output_txt_path, 'w', encoding='utf-8') as text_file:
        text_file.write(text)
    
    print(f"Text extracted and saved successfully to {output_txt_path}")

if __name__ == '__main__':
    # Example usage
    filename = "_YAHYAGHANI_.pdf"  # Replace with actual PDF file name

    input_pdf_path = os.path.abspath(filename)

    process_pdf_to_text(input_pdf_path)
