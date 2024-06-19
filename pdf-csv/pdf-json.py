import pdfplumber
import json

empresa = "HAGANA"
pdf = "TRCT Tecnologia 04.2024.pdf"

# Function to remove null values from tables
def clean_table(table):
    cleaned_table = []
    for row in table:
        cleaned_row = [cell for cell in row if cell is not None]
        cleaned_table.append(cleaned_row)
    return cleaned_table


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
            page_content = {
                "page_number": page_number,
                "text": page.extract_text() if page.extract_text() else "",
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
