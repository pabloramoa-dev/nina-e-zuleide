import unittest,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TestCatalog(unittest.TestCase):
    def test_50_episodes(self):
        arr=json.loads((ROOT/'data/50_episodios.json').read_text())
        self.assertEqual(len(arr),50)
        self.assertEqual([x['numero'] for x in arr],list(range(1,51)))
        self.assertEqual(len({x['titulo'] for x in arr}),50)
        for ep in arr:
            self.assertGreater(len(ep['gancho_antecipacao']),50)
            self.assertGreater(len(ep['virada_final']),40)
            self.assertIn('zuleide',ep['personagens'])
            self.assertNotEqual(ep['ilustracao_nina'],ep['ilustracao_zuleide'])
    def test_sources_are_real_urls(self):
        sources=json.loads((ROOT/'data/fontes_pesquisadas.json').read_text())
        self.assertGreaterEqual(len(sources),10)
        self.assertTrue(all(x['url'].startswith('https://') for x in sources))
        refs={s['id'] for s in sources}
        self.assertTrue(all(x['inspiracao_id'] in refs for x in json.loads((ROOT/'data/50_episodios.json').read_text())))
    def test_distinct_images_if_present(self):
        build=ROOT/'build/images'
        if not build.exists():return
        for i in range(10):
            a=build/'nina'/f'cena_{i:02d}.jpg';b=build/'zuleide'/f'cena_{i:02d}.jpg'
            if a.exists() and b.exists():
                self.assertNotEqual(hashlib.sha256(a.read_bytes()).digest(),hashlib.sha256(b.read_bytes()).digest())
if __name__=='__main__':unittest.main()
