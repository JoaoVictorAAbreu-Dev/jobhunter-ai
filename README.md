# JobHunter AI — plataforma de descoberta de vagas

Projeto de portfólio em **Engenharia de Software** para agregar anúncios públicos de estágio e júnior em tecnologia, com classificação por regras, painel web, API PHP opcional, Docker e CI/CD. Não realiza candidaturas automáticas.

## Visão geral das stacks

| Camada | Stack | Diretório / arquivo |
|---|---|---|
| Coleta e regras de negócio | Python 3 | `job_hunter.py` |
| Geração de dados públicos | Python 3 | `scripts/build_site.py` |
| Interface web | HTML, CSS, TypeScript | `web/` |
| API REST opcional | PHP 8.3 | `php/api/` |
| Execução local | Docker / Compose | `Dockerfile`, `compose.yaml`, `docker/` |
| Testes e deploy | GitHub Actions | `.github/workflows/` |
| Publicação estática | GitHub Pages | `site/` (gerado) |

## Documentação de engenharia

- [Arquitetura e decisões técnicas](docs/ARCHITECTURE.md)
- [Requisitos e critérios de aceite](docs/REQUIREMENTS.md)
- [Contrato da API PHP](docs/API.md)
- [Desenvolvimento, qualidade e contribuição](docs/DEVELOPMENT.md)

## Início rápido com Docker

```bash
git clone https://github.com/JoaoVictorAAbreu-Dev/jobhunter-ai.git
cd jobhunter-ai
cp .env.example .env
docker compose up --build -d
```

Acesse http://localhost:8080 para o painel e http://localhost:8080/api/vagas para a API. Para buscar vagas, consulte a seção Docker abaixo.

---

## Guia detalhado — São Paulo e remoto

Mini-projeto Python 3 (sem dependências externas) para localizar vagas de **estágio e júnior** nas páginas públicas de empresas que utilizam **Greenhouse** ou **Lever**, priorizar por área técnica e indicar um dos nove currículos em PDF.

## Configuração

Em `config.json`, adicione os identificadores reais das empresas em `greenhouse` e `lever`. Os arrays vêm vazios de propósito: o programa **não descobre todas as empresas automaticamente** e não deve simular resultados. Exemplos de formatos de URL: `https://boards.greenhouse.io/IDENTIFICADOR` e `https://jobs.lever.co/IDENTIFICADOR`.

## Uso no Ubuntu

```bash
cd JobHunter_AI_v2
python3 job_hunter.py buscar
python3 job_hunter.py listar
python3 job_hunter.py aprovar --id 'gh:EMPRESA:12345'
python3 job_hunter.py rejeitar --id 'gh:EMPRESA:12345'
# Somente após você efetivamente se candidatar no site:
python3 job_hunter.py marcar-enviada --id 'gh:EMPRESA:12345'
python3 -m unittest discover -s tests -v
```

A busca grava `vagas_para_revisar.csv` e `avisos_busca.txt`. Aprovações ficam persistidas em `aprovacoes.json`, inclusive após novas buscas. `aprovar` **não envia candidatura**: apenas registra sua decisão para posterior revisão e envio manual pelo link oficial. A ação `marcar-enviada` só registra uma candidatura que você já realizou.

## Filtros

- Títulos explícitos de estágio/internship ou júnior/entry-level; exclui pleno, sênior e liderança.
- São Paulo e municípios da região metropolitana, ou vagas com localização explicitamente remota.
- Vagas sem localidade identificável são excluídas; vagas remotas restritas explicitamente a EUA/Canadá/Europa também.
- Compatibilidade por palavras-chave, não por inteligência artificial generativa.
- **Atenção:** 'remote' pode ainda exigir residência ou autorização de trabalho em determinado país; confirme no anúncio. O filtro de cidade é aproximado, não geográfico por coordenadas.

## Limites e privacidade

Sem automação de navegador, sem contorno de CAPTCHA, sem envio de currículo, sem armazenamento de credenciais e sem promessa de candidatura automática. Só consulta endpoints públicos; empresas podem alterar ou remover os endpoints. A busca precisa de internet. Não há garantia de vagas, nem de elegibilidade ou de exatidão da classificação. Nenhum currículo é transmitido a empresas.

APIs: https://developers.greenhouse.io/job-board.html e https://github.com/lever/postings-api

## GitHub Actions e Pages

1. Crie um repositório **público** vazio `jobhunter-ai` no GitHub e envie os arquivos deste projeto (incluindo `.github/workflows/search-and-pages.yml`).
2. Em **Settings → Pages → Build and deployment → Source**, selecione **GitHub Actions**.
3. Em **Actions**, abra **Buscar vagas e publicar painel** e clique **Run workflow**.
4. O workflow roda diariamente às **11:23 UTC** (aproximadamente 08:23 em Brasília) e também manualmente. Agendamentos do GitHub podem atrasar.
5. Configure os identificadores reais dos quadros Greenhouse/Lever em `config.json`; sem eles, a busca ficará vazia. Não invente identificadores.
6. O endereço público previsto será `https://SEU-USUARIO.github.io/jobhunter-ai/` após a primeira implantação bem-sucedida.

**Privacidade:** o site público apresenta apenas informações das vagas e links de candidatura, sem currículos, telefone, e-mail, aprovações ou dados pessoais. Os PDFs do projeto ficam no repositório e **serão públicos se você publicar este diretório em um repositório público**. Para preservar seus dados, remova os arquivos `*.pdf` e `*.tex` antes de fazer o push público, ou use um repositório privado com permissões de Pages apropriadas. O CSV de busca fica como artefato do Actions, mas artefatos em repositórios públicos podem ser acessíveis conforme as permissões do GitHub; não inclua dados pessoais nele.

**Aprovação:** não há aprovação via site público. Use `python job_hunter.py aprovar --id '...'` localmente, após baixar o CSV da execução. A aprovação é apenas um registro local; o envio permanece manual no site da empresa. A execução agendada não sincroniza aprovações locais.

## Fontes de vagas (integração atual)

- **Remotive:** habilitada por padrão em `config.json`; usa API pública de vagas remotas de software. Apenas anúncios que indiquem explicitamente **Brazil/Brasil** ou **Worldwide/Global/Anywhere** são considerados, e ainda precisam passar pelos filtros de nível e área. Verifique sempre elegibilidade no anúncio original. Uma busca pode retornar zero vagas.
- **Adzuna:** habilitada em `config.json`, mas só consegue consultar a API quando as credenciais estiverem configuradas e o endpoint `br` estiver disponível. Crie secrets do repositório em **Settings → Secrets and variables → Actions** chamados `ADZUNA_APP_ID` e `ADZUNA_APP_KEY`, a opção `adzuna.enabled` já está em `true`. Nunca adicione chaves ao repositório ou ao frontend.
- **Greenhouse/Lever:** continuam disponíveis; configure identificadores reais de empresas nos arrays de `config.json`.

A coleta roda no GitHub Actions e gera `vagas.json` no site; o TypeScript apenas exibe os resultados. Erros de coleta ficam no artefato `avisos_busca.txt`. Nenhuma fonte garante vagas elegíveis e nenhuma candidatura é enviada automaticamente.

## API PHP opcional (backend local / hospedagem PHP)

O endpoint `php/api/vagas.php` fornece uma API REST de **somente leitura**, sem expor credenciais, currículos ou decisões de candidatura. Ele lê `site/vagas.json`, que é gerado pelo Python; **não busca vagas diretamente nas APIs externas**. Não substitui a rotina do GitHub Actions.

Pré-requisito: PHP 8.1+ (usa `array_is_list`), Python 3 e `site/vagas.json` gerado. Na raiz do repositório:

```bash
python3 job_hunter.py buscar
python3 scripts/build_site.py
php -S localhost:8000 -t .
# Em outro terminal:
curl 'http://localhost:8000/php/api/vagas.php?q=python&nivel=junior&pagina=1&limite=12'
```

Parâmetros opcionais: `q` (texto), `nivel`, `area`, `modalidade`, `local`, `empresa`, `ordem` (`pontuacao`, `empresa`, `titulo`), `pagina` e `limite` (1–100). Resposta JSON: `total`, `pagina`, `limite`, `paginas`, `vagas`. Parâmetros inválidos recebem HTTP 400; dados ausentes, HTTP 503. Os filtros são combinados e a paginação é feita no servidor.

**Hospedagem:** GitHub Pages é estático e **não executa PHP**. O painel atual continua consumindo `site/vagas.json` e funcionando no Pages. Para consumir a API PHP em produção, hospede o backend em um servidor com PHP e configure a URL do frontend; não publique segredos nesse servidor ou no JSON público.

## Docker (Ubuntu / Windows / macOS)

Pré-requisito: Docker Engine com Compose v2 ou Docker Desktop. O contêiner usa **PHP 8.3** para servir o painel e a API, **Python 3** para coletar as vagas e **Node 22** apenas na etapa de compilação do TypeScript.

```bash
git clone https://github.com/JoaoVictorAAbreu-Dev/jobhunter-ai.git
cd jobhunter-ai
cp .env.example .env
docker compose up --build -d
```

Acesse **http://localhost:8080/** para o painel e **http://localhost:8080/api/vagas?pagina=1&limite=12** para a API PHP. A imagem gera o JSON inicial mesmo sem vagas; não é necessário ter credenciais para abrir o painel.

Para buscar vagas manualmente e atualizar a página, com o contêiner em execução:

```bash
docker compose exec jobhunter sh -c 'python3 job_hunter.py buscar && python3 scripts/build_site.py'
```

Para coletar automaticamente **uma vez na inicialização**, configure `RUN_COLLECTION=1` no arquivo `.env` e execute `docker compose up -d --force-recreate`. Isso não agenda coletas periódicas. Se a coleta falhar, o painel ainda sobe, com o último conjunto de dados disponível no contêiner.

Para habilitar a Adzuna, defina `ADZUNA_APP_ID` e `ADZUNA_APP_KEY` no **arquivo local** `.env`, usando uma chave nova e privada. O `.env` está no `.gitignore` e no `.dockerignore`; **nunca** envie credenciais ao repositório. A disponibilidade da API Adzuna para `br` ainda depende da conta e do endpoint.

```bash
docker compose logs -f jobhunter
docker compose down
```

O contêiner **não envia candidaturas**. Dados coletados dentro do contêiner são efêmeros e podem desaparecer ao recriá-lo; exporte o CSV se precisar mantê-lo. Para disponibilizar na internet, implante em um servidor com Docker, DNS/HTTPS e portas configuradas; `localhost:8080` é apenas acesso local. O GitHub Pages continua sendo uma publicação separada, sem execução de PHP.
