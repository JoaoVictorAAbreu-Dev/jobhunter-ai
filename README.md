# JobHunter AI v2 — São Paulo e remoto

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
- **Adzuna:** implementada, mas desabilitada até configurar credenciais e confirmar disponibilidade para `br`. Crie secrets do repositório em **Settings → Secrets and variables → Actions** chamados `ADZUNA_APP_ID` e `ADZUNA_APP_KEY`, depois mude `adzuna.enabled` para `true` em `config.json`. Nunca adicione chaves ao repositório ou ao frontend.
- **Greenhouse/Lever:** continuam disponíveis; configure identificadores reais de empresas nos arrays de `config.json`.

A coleta roda no GitHub Actions e gera `vagas.json` no site; o TypeScript apenas exibe os resultados. Erros de coleta ficam no artefato `avisos_busca.txt`. Nenhuma fonte garante vagas elegíveis e nenhuma candidatura é enviada automaticamente.
