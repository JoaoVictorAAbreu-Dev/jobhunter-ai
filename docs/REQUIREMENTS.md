# Engenharia de requisitos — MVP

## Stakeholders e problema
Pessoa candidata a estágio/júnior em tecnologia que deseja centralizar oportunidades públicas em São Paulo, Grande São Paulo e vagas remotas potencialmente elegíveis.

## Requisitos funcionais
| ID | Requisito | Critério de aceite |
|---|---|---|
| RF-01 | Coletar vagas de fontes configuradas | Executar `python3 job_hunter.py buscar` e produzir CSV e avisos |
| RF-02 | Classificar estágio/júnior e área | Testes cobrem níveis permitidos e exclusões |
| RF-03 | Filtrar por localidade ou remoto | Regras rejeitam regiões explicitamente incompatíveis |
| RF-04 | Exibir vagas públicas | Painel carrega `site/vagas.json` e informa resultado vazio |
| RF-05 | Buscar, ordenar e filtrar no painel | Contagem e cards mudam conforme filtros |
| RF-06 | Consultar API PHP | `GET /api/vagas` retorna JSON paginado no Docker |
| RF-07 | Revisar candidaturas manualmente | Aprovar/rejeitar não envia currículo |
| RF-08 | Publicar frontend | GitHub Actions gera e publica site estático |

## Requisitos não funcionais
| ID | Requisito | Verificação |
|---|---|---|
| RNF-01 | Proteção de credenciais | Chaves só em Secrets/variáveis de ambiente |
| RNF-02 | Compatibilidade local | `docker compose up --build -d` |
| RNF-03 | Testabilidade | Unit tests Python, lint PHP e compilação TypeScript no CI |
| RNF-04 | Falha controlada | Erros de coleta são reportados sem inventar vagas |
| RNF-05 | Acessibilidade básica | Rótulos e navegação por teclado no frontend |
| RNF-06 | Transparência | Links externos levam ao anúncio original |

## Fora do escopo
Login, envio automático de candidaturas, IA generativa, scraping autenticado, notificações e garantia de atualização em tempo real.

## Critérios de pronto (Definition of Done)
Mudança documentada; testes de regressão passando; sem segredos em commits; comportamento de falha considerado; revisão de segurança para entrada externa; deploy validado em ambiente real antes de afirmar que está no ar.
