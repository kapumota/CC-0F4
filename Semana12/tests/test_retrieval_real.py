"""Pruebas aritméticas y de contratos; no constituyen una evaluación de SQuAD."""
import tempfile
import unittest
from pathlib import Path
import pandas as pd
from Semana12 import retrieval_real as r


def arithmetic_fixture():
    # Cuatro filas numéricas para verificar fórmulas, sin textos ni preguntas fabricadas.
    return pd.DataFrame({'article':['a','a','a','b'], 'split':['test']*4,
                         'score_margin':[.01,.02,.3,.01],
                         'hit_top1':[0,1,0,0], 'hit_top2':[0,1,0,0],
                         'hit_top3':[1,1,0,0], 'hit_top4':[1,1,0,1],
                         'hit_top5':[1,1,0,1]},index=[2,4,6,9])


class TestContracts(unittest.TestCase):
    def test_fixed_and_adaptive_arithmetic(self):
        f=r.apply_threshold(arithmetic_fixture(),.075)
        self.assertEqual(f.context_B.tolist(),[5,5,1,5])
        self.assertEqual(f.hit_B_adaptive.tolist(),[1,1,0,1])
        stats=r.summarize(f)
        self.assertEqual(len(stats),6)
        self.assertAlmostEqual(stats[r.ADAPTIVE]['mean_context_paragraphs'],4)
        self.assertAlmostEqual(stats[r.ADAPTIVE]['utility'],.65)
        _,mix=r.equal_budget_mix(f)
        self.assertEqual(mix['k_lower'],4)
        self.assertEqual(mix['k_upper'],4)
        self.assertAlmostEqual(mix['expected_hit'],.75)

    def test_fractional_budget(self):
        f=r.apply_threshold(arithmetic_fixture().iloc[:3],.015)
        _,m=r.equal_budget_mix(f)
        self.assertAlmostEqual(m['mean_context'],7/3)
        self.assertEqual(m['k_lower'],2)
        self.assertEqual(m['k_upper'],3)
        self.assertAlmostEqual(m['expected_hit'],(2/3)*(1/3)+(1/3)*(2/3))

    def test_cluster_micro_vs_macro(self):
        f=r.apply_threshold(arithmetic_fixture(),.075)
        out=r.bootstrap_article_differences(f,r.FIXED[3],repeats=2000)['B_menos_A0_hit']
        self.assertAlmostEqual(out['observado_micro'],.5)
        self.assertAlmostEqual(out['observado_macro_articulo'],(1/3+1)/2)
        self.assertEqual(out['IC95_micro_cluster_articulo'],[1/3,1.0])

    def test_no_test_tuning(self):
        with self.assertRaises(ValueError): r.tune_threshold(arithmetic_fixture())
        dev=arithmetic_fixture().assign(split='development')
        best,table=r.tune_threshold(dev)
        self.assertEqual(len(table),len(r.THRESHOLDS))
        self.assertEqual(best['threshold'],table.iloc[0].threshold)
        self.assertTrue(table.dev_utility.is_monotonic_decreasing)

    def test_frontier_matches_direct_calculation(self):
        f=r.apply_threshold(arithmetic_fixture(),.075)
        rows=r.fixed_frontier(f)
        self.assertEqual(rows[0]['lambda_lower'],0)
        self.assertIsNone(rows[-1]['lambda_upper'])
        for row in rows:
            lo,hi=row['lambda_lower'],row['lambda_upper']
            lam=(lo+hi)/2 if hi is not None else lo+1
            v=r.summarize(f,lam)
            self.assertAlmostEqual(v[row['winner']]['utility'],max(x['utility'] for x in v.values()))

    def test_sample_distinct_and_repeatable(self):
        f=arithmetic_fixture()
        a=r.sample_errors(f,count=2)
        b=r.sample_errors(f,count=2)
        self.assertEqual(a.index.tolist(),b.index.tolist())
        self.assertEqual(a.article.nunique(),2)
        self.assertEqual(len(r.sample_errors(f.iloc[:0])),0)

    def test_reject_nonofficial_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json'
            p.write_bytes(b'{}')
            with self.assertRaises(ValueError): r.verify_source(p)

    def test_real_source_if_available(self):
        if not r.DATA_PATH.exists(): self.skipTest('SQuAD original no instalado')
        docs,q,manifest=r.load_squad()
        self.assertEqual((len(docs),len(q),manifest['n_articles']),(2067,10570,48))
        for seed in r.SENSITIVITY_SEEDS:
            split=r.partition_questions(q,seed)
            groups=split.groupby('split').article.nunique().to_dict()
            self.assertEqual(groups,{'development':24,'test':24})
            self.assertEqual(split.groupby('article').split.nunique().max(),1)

if __name__=='__main__': unittest.main()
