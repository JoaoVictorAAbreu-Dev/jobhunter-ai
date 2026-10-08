"""JobHunter AI v2: busca, classifica e registra aprovação; nunca envia candidaturas."""
import argparse
import csv
import hashlib
import html
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

BASE = Path(__file__).resolve().parent
AREAS = {
    'backend_java': ['java', 'spring', 'backend', 'back end', 'api rest'],
    'frontend': ['frontend', 'front end', 'react', 'javascript', 'typescript'],
    'fullstack': ['fullstack', 'full stack', 'full-stack'],
    'python_ia': ['python', 'machine learning', 'inteligencia artificial', 'ai engineer'],
    'dados': ['dados', 'analytics', 'data analyst', 'data science', 'cientista de dados'],
    'mobile': ['mobile', 'flutter', 'android', 'ios'],
    'sistemas': ['linux', 'infraestrutura', 'infrastructure', 'devops', 'systems'],
    'engenharia_software': ['software engineer', 'engenharia de software', 'developer', 'desenvolvedor', 'desenvolvimento de software'],
    'qa_testes': ['quality assurance', 'qa', 'tester', 'testes', 'test automation'],
}
JUNIOR = ['junior', 'jr', 'entry level', 'entry-level', 'early career', 'recem formado']
ESTAGIO = ['estagio', 'estagiario', 'estagiaria', 'intern', 'internship']
EXCLUDE = ['senior', 'sr', 'staff', 'principal', 'lead', 'lider', 'gerente', 'manager', 'director', 'diretor', 'head of', 'pleno', 'mid level', 'mid-level']
METRO = ['sao paulo', 'suzano', 'itaquaquecetuba', 'mogi das cruzes', 'poa', 'ferraz de vasconcelos', 'guarulhos', 'osasco', 'barueri', 'santo andre', 'sao bernardo', 'sao caetano', 'maua', 'diadema', 'taboao da serra', 'carapicuiba', 'cotia', 'embu das artes', 'ar uja', 'aruja', 'santana de parnaiba', 'jandira', 'itapevi', 'ribeirao pires', 'francisco morato', 'franco da rocha', 'caieiras', 'cajamar', 'embu-guacu', 'embu guacu', 'guararema', 'salesopolis', 'biritiba mirim', 'santa isabel', 'rio grande da serra', 'vargem grande paulista', 'pirapora do bom jesus', 'juquitiba', 'sao lourenco da serra', 'mairipora', 'itapecerica da serra']
REMOTE = ['remote', 'remoto', 'remota', 'home office', 'work from home', 'teletrabalho']
FIELDS = ['id', 'empresa', 'titulo', 'nivel', 'local', 'modalidade', 'area', 'pontuacao', 'curriculo', 'status', 'url', 'motivo']

def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(s or '').lower()) if not unicodedata.combining(c))

def contains_term(text, term):
    return bool(re.search(r'(?<!\w)' + re.escape(norm(term)) + r'(?!\w)', norm(text)))

def has_any(text, terms):
    return any(contains_term(text, t) for t in terms)

def fetch(url):
    req = Request(url, headers={'User-Agent': 'JobHunterAI-Portfolio/2.0', 'Accept': 'application/json'})
    with urlopen(req, timeout=20) as response:
        return json.load(response)

def collect(config, loader=fetch):
    jobs, errors = [], []
    for board in config.get('greenhouse', []):
        try:
            data = loader('https://boards-api.greenhouse.io/v1/boards/' + quote(board, safe='') + '/jobs?content=true')
            for j in data.get('jobs', []):
                jobs.append(dict(id=f'gh:{board}:{j.get("id")}', empresa=board, titulo=j.get('title', ''), local=(j.get('location') or {}).get('name', ''), descricao=html.unescape(re.sub('<[^>]*>', ' ', j.get('content') or '')), url=j.get('absolute_url', '')))
        except Exception as exc:
            errors.append(f'Greenhouse {board}: {exc}')
    for board in config.get('lever', []):
        try:
            data = loader('https://api.lever.co/v0/postings/' + quote(board, safe='') + '?mode=json')
            for j in data:
                cat = j.get('categories') or {}
                jobs.append(dict(id=f'lever:{board}:{j.get("id")}', empresa=board, titulo=j.get('text', ''), local=cat.get('location', ''), descricao=j.get('descriptionPlain') or '', url=j.get('hostedUrl', '')))
        except Exception as exc:
            errors.append(f'Lever {board}: {exc}')
    return jobs, errors

def classify(job, config):
    title = norm(job.get('titulo', ''))
    blob = norm(title + ' ' + job.get('descricao', ''))
    loc = norm(job.get('local', ''))
    if has_any(title, EXCLUDE):
        return None
    nivel = 'estagio' if has_any(title, ESTAGIO) else 'junior' if has_any(title, JUNIOR) else None
    if nivel not in config.get('niveis', ['estagio', 'junior']):
        return None
    is_remote = has_any(loc, REMOTE)
    is_metro = has_any(loc, METRO)
    # A localidade não pode ser inferida apenas pela descrição da vaga.
    if not (is_remote or is_metro):
        return None
    if is_remote and not is_metro:
        # Vagas remotas explicitamente restritas a outros países não são incluídas.
        if has_any(loc, ['united states', 'usa only', 'us only', 'canada only', 'europe only', 'emea only', 'uk only']):
            return None
    scores = {area: sum(4 if contains_term(title, term) else 1 if contains_term(blob, term) else 0 for term in terms) for area, terms in AREAS.items()}
    area = max(scores, key=scores.get)
    if scores[area] == 0:
        return None
    out = dict(job)
    out.update(nivel=nivel, modalidade='remoto' if is_remote else 'presencial/hibrido', area=area, pontuacao=scores[area] + 3, curriculo=area + '.pdf', status='pendente', motivo='Correspondência por palavras-chave; confirme requisitos, localização e elegibilidade antes de aprovar.')
    return out

def load_state(path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))

def save_state(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def export(rows, path):
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)

def search(config, base=BASE, loader=fetch):
    raw, errors = collect(config, loader)
    state_path = base / 'aprovacoes.json'
    state = load_state(state_path)
    seen, rows = set(), []
    for job in raw:
        ranked = classify(job, config)
        if not ranked or not ranked.get('url'):
            continue
        key = ranked['url'].rstrip('/').lower()
        if key in seen:
            continue
        seen.add(key)
        ranked['status'] = state.get(ranked['id'], {}).get('status', 'pendente')
        rows.append(ranked)
    rows.sort(key=lambda j: j['pontuacao'], reverse=True)
    export(rows, base / 'vagas_para_revisar.csv')
    (base / 'avisos_busca.txt').write_text('\n'.join(errors) if errors else 'Nenhum erro reportado.', encoding='utf-8')
    return rows, errors

def decide(base, job_id, status):
    with (base / 'vagas_para_revisar.csv').open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    matches = [r for r in rows if r['id'] == job_id]
    if len(matches) != 1:
        raise ValueError('ID não encontrado na lista de vagas. Execute buscar primeiro.')
    state_path = base / 'aprovacoes.json'
    state = load_state(state_path)
    state[job_id] = {'status': status, 'data_utc': datetime.now(timezone.utc).isoformat(), 'url': matches[0]['url']}
    save_state(state_path, state)
    for r in rows:
        if r['id'] == job_id:
            r['status'] = status
    export(rows, base / 'vagas_para_revisar.csv')
    return matches[0]

def main():
    parser = argparse.ArgumentParser(description='JobHunter AI v2: aprovação manual, sem envio automático.')
    parser.add_argument('acao', nargs='?', choices=['buscar', 'listar', 'aprovar', 'rejeitar', 'marcar-enviada'], default='buscar')
    parser.add_argument('--id', help='ID da vaga para aprovar, rejeitar ou marcar como enviada manualmente')
    parser.add_argument('--config', type=Path, default=BASE / 'config.json')
    args = parser.parse_args()
    if args.acao == 'buscar':
        config = json.loads(args.config.read_text(encoding='utf-8'))
        rows, errors = search(config)
        print(f'{len(rows)} vagas elegíveis; {len(errors)} fontes com erro. CSV: {BASE / "vagas_para_revisar.csv"}')
        print('Nenhuma candidatura enviada. IDs e links oficiais disponíveis no CSV.')
    elif args.acao == 'listar':
        p = BASE / 'vagas_para_revisar.csv'
        if not p.exists():
            parser.error('Execute buscar antes de listar.')
        with p.open(encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                print(f'{row["id"]} | {row["status"]} | {row["titulo"]} | {row["local"]} | {row["url"]}')
    else:
        if not args.id:
            parser.error('--id é obrigatório nesta ação')
        status = {'aprovar': 'aprovada_para_revisao_final', 'rejeitar': 'rejeitada', 'marcar-enviada': 'enviada_manualmente'}[args.acao]
        job = decide(BASE, args.id, status)
        print(f'Status registrado: {status}. Vaga: {job["titulo"]}. URL oficial: {job["url"]}')
        print('Este programa NÃO envia formulários ou currículos. O envio é feito por você no site oficial.')

if __name__ == '__main__':
    main()
