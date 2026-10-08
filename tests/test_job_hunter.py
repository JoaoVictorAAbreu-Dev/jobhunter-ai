import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import job_hunter as j

class TestJobHunter(unittest.TestCase):
    def setUp(self):
        self.config = {'greenhouse': ['teste'], 'lever': ['demo'], 'niveis': ['estagio', 'junior']}
    def job(self, title, loc):
        return {'id': 'x:1', 'empresa': 'x', 'titulo': title, 'local': loc, 'descricao': 'Spring Boot e Java', 'url': 'https://example.com/job/1'}
    def test_estagio_suzano(self):
        self.assertEqual(j.classify(self.job('Estágio em Desenvolvimento Java', 'Suzano, SP'), self.config)['nivel'], 'estagio')
    def test_junior_remote(self):
        self.assertEqual(j.classify(self.job('Junior Java Developer', 'Remote - Brazil'), self.config)['modalidade'], 'remoto')
    def test_exclude_senior(self):
        self.assertIsNone(j.classify(self.job('Senior Java Developer', 'São Paulo'), self.config))
    def test_exclude_pleno(self):
        self.assertIsNone(j.classify(self.job('Desenvolvedor Pleno Java', 'São Paulo'), self.config))
    def test_exclude_other_city(self):
        self.assertIsNone(j.classify(self.job('Estágio Java', 'Curitiba'), self.config))
    def test_exclude_remote_us_only(self):
        self.assertIsNone(j.classify(self.job('Junior Java Developer', 'Remote - US Only'), self.config))
    def test_unknown_seniority(self):
        self.assertIsNone(j.classify(self.job('Software Engineer', 'São Paulo'), self.config))
    def test_collection_and_persistent_approval(self):
        def fake(url):
            if 'greenhouse' in url:
                return {'jobs': [{'id': 42, 'title': 'Estágio Java', 'location': {'name': 'São Paulo'}, 'absolute_url': 'https://example.com/42', 'content': '<b>Spring</b>'}]}
            return [{'id': 'abc', 'text': 'Junior Frontend React', 'categories': {'location': 'Remote - Brazil'}, 'hostedUrl': 'https://example.com/abc', 'descriptionPlain': 'React TypeScript'}]
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            rows, errors = j.search(self.config, base, fake)
            self.assertEqual(len(rows), 2)
            self.assertFalse(errors)
            j.decide(base, 'gh:teste:42', 'aprovada_para_revisao_final')
            rows, _ = j.search(self.config, base, fake)
            self.assertEqual(next(r for r in rows if r['id'] == 'gh:teste:42')['status'], 'aprovada_para_revisao_final')

if __name__ == '__main__':
    unittest.main()
