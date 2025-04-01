from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import numpy as np

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Libera CORS para todas as rotas

# Configurações
CSV_PATH = os.path.join(os.path.dirname(__file__), '..', "C:\\Users\\haris\\Desktop\\Projeto\Relatorio_cadop.csv")
COLUNAS_RELEVANTES = [
    'Registro_ANS', 'CNPJ', 'Razao_Social', 'Nome_Fantasia', 'Modalidade',
    'Logradouro', 'Numero', 'Complemento', 'Bairro', 'Cidade', 'UF', 'CEP',
    'DDD', 'Telefone', 'Endereco_eletronico'
]

def load_data():
    """Carrega e prepara os dados do CSV"""
    try:
        # Carrega o CSV com tipos específicos para evitar perda de zeros
        df = pd.read_csv(
            CSV_PATH,
            sep=';',
            encoding='utf-8',
            dtype={
                'CNPJ': 'string',
                'CEP': 'string',
                'DDD': 'string',
                'Telefone': 'string',
                'Registro_ANS': 'string'
            },
            parse_dates=['Data_Registro_ANS'],
            dayfirst=True
        )
        
        # Padroniza colunas e valores
        df.columns = df.columns.str.strip()
        df = df[COLUNAS_RELEVANTES]  # Filtra apenas colunas relevantes
        
        # Converte números para string (mantendo zeros à esquerda)
        for col in ['CNPJ', 'CEP', 'DDD', 'Telefone', 'Registro_ANS']:
            if col in df.columns:
                df[col] = df[col].astype('string').str.strip()
        
        print("✅ Dados carregados com sucesso!")
        print(f"📋 Colunas: {list(df.columns)}")
        print(f"📊 Total de registros: {len(df)}")
        print(f"🔍 Exemplo:\n{df.iloc[0].to_dict()}\n")
        
        return df
        
    except Exception as e:
        print(f"🔥 ERRO ao carregar dados: {str(e)}")
        return pd.DataFrame()

# Carrega os dados ao iniciar
df = load_data()

@app.route('/buscar', methods=['GET'])
def buscar_operadoras():
    """Endpoint principal de busca"""
    try:
        termo = request.args.get('termo', '').lower().strip()
        print(f"\n🔍 Buscando por: '{termo}'")
        
        if not termo or len(termo) < 2:
            return jsonify({
                "error": "O termo de busca deve ter pelo menos 2 caracteres",
                "termo": termo,
                "quantidade": 0,
                "resultados": []
            }), 400
            
        if df.empty:
            return jsonify({
                "error": "Base de dados não carregada",
                "termo": termo,
                "quantidade": 0,
                "resultados": []
            }), 500
        
        # Filtra os resultados (case-insensitive)
        mask = df.apply(
            lambda row: row.astype(str).str.lower().str.contains(termo).any(),
            axis=1
        )
        resultados = df[mask].head(100)  # Limita a 100 resultados
        
        # Prepara a resposta
        response_data = {
            "termo": termo,
            "quantidade": len(resultados),
            "resultados": resultados.replace({np.nan: None}).to_dict('records')
        }
        
        print(f"📤 Enviando {len(resultados)} resultados")
        if len(resultados) > 0:
            print("📄 Exemplo de registro:", response_data['resultados'][0])
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"🚨 Erro na busca: {str(e)}")
        return jsonify({
            "error": "Erro interno no servidor",
            "details": str(e),
            "termo": termo,
            "quantidade": 0,
            "resultados": []
        }), 500

@app.route('/detalhes/<registro_ans>', methods=['GET'])
def detalhes_operadora(registro_ans):
    """Endpoint para detalhes completos de uma operadora"""
    try:
        registro_ans = str(registro_ans).strip()
        resultado = df[df['Registro_ANS'] == registro_ans]
        
        if len(resultado) == 0:
            return jsonify({
                "error": "Operadora não encontrada",
                "registro_ans": registro_ans
            }), 404
            
        return jsonify(resultado.iloc[0].replace({np.nan: None}).to_dict())
        
    except Exception as e:
        return jsonify({
            "error": "Erro ao buscar detalhes",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')