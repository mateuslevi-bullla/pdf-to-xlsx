import pdfplumber
import json
import re

empresa = "DELPHOS"
pdf = "DELPHOS-COMPLETO.pdf"


# Function to remove null values from tables and clean text in each cell
def clean_table(table):
    cleaned_table = []
    for row in table:
        cleaned_row = [clean_text(cell) for cell in row if cell is not None]
        cleaned_table.append(cleaned_row)
    return cleaned_table


# Function to clean and process text
def clean_text(text):
    if text is None:
        return ""

    text = re.sub(r'\b0+(\d)', r'\1', text)
    text = re.sub(r'\s+', ' ', text).strip()

    text = text.replace('\n', ' ')

    if not text.isupper():
        text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
        text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
        text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        text = re.sub(r'([a-z]+)([A-Z][a-z]*)', r'\1 \2', text)
        text = re.sub(r'([a-zA-Z])(/)', r'\1 \2', text)
        text = re.sub(r'([a-zA-Z])(\.)', r'\1 \2', text)
        text = re.sub(r'([A-Z][a-z]+)([A-Z][a-z]+)', r'\1 \2', text)

    return text


# Function to convert PDF to JSON with table extraction and cleaning
def pdf_to_json(pdf_file_path):
    # Dictionary to store the PDF data
    pdf_data = {
        "pages": []
    }

    # Open the PDF file
    with pdfplumber.open(pdf_file_path) as pdf:
        # Iterate over each page in the PDF
        for page_number, page in enumerate(pdf.pages, start=1):
            raw_text = page.extract_text() if page.extract_text() else ""

            # Divide o texto em linhas
            lines = raw_text.split('\n')
            cleaned_lines = []
            start_cleaning = False

            # Identifica a linha "DISCRIMINAÇÃO DAS VERBAS RESCISÓRIAS"
            for line in lines:
                if "DISCRIMINAÇÃO DAS VERBAS RESCISÓRIAS" in line:
                    start_cleaning = True

                if start_cleaning:
                    cleaned_lines.append(clean_text(line))
                else:
                    cleaned_lines.append(line)

            cleaned_text = '\n'.join(cleaned_lines)

            page_content = {
                "page_number": page_number,
                "text": cleaned_text,
                "tables": []
            }

            # Extract tables from the page
            tables = page.extract_tables()
            for table in tables:
                cleaned_table = clean_table(table)
                page_content["tables"].append(cleaned_table)

            # Add the page content to the dictionary
            pdf_data["pages"].append(page_content)

    # Convert the dictionary to a JSON string
    json_data = json.dumps(pdf_data, ensure_ascii=False, indent=2)
    return json_data


# Path to the PDF file
pdf_file_path = f'../pdf-csv/PDFs/{empresa}/{pdf}'

# Convert the PDF to JSON
json_output = pdf_to_json(pdf_file_path)

# Print the JSON output
print(json_output)

# Optionally, save the JSON data to a file
with open(f'../pdf-csv/JSONs/{empresa}/{empresa}-EXTRAIDO.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_output)