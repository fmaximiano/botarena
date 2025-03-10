import pandas as pd
import json

def excel_to_json(file_path):
    # Carrega todas as abas do arquivo Excel em um dicionário
    excel_data = pd.read_excel(file_path, sheet_name=None)
    
    # Dicionário para armazenar o JSON final
    final_json = {}
    
    # Itera por cada aba (tabela) no arquivo Excel
    for sheet_name, data in excel_data.items():
        # Inicializa uma lista para armazenar as entradas desta aba
        entries = []
        
        # Itera por cada linha da tabela
        for _, row in data.iterrows():
            # Cria um dicionário para cada entrada com 'input' e 'output'
            entry = {
                "input": row[0],  # Nome da coluna 'input_example'
                "output": row[1]  # Nome da coluna 'suggested_output'
            }
            # Adiciona a entrada à lista de entradas
            entries.append(entry)
        
        # Adiciona as entradas ao JSON final sob o nome da aba
        final_json[sheet_name] = {
            "entries": entries
        }
    
    # Converte o dicionário final para JSON
    json_data = json.dumps(final_json, indent=4, ensure_ascii=False)
    
    return json_data

# Exemplo de uso
file_path = './avbot.xlsx'
json_output = excel_to_json(file_path)

# Salvar o JSON em um arquivo
with open('output.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_output)    

print("Conversão concluída. JSON salvo em 'output.json'.")
