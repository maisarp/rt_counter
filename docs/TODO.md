# TODO - Contador de Retweets

Lista de melhorias e correções planejadas para o projeto.

---

## Correções

- [ ] **Correção do CSV gerado**: Está gerando com vários meses do ano (deveria filtrar apenas o mês atual ou período relevante)
- [ ] **Corrigir resumo final**: Revisar cálculos e exibição do resumo semanal/mensal

---

## Refatoração

- [ ] **Refatoração DDD**: Aplicar padrões de Domain-Driven Design para melhor organização do código
- [ ] **Deixar app leve**: Otimizar performance e reduzir dependências desnecessárias

---

## Otimização de Performance (PCs menos potentes)

- [ ] **Timer update**: Aumentar intervalo de `_update_timer` de 100ms para 200-300ms
- [ ] **HTML Viewer monitor**: Aumentar intervalo de verificação de 300ms para 500ms-1s
- [ ] **Modo lite**: Criar flag para rodar com tkinter puro em vez de CustomTkinter
- [ ] **Desabilitar XLSX**: Tornar geração de Excel opcional (openpyxl consome recursos)
- [ ] **Lazy loading**: Carregar dados apenas do mês atual inicialmente
- [ ] **Debounce no salvamento**: Implementar salvamento periódico em vez de a cada mudança
- [ ] **Substituir Pandas**: Usar csv nativo para operações simples de I/O

---

## Estudo OOP (Pré-requisito para migração C#)

Plano prático: aprender OOP refatorando este projeto.

- [ ] **Fase 1 - Separar Responsabilidades**: Extrair classes do `app.py` (Counter, Timer, Repository, Exporter)
- [ ] **Fase 2 - Encapsulamento**: Usar `@property`, métodos privados (`_method`), proteger atributos
- [ ] **Fase 3 - Composição**: Classes que usam outras classes (ex: `App` usa `Counter`, `Timer`, etc.)
- [ ] **Fase 4 - Herança/Polimorfismo**: Criar classe base `Exporter` com filhas `CSVExporter`, `ExcelExporter`
- [ ] **Fase 5 - SOLID**: Aplicar princípios (principalmente Single Responsibility e Dependency Inversion)

**Recursos:**
- YouTube: "Corey Schafer OOP Python" (EN) | "Otávio Miranda OOP" (PT-BR)
- Site: [Refactoring Guru](https://refactoring.guru/pt-br) - Padrões e SOLID

---

## Estudo OpenTelemetry

Objetivo: Implementar observabilidade para metrificar uso de IA.

### Conceitos Básicos
- [ ] Entender os 3 pilares: **Traces**, **Metrics**, **Logs**
- [ ] Entender o fluxo: App → Collector → Backend (Grafana/Jaeger)
- [ ] Saber a diferença entre SDK, Exporter e Collector

### Recursos em Vídeo
- **PT-BR:**
  - YouTube: "Full Cycle - OpenTelemetry" (Wesley Willians)
  - YouTube: "Fabricio Veronez - Observabilidade"
  - YouTube: "LinuxTips - OpenTelemetry + Grafana"
- **EN:**
  - YouTube: "OpenTelemetry Course - FreeCodeCamp" (~1h, completo)
  - YouTube: "TechWorld with Nana - OpenTelemetry Explained"
  - YouTube: "IBM Technology - What is OpenTelemetry?"

### Recursos Escritos
- [Documentação Oficial](https://opentelemetry.io/docs/) - Referência
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/) - Guia específico
- [Grafana + OpenTelemetry](https://grafana.com/docs/opentelemetry/) - Integração

### Hands-on (depois dos vídeos)
- [ ] Instrumentar uma rota simples (trace de request)
- [ ] Criar métrica customizada (ex: contagem de chamadas à API de IA)
- [ ] Enviar dados pro Grafana Cloud (free tier)
- [ ] Criar dashboard básico

---

## Estudo Banco de Dados

Objetivo: Armazenar histórico de testes gerados por usuário (integrar com Auth).

### Conceitos Básicos
- [ ] Entender SQL básico: SELECT, INSERT, UPDATE, DELETE, JOIN
- [ ] Entender ORM: mapear classes Python para tabelas
- [ ] Modelagem básica: relacionamento User → Testes (1:N)

### Stack Recomendada para Python
| Componente | Opção Simples | Opção Enterprise |
|------------|---------------|------------------|
| Banco | SQLite / PostgreSQL | PostgreSQL / SQL Server |
| ORM | SQLAlchemy | SQLAlchemy |
| Migrations | Alembic | Alembic |

### Recursos em Vídeo
- **PT-BR:**
  - YouTube: "Otávio Miranda - SQLAlchemy" (completo)
  - YouTube: "Eduardo Mendes (Live de Python) - SQLAlchemy 2.0"
  - YouTube: "Hashtag Programação - SQL do zero"
- **EN:**
  - YouTube: "Corey Schafer - SQLAlchemy"
  - YouTube: "FreeCodeCamp - SQL Full Course"
  - YouTube: "ArjanCodes - SQLAlchemy 2.0"

### Modelo Sugerido para seu caso
```python
# Exemplo de estrutura
class User:  # Já vem do Auth
    id: str
    email: str

class GeneratedTest:
    id: int
    user_id: str  # FK para User
    test_type: str  # "BDD" | "Robot"
    input_doc: str  # Documento de entrada
    output_code: str  # Código gerado
    created_at: datetime
    tokens_used: int  # Métrica de uso de IA
```

### Hands-on
- [ ] Criar modelo `GeneratedTest` com SQLAlchemy
- [ ] Fazer migration com Alembic
- [ ] Criar endpoint para salvar teste gerado
- [ ] Criar endpoint para listar histórico do usuário
- [ ] Adicionar paginação na listagem

---

## Futuro

- [ ] **Verificar como distribuir como SaaS**: Pesquisar opções de hospedagem, modelo de cobrança e distribuição como serviço
- [ ] **Migrar para C# WPF (.NET)**: Reescrever aplicação para melhor performance e distribuição nativa
  - Recomendado: WPF (visual moderno, XAML) - similar ao CustomTkinter em flexibilidade
  - Benefícios: Executável leve (~5-15MB), startup instantâneo, ~3x menos RAM
  - Pré-requisito: Completar estudo OOP acima
  - Bibliotecas UI: Material Design in XAML ou MahApps.Metro

---

## Concluído

- [x] **Centralizar arquivos de dados**: Arquivos internos agora são armazenados em AppData (não polui pasta do usuário)
- [x] **Escolha de pasta de exportação**: Usuário pode escolher onde salvar os arquivos CSV/Excel finais (Config > Escolher)

---

*Última atualização: 01/12/2025*
