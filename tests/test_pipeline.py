import copy, importlib.util, json, os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.script=module('gerar_roteiro')
        self.item=json.loads((ROOT/'data/50_episodios.json').read_text())[0]
        self.doc=self.script.demo(self.item)
    def test_all_catalog_hooks_validate(self):
        for item in json.loads((ROOT/'data/50_episodios.json').read_text()):
            self.script.validate(self.script.demo(item),item,False)
    def test_invalid_hook_blocked(self):
        self.doc['lines'][0]['text']='Gancho errado'
        with self.assertRaises(AssertionError):self.script.validate(self.doc,self.item,False)
    def test_same_prompts_blocked(self):
        self.doc['scenes'][0]['zuleide_prompt']=self.doc['scenes'][0]['nina_prompt']
        with self.assertRaises(AssertionError):self.script.validate(self.doc,self.item,False)
    def test_demo_never_production(self):
        with self.assertRaises(AssertionError):self.script.validate(self.doc,self.item,True)
    def test_plan_persisted_before_paid_call_and_duplicates_blocked(self):
        m=module('gerar_imagens')
        with tempfile.TemporaryDirectory() as d:
            m.B=Path(d);(m.B/'roteiro.json').write_text(json.dumps(self.doc))
            from PIL import Image
            import io
            buf=io.BytesIO();Image.new('RGB',(64,64),'red').save(buf,'JPEG')
            def fake(*args,**kwargs):
                plan=json.loads((m.B/'prompts_imagens.json').read_text())
                self.assertEqual(len(plan),20)
                return buf.getvalue()
            with patch.dict(os.environ,{'SILICONFLOW_API_KEY':'test-only'}),patch.object(m,'generated_image',side_effect=fake):
                with self.assertRaises(AssertionError):m.run()
    def test_missing_secret_blocks_images(self):
        m=module('gerar_imagens')
        with tempfile.TemporaryDirectory() as d:
            m.B=Path(d);(m.B/'roteiro.json').write_text(json.dumps(self.doc))
            with patch.dict(os.environ,{},clear=True):
                with self.assertRaises(RuntimeError):m.run()
    def test_video_rejects_wrong_codec_and_duration(self):
        m=module('validar_video')
        info={'streams':[{'codec_type':'video','codec_name':'h264','width':540,'height':960,'pix_fmt':'yuv420p','duration':'180'},{'codec_type':'audio','codec_name':'aac','duration':'180'}],'format':{'duration':'180'}}
        m.validate(info)
        bad=copy.deepcopy(info);bad['streams'][0]['codec_name']='vp9'
        with self.assertRaises(AssertionError):m.validate(bad)
        bad=copy.deepcopy(info);bad['format']['duration']='30'
        with self.assertRaises(AssertionError):m.validate(bad)
