import json
import pandas as pd

empresa = "HAGANA"

# Carregar os dados do JSON
with open(f'../pdf-csv/JSONs/{empresa}/{empresa}-EXTRAIDO.json', 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)

# Carregar os dados do arquivo .xlsx
xlsx_data = pd.read_excel(f'../pdf-csv/RESULTADOS/{empresa}/{empresa}-EXTRAIDO.xlsx')

# Função para obter o valor correspondente ao cabeçalho no JSON
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
                if table[i][index + 1].strip():
                    return table[i][index + 1].replace("\n", " ")
                else:
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
                    deducoes.extend([(" ".join(row[i].split(" ")[1:]), row[i + 1].replace("\n", " ")) for i in range(0, index_total - 1, 2) if row[i] and row[i + 1]])
                    return deducoes
                deducoes.extend([(" ".join(row[i].split(" ")[1:]), row[i + 1].replace("\n", " ")) for i in range(0, len(row) - 1, 2) if row[i] and row[i + 1]])
            elif "DEDUÇÕES" in row:
                iniciou_deducoes = True
    return deducoes

def extrair_dados_json(data):
    linhas_dados = []
    for page in data["pages"]:
        tables = page["tables"]

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

        linha = {
            "01 CNPJ/CEI": cnpj_cei, "02 Razão Social/Nome": razao_social, "18 CPF": cpf, "11 Nome": nome,
            "21 Tipo de Contrato": tipo_contrato, "22 Causa do Afastamento": causa_afastamento,
            "26 Data de Afastamento": data_afastamento, "TOTAL BRUTO": total_bruto, "TOTAL DEDUÇÕES": total_deducoes,
            "VALOR LÍQUIDO": valor_liquido
        }
        linha.update(dict(verbas_rescisorias_valores))
        linha.update(dict(deducoes_valores))

        linhas_dados.append(linha)
    return pd.DataFrame(linhas_dados)

# Extrair dados do JSON para DataFrame
df_json = extrair_dados_json(json_data)

# Comparar os dados do JSON e do arquivo .xlsx
def comparar_dados(df1, df2):
    inconsistencias = []
    colunas_comuns = set(df1.columns).intersection(set(df2.columns))

    for index, row in df1.iterrows():
        for coluna in colunas_comuns:
            valor_json = row[coluna]
            valor_xlsx = df2.at[index, coluna]
            if pd.isnull(valor_json) and pd.isnull(valor_xlsx):
                continue
            if str(valor_json) != str(valor_xlsx):
                inconsistencias.append({
                    "Linha": index + 1,
                    "Coluna": coluna,
                    "Valor JSON": valor_json,
                    "Valor XLSX": valor_xlsx
                })
    return inconsistencias

# Comparar os dados e imprimir inconsistências
inconsistencias = comparar_dados(df_json, xlsx_data)
if inconsistencias:
    print("Inconsistências encontradas:")
    for inconsistencia in inconsistencias:
        print(f"Linha {inconsistencia['Linha']}, Coluna '{inconsistencia['Coluna']}': JSON = {inconsistencia['Valor JSON']}, XLSX = {inconsistencia['Valor XLSX']}")
else:
    print("Nenhuma inconsistência encontrada.")