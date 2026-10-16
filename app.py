"""
MIT License

Copyright (c) 2026 Marcelo Antonio Maffeis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import streamlit as st
from openai import AzureOpenAI
import json

# ==============================================================================
# 🔐 INSTRUÇÕES DIDÁTICAS PARA OS ALUNOS (BOAS PRÁTICAS DE SEGURANÇA)
# ==============================================================================
# ATENÇÃO ALUNOS: 
# Para projetos reais e repositórios no GitHub, NUNCA deixe chaves de API 
# (API_KEY) expostas no código fonte. 
#
# Para proteger suas credenciais no Streamlit, siga estes passos:
# 1. Crie uma pasta chamada '.streamlit' na raiz do seu projeto.
# 2. Dentro dela, crie um arquivo chamado 'secrets.toml'.
# 3. Adicione suas chaves no arquivo assim:
#    AZURE_OPENAI_KEY = "sua_chave_aqui"
#    AZURE_OPENAI_ENDPOINT = "seu_endpoint_aqui"
# 4. No código, chame as variáveis usando: st.secrets["AZURE_OPENAI_KEY"]
# ==============================================================================

# Credenciais do Microsoft Foundry (Inseridas diretamente para fins de laboratório)
API_KEY = "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os"
ENDPOINT = "https://marcelomaffeis-05082026-resource.services.ai.azure.com/"
MEU_MODELO = "gpt-4.1-mini"
API_VERSION = "2024-02-15-preview" # Versão padrão recomendada para a API do Azure

# Inicialização do Cliente Azure OpenAI
client = AzureOpenAI(
    api_key=API_KEY,
    api_version=API_VERSION,
    azure_endpoint=ENDPOINT
)

# Configuração visual da página
st.set_page_config(
    page_title="Extrator de Dados Inteligente", 
    page_icon="🧠", 
    layout="centered"
)

st.title("🧠 Extrator de Dados Inteligente")
st.markdown("Insira um texto abaixo. A IA irá processar o conteúdo e extrair informações estruturadas automaticamente.")

# Área de entrada de dados
texto_usuario = st.text_area("Texto para análise:", height=150, placeholder="Cole ou digite o texto aqui...")

# Botão de processamento
if st.button("Processar", type="primary"):
    if texto_usuario.strip():
        with st.spinner("Conectando à infraestrutura da Microsoft e analisando o texto..."):
            try:
                # O System Prompt é a alma da extração: regras rígidas para garantir o formato JSON
                system_prompt = """
                Você é um arquiteto de dados e assistente especialista em análise de texto.
                Sua tarefa é analisar o texto fornecido pelo usuário e retornar EXCLUSIVAMENTE um objeto JSON válido.
                Não adicione nenhuma formatação Markdown (como ```json) ao redor da resposta. Apenas o JSON puro.
                
                O JSON deve conter exatamente as seguintes chaves:
                - "sentimento": string (ex: Positivo, Negativo, Neutro).
                - "porcentagem_sentimento": inteiro (de 0 a 100, indicando a intensidade do sentimento detectado).
                - "assunto_principal": string resumindo o tema central do texto.
                - "pessoas_citadas": array de strings com os nomes das pessoas mencionadas (use lista vazia [] se não houver).
                - "nivel_de_urgencia": string restrita aos valores exatos: "Baixo", "Medio" ou "Alto".
                """

                # Chamada para o Azure OpenAI
                response = client.chat.completions.create(
                    model=MEU_MODELO,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": texto_usuario}
                    ],
                    # Força o modelo a responder em formato JSON (requer suporte do modelo selecionado)
                    response_format={"type": "json_object"}, 
                    temperature=0.1 # Temperatura baixa para respostas mais precisas e determinísticas
                )

                # Extração da resposta e conversão de string para dicionário Python
                resultado_texto = response.choices[0].message.content
                dados_extraidos = json.loads(resultado_texto)

                st.success("Análise concluída com sucesso!")

                # ==============================================================================
                # INTERFACE DE EXIBIÇÃO ESTRUTURADA
                # ==============================================================================
                st.markdown("### 📊 Indicadores Principais")
                
                # Utilizando st.metric para exibir os KPIs de forma moderna
                col1, col2, col3 = st.columns(3)
                col1.metric("Sentimento", dados_extraidos.get("sentimento", "N/A"))
                col2.metric("Intensidade (%)", f"{dados_extraidos.get('porcentagem_sentimento', 0)}%")
                
                # Lógica de cor para o nível de urgência
                urgencia = dados_extraidos.get("nivel_de_urgencia", "N/A")
                if urgencia == "Alto":
                    col3.error(f"Urgência: {urgencia}")
                elif urgencia == "Medio":
                    col3.warning(f"Urgência: {urgencia}")
                else:
                    col3.success(f"Urgência: {urgencia}")

                st.markdown("### 📋 Assunto Central")
                st.info(dados_extraidos.get("assunto_principal", "N/A"))

                st.markdown("### 👥 Pessoas Mencionadas")
                pessoas = dados_extraidos.get("pessoas_citadas", [])
                if pessoas:
                    for pessoa in pessoas:
                        st.markdown(f"- **{pessoa}**")
                else:
                    st.write("Nenhuma pessoa foi detectada no texto.")

                st.markdown("---")
                st.markdown("### 📦 Resposta Raw (JSON)")
                # Exibe o objeto JSON cru para inspeção técnica
                st.json(dados_extraidos)

            except json.JSONDecodeError:
                st.error("Falha no processamento: O modelo não retornou um JSON válido. Verifique o System Prompt.")
            except Exception as e:
                st.error(f"Erro na comunicação com a API do Azure: {e}")
    else:
        st.warning("O campo de texto está vazio. Por favor, insira um texto para processar o fluxo Entrada-Processamento-Saída.")
