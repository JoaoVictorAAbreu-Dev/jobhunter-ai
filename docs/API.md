# Contrato HTTP — API PHP

**Base URL no Docker:** `http://localhost:8080`

### GET /api/vagas
Parâmetros opcionais: `q`, `nivel`, `area`, `modalidade`, `local`, `empresa`, `ordem` (`pontuacao`, `empresa`, `titulo`), `pagina` (>=1) e `limite` (1 a 100).

```bash
curl 'http://localhost:8080/api/vagas?q=python&pagina=1&limite=10'
```

Exemplo de formato, não de dados reais:
```json
{
  "total": 0,
  "pagina": 1,
  "limite": 10,
  "paginas": 0,
  "vagas": []
}
```

| HTTP | Situação |
|---|---|
| 200 | Consulta válida, mesmo sem resultados |
| 400 | Filtro ou paginação inválidos |
| 405 | Método diferente de GET |
| 503 | JSON público ausente ou inválido |

A API não oferece autenticação nem operações de escrita; não publicar dados privados em `site/vagas.json`. O painel GitHub Pages consulta diretamente o JSON estático, não esta API.
