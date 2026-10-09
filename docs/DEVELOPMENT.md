# Guia de desenvolvimento

## Fluxo local
```bash
python3 -m unittest discover -s tests -v
python3 job_hunter.py buscar
python3 scripts/build_site.py
docker compose up --build -d
docker compose logs -f jobhunter
```

Frontend: `web/` é o código-fonte; `site/` é o artefato gerado e não deve ser editado manualmente. API: `php/api/vagas.php`. Servidor Docker: `docker/router.php`.

## Padrão de contribuição
1. Criar issue com problema, impacto e critérios de aceite.
2. Criar branch `feat/<tema>`, `fix/<tema>` ou `docs/<tema>`.
3. Implementar alteração pequena com teste correspondente.
4. Executar `python3 -m unittest discover -s tests -v`, `php -l php/api/vagas.php`, `php -l docker/router.php` e compilação TypeScript.
5. Abrir pull request; verificar CI e revisar riscos antes do merge.

## Convenções
Commits `feat:`, `fix:`, `docs:`, `test:`, `ci:`, `refactor:`. Usar português na documentação e mensagens de interface; identificadores de código seguem os padrões de cada linguagem.

## Operação
- Configurar `ADZUNA_APP_ID` e `ADZUNA_APP_KEY` exclusivamente via GitHub Actions Secrets ou `.env` local.
- Em caso de vazamento, revogar chave e gerar outra.
- Coletas não garantem vagas elegíveis; investigar `avisos_busca.txt`.
- GitHub Pages não executa PHP; hospedar backend separadamente quando necessário.
