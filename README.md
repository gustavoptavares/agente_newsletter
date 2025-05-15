# 📰 Agente Gerador de Newsletters com IA

Este projeto implementa um agente de inteligência artificial baseado em LangGraph para automatizar a criação de newsletters informativas a partir de temas definidos. O agente utiliza modelos de linguagem para pesquisar, analisar e compor conteúdos ricos, prontos para distribuição por e-mail, blogs ou redes sociais.

---

## 📌 Visão Geral

O agente implementado neste repositório foi desenvolvido com o objetivo de automatizar o processo de criação de newsletters temáticas. Utilizando a biblioteca **LangGraph** e um modelo LLM (OpenAI), o agente é capaz de:

- Realizar pesquisas em tempo real sobre temas diversos;
- Sintetizar e organizar as informações coletadas;
- Estruturar o conteúdo em formato de newsletter;
- Gerar textos envolventes e informativos, prontos para publicação.

---

## ❓ Problema e Solução

### Problema

A criação de newsletters informativas e de qualidade demanda tempo, pesquisa e habilidades de redação. Empresas e criadores de conteúdo enfrentam dificuldades em manter consistência, qualidade e frequência nesse tipo de publicação.

### Solução

A solução proposta automatiza o processo com um agente inteligente capaz de:

- **Compreender o tema proposto pelo usuário**;
- **Buscar referências e realizar análises iniciais**;
- **Redigir uma newsletter bem estruturada**;
- **Entregar o conteúdo final de forma eficiente**.

---

## ⚙️ Processo

O código segue os princípios de construção de grafos de agentes com o LangGraph. O processo pode ser descrito em etapas:

### 1. Configuração dos Modelos

- Utiliza um modelo de linguagem natural (`ChatOpenAI`) via OpenAI;
- Configura o `RunnableConfig` com `thread_id` para rastreamento.

### 2. Definição das Funções (Nodes do Grafo)

- **`pesquisar_tema`**: realiza uma análise geral do tema proposto.
- **`analisar_noticias`**: busca e organiza dados relevantes sobre o tema.
- **`estruturar_conteudo`**: transforma as informações em estrutura de newsletter.
- **`escrever_newsletter`**: gera o texto final pronto para distribuição.

### 3. Construção do Grafo

- Utiliza `StateGraph` para montar o fluxo entre os nós;
- O estado inicial contém o tema da newsletter;
- O fluxo se dá de forma sequencial: pesquisa → análise → estruturação → escrita.

### 4. Execução

O grafo é compilado e executado com o método `.invoke()` sobre um dicionário que contém o tema escolhido.

### 5. Fluxo de Decisão dos Agentes

<div align="center">
<img src="https://github.com/gustavoptavares/agente_nl2sql/blob/main/Fluxo%20de%20decisao.png" alt="Fluxo do Agente" width="500"/>
</div>

| Agente      | Critério de Decisão                     | Ação em Caso de Falha                          |
|-------------|-----------------------------------------|------------------------------------------------|
| Curadoria   | Relevância > Novidade > Diversidade     | Retorna lista mínima (3 temas)                 |
| Pesquisa    | Confiabilidade da fonte > Atualidade    | Usa apenas análise do LLM se API falhar        |
| Estrutura   | Balanceamento seções > Progressão lógica| Mantém estrutura padrão (4 seções)             |
| Redator     | Adequação ao tom > Engajamento          | Repete com temperatura=0.3 se incoerente       |
| Editor      | Clareza > Concisão                      | Mantém original se edição piorar avaliação     |
| SEO         | Densidade keywords > Legibilidade       | Prioriza legibilidade sobre SEO                |
| Revisor     | Correção > Consistência                 | Destaca problemas sem alterar se crítico       |

---

## 📈 Resultados

A saída do agente é uma newsletter coesa, estruturada e pronta para uso. Por exemplo, ao executar com o tema `"impacto da IA na medicina moderna"`, o agente produz:

- Introdução informativa e envolvente;
- Destaques de pesquisas recentes e aplicações reais da IA na medicina;
- Considerações sobre ética e futuro da tecnologia na saúde;
- Texto claro e adaptado ao público geral.

---

## ✅ Conclusões

Este projeto demonstra o poder da IA generativa combinada com estruturas orientadas a fluxo como o LangGraph. Os principais benefícios incluem:

- **Automação inteligente**: reduz o tempo necessário para produzir conteúdo de alta qualidade.
- **Escalabilidade**: pode ser integrado em plataformas maiores de marketing ou CRM.
- **Flexibilidade**: adapta-se a qualquer tema definido pelo usuário.

O agente gerador de newsletters é uma ferramenta poderosa para empresas, educadores, jornalistas e criadores de conteúdo que buscam manter comunicação constante e relevante com seu público.

---

## ▶️ Como Executar

**Instalação dos pacotes necessários**

```bash
pip install streamlit langchain-openai langgraph requests
```

**Execução do app Streamlit**
```bash
streamlit run nome_do_arquivo.py
```

**Tela do Deploy**

<p align="center">
  <img src="https://github.com/gustavoptavares/agente_nl2sql/blob/main/Deploy%201.jpg" alt="Imagem 1" width="500"/>
</p>
