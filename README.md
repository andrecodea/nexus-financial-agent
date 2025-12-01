## 🤖 NEXUS Financial Agent 

> **Case Técnico Dreamsquad:** API de Chat com Agente de IA Financeiro.

O NEXUS é um agente financeiro desenvolvido para o desafio técnico da Dreamsquad, projetado para realizar cálculos matemáticos e consultas de mercado via ferramentas externas. A solução utiliza uma arquitetura híbrida com FastAPI no backend e Streamlit no frontend, orquestrando o modelo Llama 3.1 (via Ollama) através do Strands Agents SDK. O projeto executa localmente e aplica técnicas de engenharia de prompt, Few-Shot e notação orientada a objetos (TOON), para estruturar o uso de ferramentas Python (yfinance e math) e validar as respostas do modelo.

---

## Arquitetura do Projeto

Para cumprir os requisitos e demonstrar conhecimentos além do básico, o projeto utiliza uma arquitetura em duas camadas:

1.  **Backend (Obrigatório):** API REST construída com *FastAPI*, responsável por gerenciar o *Strands Agents SDK* e a comunicação com o *Ollama*.
2.  **Frontend (Diferencial):** Interface interativa em *Streamlit*, permitindo chat amigável e visualização de gráficos de ações (Dashboard), consumindo a API do backend.

### Fluxo de Dados
```mermaid
[Usuário] -> [Streamlit Frontend] -> (HTTP POST) -> [FastAPI Backend] -> [Strands Agent] -> [Ollama (Llama 3.1)]
```

## Pré-requisitos
Antes de iniciar, certifique-se de ter instalado:
- Python 3.10+Ollama (Rodando localmente)
- Configuração do Modelo (Crítico)
- Este projeto utiliza Tool Calling (uso de ferramentas). Para isso, é necessário o modelo Llama 3.1 (o Llama 3.0 possui limitações nesta função).Instale o Ollama em ollama.com.No seu terminal, baixe o modelo correto:Bashollama pull llama3.1

## Instalação Passo a Passo
1. Clonar e Criar Ambiente VirtualBash# Clone o repositório
```bash
 git clone https://github.com/andrecodea/nexus-financial-agent.git
cd nexus-financial-agent

# Crie o ambiente virtual
```python -m venv venv```

# Ative o ambiente (Windows)
.\venv\Scripts\activate

# Ative o ambiente (Linux/Mac)
source venv/bin/activate
```
2. Instalar Dependências 
```bash
Bashpip install -r requirements.txt
```

3. Configurar Variáveis de Ambiente
Crie um arquivo chamado .env na raiz do projeto e adicione as configurações abaixo:
```Ini, TOML
OLLAMA_HOST=http://localhost:11434
MODEL_NAME=llama3.1
```

## Como Executar o Projeto
Para a experiência completa, você precisará de dois terminais abertos simultaneamente (ambos com o venv ativado).
1. **Iniciar o backend**: No primeiro terminal, inicie o servidor FastAPI. Ele ficará escutando na porta 8000. ```uvicorn app.main:app --reload```
2. **Aguarde a mensagem**: Application startup complete.
3. **Iniciar o frontend**: Abra um novo terminal, ative o venv (.\venv\Scripts\activate) e inicie a interface visual:```streamlit run frontend/app.py```
4. O navegador abrirá automaticamente no endereço http://localhost:8501.

## Exemplos de Uso
O Agente NEXUS foi treinado para identificar intenções e usar ferramentas específicas. Tente perguntar:

| Intenção | Exemplo de Pergunta | Tool Acionada |
| :--- | :--- | :--- |
| **Cálculo Matemático** | "Quanto é 1234 vezes 5678?" | `calculate_math_expression` |
| **Matemática Python** | "Qual a raiz quadrada de 144?" | `calculate_math_expression` (usa `math.sqrt`) |
| **Cotação de Ações** | "Qual o preço da ação PETR4.SA?" | `get_ticker_price` |
| **Investimentos** | "Quanto rende 1000 reais a 10% por 5 anos?" | `calculate_compound_interest` |

## Estrutura de Arquivos
```
nexus-financial-agent/
│
├── app/                    # Núcleo da Aplicação
│   ├── main.py             # Servidor API (FastAPI)
│   ├── agent.py            # Configuração do Agente e Prompts
│   └── tools.py            # Ferramentas (Lógica de Cálculo e Mercado)
│
├── frontend/               # Interface Visual
│   └── app.py              # Aplicação Streamlit
│
├── .env                    # Variáveis de Ambiente (Config Ollama)
├── .gitignore              # Arquivos ignorados pelo Git
├── requirements.txt        # Lista de bibliotecas
└── README.md               # Documentação do Projeto
```
⚠️ Solução de Problemas ComunsErro ConnectionRefused ou ConnectionError:Verifique se o Ollama está rodando no seu computador (ícone na barra de tarefas ou ollama serve).Verifique se o terminal do Backend (uvicorn) está aberto e sem erros.Erro llama3:latest does not support tools:Você está usando a versão antiga do modelo. Rode ollama pull llama3.1 e atualize seu arquivo .env.Erro ModuleNotFoundError:Você provavelmente esqueceu de ativar o ambiente virtual (.\venv\Scripts\activate) antes de rodar os comandos.
