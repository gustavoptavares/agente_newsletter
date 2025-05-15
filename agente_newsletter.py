import os
from typing import Dict, TypedDict, List, Optional
import streamlit as st
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
import requests

# ===================== Definição do Estado =====================
class NewsletterState(TypedDict):
    topics: Optional[List[Dict[str, str]]]
    selected_topic: Optional[str]
    research_materials: Optional[List[Dict[str, str]]]
    content_structure: Optional[Dict[str, List[str]]]
    draft_content: Optional[str]
    edited_content: Optional[str]
    seo_optimized_content: Optional[str]
    final_content: Optional[str]
    feedback: Optional[List[str]]

# ===================== Definições dos Agentes =====================

def agente_curacao_temas(state: NewsletterState) -> Dict[str, List[Dict[str, str]]]:
    """Agente que seleciona temas relevantes para a newsletter."""
    st.session_state['status'] = "🔍 Selecionando temas..."
    nicho = st.session_state.get('nicho', 'tecnologia e inovação')
    
    llm = ChatOpenAI(
        model=st.session_state['modelo'],
        temperature=0.7,
        api_key=st.session_state['openai_key']
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Você é um editor de newsletter sobre {nicho}. 
         Sugira 3-5 temas atuais com:
         - Título chamativo
         - Justificativa (1-2 frases)
         - Possíveis fontes"""),
        ("human", "Sugira temas para nossa próxima edição.")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"nicho": nicho})
    
    temas = []
    for linha in response.content.split("\n"):
        if linha.strip() and (linha.startswith("1.") or linha.startswith("- ")):
            partes = linha.split(":", 1)
            if len(partes) > 1:
                titulo = partes[0].replace("1.", "").replace("2.", "").replace("3.", "").replace("- ", "").strip()
                justificativa = partes[1].strip()
                temas.append({"titulo": titulo, "justificativa": justificativa})
    
    return {"topics": temas[:5]}

def selecionar_tema(state: NewsletterState) -> Dict[str, str]:
    """Seleciona o primeiro tema da lista para processamento."""
    if state['topics']:
        return {"selected_topic": state['topics'][0]['titulo']}
    return {"selected_topic": "Tema Padrão"}

def agente_pesquisa(state: NewsletterState) -> Dict[str, List[Dict[str, str]]]:
    """Coleta informações sobre o tema selecionado."""
    st.session_state['status'] = "📚 Pesquisando tema..."
    tema = state['selected_topic']
    
    llm = ChatOpenAI(
        model=st.session_state['modelo'],
        temperature=0.7,
        api_key=st.session_state['openai_key']
    )
    
    # Pesquisa via NewsAPI
    newsapi_url = f"https://newsapi.org/v2/everything?q={tema}&apiKey={st.session_state['newsapi_key']}&pageSize=3"
    try:
        news_data = requests.get(newsapi_url).json()
        artigos = news_data.get('articles', [])[:3]
    except:
        artigos = []
    
    materiais = []
    for artigo in artigos:
        materiais.append({
            "fonte": artigo.get('url', 'Desconhecida'),
            "conteudo": f"{artigo.get('title', '')}\n\n{artigo.get('description', '')}"
        })
    
    # Pesquisa com LLM
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Para o tema '{tema}', forneça:
         - 3 fatos-chave
         - 2 debates relevantes
         - 1 insight"""),
        ("human", "Pesquise sobre: {tema}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"tema": tema})
    materiais.append({"fonte": "Análise IA", "conteudo": response.content})
    
    return {"research_materials": materiais}

def agente_estruturacao(state: NewsletterState) -> Dict[str, Dict[str, List[str]]]:
    """Define a estrutura do conteúdo."""
    st.session_state['status'] = "📝 Estruturando conteúdo..."
    pesquisa = state['research_materials']
    
    llm = ChatOpenAI(
        model=st.session_state['modelo'],
        temperature=0.7,
        api_key=st.session_state['openai_key']
    )
    
    resumo = "\n".join([f"Fonte: {item['fonte']}\n{item['conteudo'][:200]}..." for item in pesquisa])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Crie uma estrutura para newsletter com:
         - Manchete
         - Introdução
         - 3-5 seções
         - Conclusão com CTA"""),
        ("human", "Pesquisa:\n{resumo}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"resumo": resumo})
    
    estrutura = {
        "manchete": "",
        "secoes": [],
        "conclusao": ""
    }
    
    for linha in response.content.split("\n"):
        if "Manchete:" in linha:
            estrutura["manchete"] = linha.split("Manchete:")[1].strip()
        elif "Seção" in linha:
            estrutura["secoes"].append(linha.split("Seção")[1].strip())
    
    return {"content_structure": estrutura}

def agente_redacao(state: NewsletterState) -> Dict[str, str]:
    """Escreve o conteúdo da newsletter."""
    st.session_state['status'] = "✍️ Escrevendo conteúdo..."
    estrutura = state['content_structure']
    tom = st.session_state.get('tom', 'profissional')
    
    llm = ChatOpenAI(
        model=st.session_state['modelo'],
        temperature=0.7,
        api_key=st.session_state['openai_key']
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Escreva uma newsletter com tom {tom} usando esta estrutura:
         {estrutura}"""),
        ("human", "Por favor, escreva o conteúdo.")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"estrutura": estrutura, "tom": tom})
    
    return {"draft_content": response.content}

def agente_edicao(state: NewsletterState) -> Dict[str, str]:
    """Edita e aprimora o conteúdo."""
    st.session_state['status'] = "🔧 Editando..."
    conteudo = state['draft_content']
    
    llm = ChatOpenAI(
        model=st.session_state['modelo'],
        temperature=0.7,
        api_key=st.session_state['openai_key']
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Edite o texto para:
         - Melhorar clareza
         - Remover redundâncias
         - Garantir tom consistente"""),
        ("human", "Texto para edição:\n{conteudo}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"conteudo": conteudo})
    
    return {"edited_content": response.content}

def agente_seo(state: NewsletterState) -> Dict[str, str]:
    """Otimiza o conteúdo para SEO."""
    st.session_state['status'] = "🔎 Otimizando SEO..."
    conteudo = state['edited_content']
    keywords = st.session_state.get('keywords', ['tecnologia'])
    
    llm = ChatOpenAI(
        model=st.session_state['modelo'],
        temperature=0.7,
        api_key=st.session_state['openai_key']
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Otimize este texto para SEO:
         - Palavras-chave: {keywords}
         - Títulos otimizados
         - Parágrafos curtos"""),
        ("human", "Texto:\n{conteudo}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"conteudo": conteudo, "keywords": keywords})
    
    return {"seo_optimized_content": response.content}

def agente_revisao(state: NewsletterState) -> Dict[str, str]:
    """Revisão final do conteúdo."""
    st.session_state['status'] = "✅ Revisando..."
    conteudo = state['seo_optimized_content']
    
    llm = ChatOpenAI(
        model=st.session_state['modelo'],
        temperature=0.7,
        api_key=st.session_state['openai_key']
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Revise o texto para:
         - Gramática e ortografia
         - Clareza
         - Consistência"""),
        ("human", "Texto para revisão:\n{conteudo}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"conteudo": conteudo})
    
    return {"final_content": response.content}

# ===================== Fluxo de Trabalho =====================
workflow = StateGraph(NewsletterState)

# Adicionar nós
workflow.add_node("curacao_temas", agente_curacao_temas)
workflow.add_node("selecionar_tema", selecionar_tema)
workflow.add_node("pesquisa", agente_pesquisa)
workflow.add_node("estruturacao", agente_estruturacao)
workflow.add_node("redacao", agente_redacao)
workflow.add_node("edicao", agente_edicao)
workflow.add_node("seo", agente_seo)
workflow.add_node("revisao", agente_revisao)

# Definir fluxo
workflow.set_entry_point("curacao_temas")
workflow.add_edge("curacao_temas", "selecionar_tema")
workflow.add_edge("selecionar_tema", "pesquisa")
workflow.add_edge("pesquisa", "estruturacao")
workflow.add_edge("estruturacao", "redacao")
workflow.add_edge("redacao", "edicao")
workflow.add_edge("edicao", "seo")
workflow.add_edge("seo", "revisao")
workflow.add_edge("revisao", END)

app = workflow.compile()

# ===================== Interface Streamlit =====================
def main():
    st.set_page_config(page_title="Newsletter AI", layout="wide")
    st.title("📰 Gerador Automático de Newsletters")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Chaves API
        st.session_state['openai_key'] = st.text_input(
            "OpenAI API Key", 
            type="password",
            value=st.session_state.get('openai_key', '')
        )
        st.session_state['newsapi_key'] = st.text_input(
            "NewsAPI Key (Opcional)", 
            type="password",
            value=st.session_state.get('newsapi_key', '')
        )
        
        # Configurações
        st.session_state['modelo'] = st.selectbox(
            "Modelo", 
            ["gpt-3.5-turbo", "gpt-4"],
            index=0
        )
        st.session_state['nicho'] = st.text_input(
            "Nicho", 
            value=st.session_state.get('nicho', 'tecnologia')
        )
        st.session_state['keywords'] = st.text_input(
            "Palavras-chave SEO (separadas por vírgula)",
            value=",".join(st.session_state.get('keywords', ['tecnologia']))
        ).split(",")
        
        if st.button("▶️ Gerar Newsletter", type="primary"):
            if not st.session_state['openai_key']:
                st.error("Chave OpenAI é obrigatória!")
            else:
                try:
                    st.session_state['resultado'] = app.invoke({})
                    st.success("✅ Newsletter gerada com sucesso!")
                except Exception as e:
                    st.error(f"Erro: {str(e)}")
    
    # Conteúdo Principal
    if 'resultado' in st.session_state:
        st.subheader("📄 Conteúdo Gerado")
        st.write(st.session_state['resultado'].get('final_content', ''))
        
        # Métricas
        st.subheader("📊 Estatísticas")
        col1, col2 = st.columns(2)
        col1.metric("Temas Gerados", len(st.session_state['resultado'].get('topics', [])))
        col2.metric("Fontes Pesquisadas", len(st.session_state['resultado'].get('research_materials', [])))

if __name__ == "__main__":
    main()