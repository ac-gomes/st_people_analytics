# People Analytics

Dashboard interativo para análise de pessoas, desenvolvido com Python, Pandas, Plotly e Streamlit. O projeto reúne indicadores de colaboradores, desempenho, jornada de trabalho, recrutamento, turnover e inteligência de talentos.

## Requisitos

- Git
- Python 3.8 ou superior
- Acesso ao terminal
- Um navegador web atualizado

O projeto utiliza arquivos CSV locais como fonte de dados. Eles já estão incluídos no diretório `data/`.

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/ac-gomes/st_people_analytics.git
cd st_people_analytics
```

### 2. Criar um ambiente virtual

No Linux ou macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

No Windows usando o Prompt de Comando:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
```

Quando o ambiente estiver ativo, o nome `.venv` aparecerá no início da linha do terminal.

### 3. Instalar as dependências

Linux ou macOS:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

Windows:

```powershell
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

## Executar a aplicação

Na raiz do projeto, com o ambiente virtual ativado, execute:

```bash
streamlit run app.py
```

O Streamlit exibirá um endereço semelhante a `http://localhost:8501`. Abra esse endereço no navegador. Caso ele não seja aberto automaticamente, copie e cole a URL na barra de endereços.

Para encerrar a aplicação, volte ao terminal e pressione `Ctrl+C`.

## Como usar o dashboard

A navegação fica disponível na barra lateral. Selecione uma das páginas abaixo:

- **Executive Dashboard**: visão geral de headcount, colaboradores ativos, turnover e receita por colaborador.
- **Performance Analytics**: avaliação de desempenho, eNPS, receita média e participação em treinamentos.
- **Workforce Analytics**: horas extras, horas ausentes, absenteísmo, índice de Bradford e indicador de burnout.
- **Recruitment Analytics**: contratações, custo por contratação, tempo para preencher a vaga, qualidade da contratação e ROI por fonte.
- **Turnover Analytics**: turnover geral, voluntário, involuntário e desligamentos nos primeiros 90 dias.
- **Talent Intelligence**: análises de risco de saída, burnout, potencial de promoção e retorno sobre o investimento em pessoas.

Algumas páginas possuem filtros na barra lateral, como departamento, senioridade, status, participação em treinamento ou fonte de aquisição. Os gráficos e os indicadores são atualizados conforme os filtros selecionados.

## Estrutura do projeto

```text
.
├── app.py                         # Ponto de entrada do Streamlit
├── requirements.txt               # Dependências Python
├── data/                          # Bases CSV utilizadas pelo dashboard
│   ├── tb_colaboradores.csv
│   ├── tb_desempenho.csv
│   ├── tb_jornada.csv
│   └── tb_recrutamento.csv
└── src/                           # Módulos das páginas e componentes
	├── executive_dashboard.py
	├── performance_analytics.py
	├── recruitment_analytics.py
	├── talent_intelligence.py
	├── turnover_analytics.py
	├── workforce_analytics.py
	└── components/
		└── components.py
```

## Dados utilizados

Os arquivos precisam permanecer com esses nomes e dentro do diretório `data/`, porque a aplicação os carrega usando caminhos relativos.

| Arquivo | Conteúdo principal |
| --- | --- |
| `tb_colaboradores.csv` | Identificação, departamento, senioridade, admissão, status, desligamento, remuneração, benefícios e promoções |
| `tb_desempenho.csv` | Notas de avaliação, fit cultural, treinamento, eNPS e receita gerada |
| `tb_jornada.csv` | Mês de referência, horas contratuais, horas extras, ausências e episódios de ausência |
| `tb_recrutamento.csv` | Fonte de aquisição, custos e datas das etapas do processo seletivo |

Os arquivos são relacionados pelo campo `ID_Colaborador`. Ao substituir os dados, preserve esse campo e os nomes das colunas esperadas pelos módulos. Datas devem estar em formato reconhecível pelo Pandas, preferencialmente `AAAA-MM-DD`.

## Atualizar os dados

1. Faça uma cópia de segurança dos arquivos existentes em `data/`.
2. Substitua os CSVs mantendo os nomes dos arquivos.
3. Verifique se as colunas obrigatórias e o campo `ID_Colaborador` continuam presentes.
4. Reinicie o Streamlit ou use a opção de recarregar a página no navegador.

Como os dados são carregados com cache, reiniciar a aplicação é a forma mais simples de garantir que todos os arquivos atualizados sejam lidos novamente.

## Solução de problemas

### `streamlit: command not found`

Confira se o ambiente virtual está ativado e instale as dependências novamente:

```bash
python3 -m pip install -r requirements.txt
```

Também é possível iniciar o Streamlit como módulo:

```bash
python3 -m streamlit run app.py
```

### Erro informando que um arquivo CSV não foi encontrado

Execute o comando na raiz do projeto, no mesmo diretório onde estão `app.py` e a pasta `data/`:

```bash
cd st_people_analytics
streamlit run app.py
```

### Erro após substituir os dados

Verifique os nomes dos arquivos, os nomes das colunas e o formato das datas. As análises dependem das colunas utilizadas nos cruzamentos e nos cálculos descritos na seção [Dados utilizados](#dados-utilizados).

## Desativar o ambiente virtual

Quando terminar de usar o projeto:

```bash
deactivate
```

Para executar novamente em outro momento, entre na pasta do projeto, ative o ambiente virtual e rode `streamlit run app.py`.