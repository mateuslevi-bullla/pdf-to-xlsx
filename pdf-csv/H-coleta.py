import pdfplumber
import json
import pandas as pd

empresa = "HAGANA"
pdf = "TRCT Segurança SP 04.2024.pdf"

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

# Carregar o JSON de um arquivo
with open(f'../pdf-csv/JSONs/{empresa}/{empresa}-EXTRAIDO.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Função para obter o valor correspondente ao cabeçalho
def obter_valor(tables, cabecalho):
    for table in tables:
        for row in table:
            for cell in row:
                if cell.startswith(cabecalho):
                    return cell.replace("\n", " ")
    return None

def obter_valor_totais(tables, cabecalho):
    for table in tables:
        for i in range(len(table)):
            if cabecalho in table[i]:
                index = table[i].index(cabecalho)
                # Verificar se o valor em index + 1 é vazio ou contém apenas espaços
                if table[i][index + 1].strip():
                    # Se não for vazio, retorna o valor em index + 1
                    return table[i][index + 1].replace("\n", " ")
                else:
                    # Se for vazio, retorna o valor em index + 2
                    return table[i][index + 2].replace("\n", " ")
    return None

def obter_verbas_rescisorias(tables):
    verbas_rescisorias = []
    iniciou_verbas = False
    for table in tables:
        for row in table:
            if iniciou_verbas:
                for i in range(0, len(row) - 1, 2):
                    if row[i] and row[i + 1] and "TOTAL BRUTO" not in row[i]:
                        cabecalho = " ".join(row[i].split(" ")[1:])  # Remover o código do cabeçalho
                        valor = row[i + 1].replace("\n", " ")
                        verbas_rescisorias.append((cabecalho, valor))
                if "TOTAL BRUTO" in row:
                    return verbas_rescisorias
            elif "VERBAS RESCISÓRIAS" in row:
                iniciou_verbas = True
    return verbas_rescisorias

def obter_deducoes(tables):
    deducoes = []
    iniciou_deducoes = False
    for table in tables:
        for row in table:
            if iniciou_deducoes:
                if "TOTAL DEDUÇÕES" in row:
                    index_total = row.index("TOTAL DEDUÇÕES")
                    # Adiciona os pares de valores antes do "TOTAL DEDUÇÕES"
                    deducoes.extend([(" ".join(row[i].split(" ")[1:]), row[i + 1].replace("\n", " ")) for i in range(0, index_total - 1, 2) if row[i] and row[i + 1]])
                    return deducoes
                deducoes.extend([(" ".join(row[i].split(" ")[1:]), row[i + 1].replace("\n", " ")) for i in range(0, len(row) - 1, 2) if row[i] and row[i + 1]])
            elif "DEDUÇÕES" in row:
                iniciou_deducoes = True
    return deducoes

# Inicializar variáveis para rastrear todos os cabeçalhos
todos_cabecalhos_adicionais = set()
todos_cabecalhos_deducoes = set()
linhas_dados = []

# Processar cada página
for page in data["pages"]:
    tables = page["tables"]

    # Obter os valores dos cabeçalhos desejados
    cnpj_cei = obter_valor(tables, "01 CNPJ/CEI")
    razao_social = obter_valor(tables, "02 Razão Social/Nome")
    cpf = obter_valor(tables, "18 CPF")
    nome = obter_valor(tables, "11 Nome")
    tipo_contrato = obter_valor(tables, "21 Tipo de Contrato")
    causa_afastamento = obter_valor(tables, "22 Causa do Afastamento")
    data_afastamento = obter_valor(tables, "26 Data de Afastamento")
    total_bruto = obter_valor_totais(tables, "TOTAL BRUTO")
    total_deducoes = obter_valor_totais(tables, "TOTAL DEDUÇÕES")
    valor_liquido = obter_valor_totais(tables, "VALOR LÍQUIDO")
    verbas_rescisorias_valores = obter_verbas_rescisorias(tables)
    deducoes_valores = obter_deducoes(tables)

    cabeçalhos_adicionais = [item[0] for item in verbas_rescisorias_valores]
    valores_adicionais = [item[1] for item in verbas_rescisorias_valores]

    cabeçalhos_deducoes_adicionais = [item[0] for item in deducoes_valores]
    valores_deducoes_adicionais = [item[1] for item in deducoes_valores]

    # Atualizar os conjuntos de todos os cabeçalhos adicionais
    todos_cabecalhos_adicionais.update(cabeçalhos_adicionais)
    todos_cabecalhos_deducoes.update(cabeçalhos_deducoes_adicionais)

    # Guardar a linha de dados
    linhas_dados.append({
        "01 CNPJ/CEI": cnpj_cei, "02 Razão Social/Nome": razao_social, "18 CPF": cpf, "11 Nome": nome,
        "21 Tipo de Contrato": tipo_contrato, "22 Causa do Afastamento": causa_afastamento,
        "26 Data de Afastamento": data_afastamento, "TOTAL BRUTO": total_bruto, "TOTAL DEDUÇÕES": total_deducoes,
        "VALOR LÍQUIDO": valor_liquido, **dict(verbas_rescisorias_valores), **dict(deducoes_valores)
    })

# Ordenar os cabeçalhos adicionais para consistência
todos_cabecalhos_adicionais = sorted(todos_cabecalhos_adicionais)
todos_cabecalhos_deducoes = sorted(todos_cabecalhos_deducoes)

# Criar DataFrame do pandas para os dados
df = pd.DataFrame(linhas_dados)

# Filtrar as colunas para remover aquelas com cabeçalho vazio
df = df[[coluna for coluna in df.columns if coluna.strip() != ""]]

# Reordenar as colunas para garantir a consistência
colunas_principais = [
    "01 CNPJ/CEI", "02 Razão Social/Nome", "18 CPF", "11 Nome",
    "21 Tipo de Contrato", "22 Causa do Afastamento",
    "26 Data de Afastamento", "TOTAL BRUTO", "TOTAL DEDUÇÕES", "VALOR LÍQUIDO"
]

# Assegurar que apenas as colunas presentes no DataFrame sejam incluídas
colunas_final = colunas_principais + [col for col in todos_cabecalhos_adicionais if col in df.columns] + [col for col in todos_cabecalhos_deducoes if col in df.columns]
df = df[colunas_final]

# Exportar para arquivo Excel
df.to_excel(f'../pdf-csv/RESULTADOS/{empresa}/{empresa}-EXTRAIDO.xlsx', index=False)