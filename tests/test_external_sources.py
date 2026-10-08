import unittest
from unittest.mock import patch
from job_hunter import collect, classify

class ExternalSourcesTests(unittest.TestCase):
    def test_remotive_worldwide_and_brazil_only(self):
        def loader(url):
            self.assertIn('remotive.com', url)
            return {'jobs': [
                {'id': 1, 'title': 'Junior Python Developer', 'company_name': 'A', 'candidate_required_location': 'Worldwide', 'description': 'Python', 'url': 'https://example.com/1'},
                {'id': 2, 'title': 'Junior Java Developer', 'company_name': 'B', 'candidate_required_location': 'United States', 'description': 'Java', 'url': 'https://example.com/2'},
                {'id': 3, 'title': 'Estágio Frontend React', 'company_name': 'C', 'candidate_required_location': 'Brazil', 'description': 'React', 'url': 'https://example.com/3'},
            ]}
        config = {'remotive': {'enabled': True}, 'greenhouse': [], 'lever': []}
        rows, errors = collect(config, loader)
        self.assertEqual(len(rows), 2)
        self.assertEqual(errors, [])
        self.assertIsNotNone(classify(rows[0], config))

    def test_adzuna_missing_credentials_is_reported_without_request(self):
        config = {'adzuna': {'enabled': True}, 'greenhouse': [], 'lever': []}
        with patch.dict('os.environ', {'ADZUNA_APP_ID': '', 'ADZUNA_APP_KEY': ''}):
            rows, errors = collect(config, lambda url: self.fail('should not request'))
        self.assertEqual(rows, [])
        self.assertIn('ADZUNA_APP_ID', errors[0])

if __name__ == '__main__':
    unittest.main()
