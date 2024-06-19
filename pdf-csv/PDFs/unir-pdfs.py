import os
from PyPDF2 import PdfMerger

empresa = "TELEMONT"

# Diretório onde estão os PDFs
diretorio = f'../PDFs/{empresa}/PDFs individuais'

# Lista para armazenar os caminhos dos arquivos PDF
arquivos_pdf = []

# Percorre o diretório em busca de arquivos PDF
for nome_arquivo in os.listdir(diretorio):
    if nome_arquivo.endswith('.pdf'):
        arquivos_pdf.append(os.path.join(diretorio, nome_arquivo))

# Cria um objeto PdfFileMerger
merger = PdfMerger()

# Combina os arquivos PDF
for arquivo_pdf in arquivos_pdf:
    merger.append(arquivo_pdf)

# Salva o arquivo combinado
merger.write(f'../PDFs/{empresa}/{empresa}-COMPLETO.pdf')
merger.close()

print('PDFs combinados com sucesso!')