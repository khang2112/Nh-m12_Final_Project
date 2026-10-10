from pathlib import Path
import sys,sqlite3,json
import pandas as pd,numpy as np,joblib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from importlib import import_module
mod=import_module('03_model_stage2')

def test_outputs():
    d=pd.read_csv(ROOT/'data/processed/master_with_clusters.csv')
    assert len(d)==1704 and d.record_id.is_unique and d.isna().sum().sum()==0
    assert d.country.nunique()==142 and sorted(d.year.unique().tolist())==list(range(1952,2008,5))
    assert set(d.Cluster_Label.unique())=={0,1}
    with sqlite3.connect(ROOT/'databases/gapminder_project.sqlite') as con:
        for table in ('master_sparse','master_clean','master_with_clusters'):
            n=con.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0];assert n==1704
    c=pd.read_csv(ROOT/'reports/held_out_test_records.csv')
    assert c.country.nunique()==29
    a=pd.read_csv(ROOT/'reports/imputation_impact.csv')
    assert (a['mean_change_percent'].abs()<1).all()
    m=json.loads((ROOT/'reports/model_results.json').read_text())
    assert .85<=m['explained_variance']<=.95
    assert m['chosen_k']>=2
    x=d.iloc[[0]]
    x=mod.features(x)
    for name in ('regression_winner.joblib','classification_winner.joblib'):
        pred=joblib.load(ROOT/'models'/name).predict(x)
        assert len(pred)==1
    charts=list((ROOT/'charts').glob('*.png'));assert len(charts)>=16
    print('PASS: 1,704 rows; complete data; SQLite round-trip; model inference; 16 figures.')
if __name__=='__main__':test_outputs()
