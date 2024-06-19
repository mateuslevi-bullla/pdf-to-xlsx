import json
import pandas as pd

empresa = "ALMAVIVA"


# Carregar o JSON de um arquivo
with open(f'../pdf-csv/JSONs/{empresa}/{empresa}-EXTRAIDO.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Função para obter o valor correspondente ao cabeçalho
def obter_valor(tables, cabecalho):
    for table in tables:
        for row in table:
            for cell in row:
                if cell.startswith(cabecalho):
                    return cell.split("\n")[1]
    return None

def obter_valor_totais(tables, cabecalho):
    for table in tables:
        for row in table:
            if cabecalho in row:  # Verificar se o cabeçalho está presente na linha
                index_cabecalho = row.index(cabecalho)  # Localizar a posição do cabeçalho na linha
                valor_string = row.split(":")[1].strip()  # Extrair a string após o cabeçalho
                valor = valor_string.split()[0]  # Extrair o valor da string
                return valor
    return None

def obter_verbas_rescisorias(tables):
    verbas_rescisorias = []
    iniciou_verbas = False
    for table in tables:
        for row in table:
            if iniciou_verbas:
                for i in range(0, len(row) - 1, 2):
                    if row[i] and row[i + 1] and "TOTAL BRUTO" not in row[i]:
                        cabecalho = " ".join(row[i].split(" ")[1:]) # Remover o código do cabeçalho
                        verbas_rescisorias.append((cabecalho, row[i + 1]))
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
                    deducoes.extend([(" ".join(row[i].split(" ")[1:]), row[i + 1]) for i in range(0, index_total - 1, 2) if row[i] and row[i + 1]])
                    return deducoes
                deducoes.extend([(" ".join(row[i].split(" ")[1:]), row[i + 1]) for i in range(0, len(row) - 1, 2) if row[i] and row[i + 1]])
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
    causa_afastamento = obter_valor(tables, "25 Causa do afastamento")
    data_afastamento = obter_valor(tables, "24 Data de afastamento")
    total_de_proventos = obter_valor_totais(tables, "Total de Proventos")
    total_de_descontos = obter_valor_totais(tables, "Total de Descontos")
    valor_liquido_recisao = obter_valor_totais(tables, "Valor Liquido Recisão")
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
        "26 Data de Afastamento": data_afastamento, "Total de Proventos": total_de_proventos, "Total de Descontos": total_de_descontos,
        "Valor Líquido Recisão": valor_liquido_recisao, **dict(verbas_rescisorias_valores), **dict(deducoes_valores)
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
    "26 Data de Afastamento", "Total de Proventos", "Total de Descontos", "Valor Líquido Recisão"
]

# Assegurar que apenas as colunas presentes no DataFrame sejam incluídas
colunas_final = colunas_principais + [col for col in todos_cabecalhos_adicionais if col in df.columns] + [col for col in todos_cabecalhos_deducoes if col in df.columns]
df = df[colunas_final]

# Exportar para arquivo Excel
df.to_excel(f'../pdf-csv/RESULTADOS/{empresa}/{empresa}-EXTRAIDO.xlsx', index=False)