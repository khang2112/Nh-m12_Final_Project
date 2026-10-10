# ORIGINAL REAL-WORLD DATASET URL: https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv
"""SECOND DATABASE (vector): ChromaDB local persistent collection and round-trip verification.
Install full requirements: pip install -r requirements.txt
Run AFTER src/03_model_stage2.py: python src/04_chromadb_vector.py
If chromadb is not installed, no data is fabricated or falsely marked as ingested.
"""
from pathlib import Path
import json
import numpy as np,pandas as pd,joblib
ROOT=Path(__file__).resolve().parents[1]

def main():
    try:
        import chromadb
    except ImportError as e:
        msg='ChromaDB CHƯA được nạp: môi trường hiện tại chưa cài chromadb. Chạy pip install -r requirements.txt sau đó python src/04_chromadb_vector.py.'
        (ROOT/'reports/chroma_status.json').write_text(json.dumps({'ingested':False,'reason':msg},ensure_ascii=False,indent=2),encoding='utf8')
        raise RuntimeError(msg) from e
    import sys
    sys.path.insert(0,str(ROOT/'src'))
    from importlib import import_module
    model_stage2=import_module('03_model_stage2')
    df=pd.read_csv(ROOT/'data/processed/master_with_clusters.csv')
    artifacts=joblib.load(ROOT/'models/clustering_pipeline.joblib')
    x=model_stage2.features(df)
    original=artifacts['preprocessor'].transform(x)
    matrix=artifacts['pca'].transform(original)
    vectors=np.asarray(matrix,dtype='float32')
    client=chromadb.PersistentClient(path=str(ROOT/'databases/chroma_db'))
    coll=client.get_or_create_collection('country_year_embeddings',metadata={'hnsw:space':'l2'})
    docs=[];meta=[]
    for r in df.itertuples(index=False):
        docs.append(f'{r.country}; {r.year}; GDP per capita {r.gdp_per_capita:.2f}; life expectancy {r.life_expectancy:.2f}; group {r.Cluster_Label}')
        meta.append({'country':str(r.country),'year':int(r.year),'continent':str(r.continent),'cluster':int(r.Cluster_Label)})
    ids=df.record_id.astype(str).tolist()
    for start in range(0,len(ids),200):
        stop=start+200
        coll.upsert(ids=ids[start:stop],embeddings=vectors[start:stop].tolist(),
                    metadatas=meta[start:stop],documents=docs[start:stop])
    assert coll.count()==len(df)
    nearest=coll.query(query_embeddings=[vectors[0].tolist()],n_results=3)
    assert nearest['ids'] and ids[0] in nearest['ids'][0]
    status={'ingested':True,'backend':'ChromaDB PersistentClient','collection':coll.name,
        'count':coll.count(),'dimensions':vectors.shape[1],'probe_record':ids[0],'nearest_ids':nearest['ids'][0]}
    (ROOT/'reports/chroma_status.json').write_text(json.dumps(status,indent=2),encoding='utf8')
    print(json.dumps(status,indent=2))
if __name__=='__main__':main()
