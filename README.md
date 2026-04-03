# Trabalho 1 — EDA2
## Motor de Busca E-commerce com Índice Invertido e Interface Web

Projeto desenvolvido para a disciplina de Estruturas de Dados e Algoritmos 2. O sistema implementa uma engine de busca para o catálogo da Adidas Brasil, combinando Índice Invertido (Hash) para texto e Busca Sequencial Indexada para preço, tudo servido por uma interface web em Flask.

## Destaques

- Busca textual rápida por nome usando Índice Invertido (Hash)
- Busca por faixa de preço com índice em dois níveis
- Interseção de resultados por nome e preço usando Set
- Interface web simples e responsiva com Flask + HTML
- Engine principal em Ruby para processamento eficiente dos dados

## Estruturas de dados e algoritmos

### 1) Índice invertido (Tabela Hash)

Cada nome de produto é tokenizado; cada termo vira uma chave de Hash cujo valor é a lista de IDs que contém aquela palavra. Isso reduz a busca textual para tempo médio de acesso em Hash.

### 2) Busca sequencial indexada (dois níveis)

Para buscas por preço exato ou intervalo, o catálogo é ordenado e indexado em dois níveis. A busca usa binária no índice secundário, refina no primário e varre apenas o bloco necessário.

### 3) Interseção de conjuntos (Set)

Quando o usuário combina nome e preço, as listas retornadas são intersectadas via Set para acelerar a filtragem final.

## Estrutura do projeto

```text
.
├── app.py                # Servidor Web (Flask)
├── scraper.py            # Scraper principal (gera products.json)
├── scraper1.py           # Scraper alternativo (gera products-example.json)
├── search.rb             # Engine com estruturas de dados
├── products-example.json # Cache de dados já incluído
├── requirements.txt      # Dependências Python
├── README.md
└── templates/
    └── index.html        # Interface do usuário
```

## Pré-requisitos

- Python 3.11+
- Ruby 3.x (no PATH do sistema operacional)
- Google Chrome instalado

## Instalação

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Geração de dados

Você pode usar o cache pronto ou executar o scraper.

### Opção A: usar o cache já incluído

O projeto já acompanha `products-example.json`. Basta iniciar a aplicação.

### Opção B: gerar dados atualizados

Apague o arquivo `products-example.json`

#### Execute o scraper

```bash
python scraper.py
```

Esse script gera `products-example.json`, que é utilizado para as buscas. 

## Executar a aplicação

```bash
python app.py
```

Abra http://127.0.0.1:5000 no navegador.

## Como usar

- Nome: digite termos como “Samba”, “Ultraboost” ou parte do nome
- Preço: informe mínimo e máximo (intervalo) ou deixe em branco para ver tudo, também é possível informar apenas um dos valores para que possa ver os produtos a partir do mínimo ou até o máximo.

## Observações

- O servidor envia um payload JSON para o Ruby via subprocesso e recebe o resultado filtrado em um único ciclo de execução.
- O campo `image_url` é usado apenas para renderização na interface, não influencia o processamento das buscas.

## Problemas comuns

- Ruby não encontrado: verifique se o Ruby 3.x está instalado e no PATH.
- Erros no Selenium/Chrome: atualize o Chrome e tente novamente; o driver é gerenciado pelo webdriver-manager.
- Bloqueio do site: execute o scraper novamente ou use o `products-example.json`.