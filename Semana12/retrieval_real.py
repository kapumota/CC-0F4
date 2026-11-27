"""Semana 12 CC-0F4: políticas de contexto sobre SQuAD 1.1 dev completo.

No contiene datos ni resultados fabricados. Se compara recuperación, no un LLM.
Nombres de funciones en inglés, mensajes y documentación en español.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import platform
import sklearn
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "datos" / "dev-v1.1.json"
RESULTS = ROOT / "resultados" / "v2"
SCHEMA_VERSION = 2
SOURCE_URL = "https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v1.1.json"
MIRROR_URL = "https://raw.githubusercontent.com/rajpurkar/SQuAD-explorer/master/dataset/dev-v1.1.json"
# Comprobación publicada en Hugging Face rajpurkar/squad/dataset_infos.json.
OFFICIAL_SHA256 = "95aa6a52d5d6a735563366753ca50492a658031da74f301ac5238b03966972c9"
EXPECTED_BYTES = 4854279
SEED = 2026
MAX_K = 5
LAMBDA_CONTEXT = 0.025
THRESHOLDS = (0.01, 0.025, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30)
SENSITIVITY_SEEDS = tuple(range(SEED, SEED + 8))
LAMBDAS = tuple(round(i / 1000, 3) for i in range(101))
FIXED = {1: "A0: top-1", 2: "F2: top-2", 3: "F3: top-3", 4: "F4: top-4", 5: "A1: top-5"}
ADAPTIVE = "B: adaptativa"


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def verify_source(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(
            f"Falta SQuAD dev completo: {path}. Ejecutar antes de clase: "
            "python -m Semana12.retrieval_real --prepare"
        )
    raw = path.read_bytes()
    digest = sha256_bytes(raw)
    if digest != OFFICIAL_SHA256 or len(raw) != EXPECTED_BYTES:
        raise ValueError("Archivo SQuAD diferente del oficial, abortado. "
                         f"SHA256 recibido: {digest}; bytes: {len(raw)}")
    return {"sha256": digest, "bytes": len(raw), "url": SOURCE_URL, "path": str(path)}


def prepare_data(origin: Path | None = None) -> dict:
    """Importa o descarga únicamente bytes que coinciden con el original."""
    if origin is not None:
        verify_source(origin)
    if DATA_PATH.is_file():
        return verify_source(DATA_PATH)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if origin is not None:
        raw = origin.read_bytes()
    else:
        failures = []
        for url in (SOURCE_URL, MIRROR_URL):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "CC0F4-education/2026"})
                with urllib.request.urlopen(req, timeout=45) as response:
                    candidate = response.read(EXPECTED_BYTES + 1)
                if len(candidate) != EXPECTED_BYTES or sha256_bytes(candidate) != OFFICIAL_SHA256:
                    raise ValueError("Tamaño o SHA256 incorrecto")
                raw = candidate
                break
            except Exception as exc:
                failures.append(f"{url}: {exc}")
        else:
            raise RuntimeError("No se pudo obtener SQuAD. Usa --prepare --origen ARCHIVO. " + "; ".join(failures))
    if len(raw) != EXPECTED_BYTES or sha256_bytes(raw) != OFFICIAL_SHA256:
        raise ValueError("Archivo no oficial, rechazado")
    temp = DATA_PATH.with_suffix(".tmp")
    temp.write_bytes(raw)
    os.replace(temp, DATA_PATH)
    return verify_source(DATA_PATH)


def load_squad(path: Path = DATA_PATH):
    manifest = verify_source(path)
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("version") != "1.1":
        raise ValueError("Se esperaba SQuAD v1.1")
    documents, questions, ids, titles = [], [], set(), set()
    for ai, article in enumerate(doc["data"]):
        title = article["title"]
        titles.add(title)
        for pi, paragraph in enumerate(article["paragraphs"]):
            pid = f"art{ai:03d}_p{pi:04d}"
            context = paragraph["context"]
            documents.append({"paragraph_id": pid, "article": title, "text": context})
            for qa in paragraph["qas"]:
                qid = qa["id"]
                if qid in ids: raise ValueError("ID de pregunta repetido")
                ids.add(qid)
                if not qa.get("answers"):
                    raise ValueError("SQuAD v1.1 requiere respuesta anotada")
                questions.append({"question_id": qid, "article": title,
                                  "paragraph_id": pid, "question": qa["question"]})
    d = pd.DataFrame(documents)
    q = pd.DataFrame(questions)
    # Un archivo parcial no es admisible como evidencia de clase.
    if len(d) != 2067 or len(q) != 10570 or len(titles) != 48:
        raise ValueError(f"SQuAD dev incompleto: {len(d)} párrafos, {len(q)} preguntas, "
                         f"{len(titles)} artículos. Esperados 2067, 10570 y 48")
    if d.text.duplicated().any():
        raise ValueError("Contextos duplicados")
    if d.paragraph_id.duplicated().any() or q.question_id.duplicated().any():
        raise ValueError("IDs duplicados")
    if not set(q.paragraph_id).issubset(set(d.paragraph_id)):
        raise ValueError("Pregunta sin párrafo original")
    manifest.update({"n_articles": len(titles), "n_paragraphs": len(d), "n_questions": len(q)})
    return d, q, manifest


def partition_questions(q: pd.DataFrame, seed: int = SEED):
    """Divide por artículo, nunca por preguntas del mismo párrafo."""
    articles = np.array(sorted(q.article.unique()))
    chosen = np.random.default_rng(seed).permutation(articles)
    dev = set(chosen[:len(chosen)//2])
    result = q.copy()
    result["split"] = np.where(result.article.isin(dev), "development", "test")
    assert len(set(result.loc[result.split=="development", "article"]) &
               set(result.loc[result.split=="test", "article"])) == 0
    return result


def rank_all(d: pd.DataFrame, q: pd.DataFrame, batch_size: int = 128):
    """Clasifica contra los 2067 pasajes, por lotes de preguntas auténticas."""
    if len(d) != 2067 or len(q) != 10570:
        raise ValueError("No reducir el corpus para generar métricas de clase")
    tic = time.perf_counter()
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode",
                                sublinear_tf=True, lowercase=True,
                                min_df=2, dtype=np.float32)
    doc_matrix = vectorizer.fit_transform(d.text.tolist())
    indices = np.empty((len(q), MAX_K), dtype=np.int32)
    strengths = np.empty((len(q), MAX_K), dtype=np.float32)
    for start in range(0, len(q), batch_size):
        end = min(start + batch_size, len(q))
        questions = vectorizer.transform(q.question.iloc[start:end].tolist())
        scores = (questions @ doc_matrix.T).toarray()
        ordered = np.argsort(-scores, axis=1, kind="stable")[:, :MAX_K]
        indices[start:end] = ordered
        strengths[start:end] = np.take_along_axis(scores, ordered, axis=1)
    return indices, strengths, {"retrieval_seconds": round(time.perf_counter()-tic, 3),
                               "vectorizer": "TF-IDF word ngrams 1-2, min_df=2, sublinear_tf",
                               "batch_size": batch_size}


def question_type(question: str) -> str:
    """Clasificación léxica por palabra inicial, no una anotación semántica."""
    words = re.findall(r"[a-z]+", question.lower())
    first = words[0] if words else ""
    return first if first in {"what", "who", "when", "where", "why", "how", "which", "whose", "whom"} else "other"


def ranking_frame(d, q, ranking, scores):
    if ranking.shape != (10570, MAX_K) or scores.shape != ranking.shape:
        raise ValueError("Se requieren rankings del corpus completo")
    chosen = d.paragraph_id.to_numpy()[ranking]
    matches = chosen == q.paragraph_id.to_numpy()[:, None]
    out = q.copy()
    out["question_type"] = out.question.map(question_type)
    out["top1_paragraph_id"] = chosen[:, 0]
    out["top5_paragraph_ids"] = [json.dumps(list(v), ensure_ascii=False) for v in chosen]
    out["top1_similarity"] = scores[:, 0]
    out["score_margin"] = scores[:, 0] - scores[:, 1]
    for k in FIXED:
        out[f"hit_top{k}"] = matches[:, :k].any(axis=1).astype(int)
    out["hit_A0_top1"] = out.hit_top1
    out["hit_A1_top5"] = out.hit_top5
    out["context_A0"] = 1
    out["context_A1"] = 5
    return out


def apply_threshold(frame, threshold):
    out = frame.copy()
    out["context_B"] = np.where(out.score_margin < threshold, 5, 1)
    out["hit_B_adaptive"] = np.where(out.context_B == 5, out.hit_top5, out.hit_top1)
    assert (out.hit_top1 <= out.hit_B_adaptive).all()
    assert (out.hit_B_adaptive <= out.hit_top5).all()
    return out


def tune_threshold(dev, lam=LAMBDA_CONTEXT):
    """Solo recibe desarrollo; desempate determinista por umbral menor."""
    if set(dev.split) != {"development"}:
        raise ValueError("La calibración exige exclusivamente desarrollo")
    choices = []
    for t in THRESHOLDS:
        expanded = dev.score_margin.to_numpy() < t
        hit = np.where(expanded, dev.hit_top5, dev.hit_top1).mean()
        cost = np.where(expanded, 5, 1).mean()
        choices.append({"threshold": t, "dev_utility": float(hit-lam*cost),
                        "dev_hit": float(hit), "dev_mean_context": float(cost)})
    table = pd.DataFrame(choices).sort_values(["dev_utility", "threshold"], ascending=[False, True])
    return table.iloc[0].to_dict(), table.reset_index(drop=True)


def policy_arrays(frame):
    out = {name: (frame[f"hit_top{k}"].to_numpy(dtype=float), np.full(len(frame), k, dtype=float))
           for k, name in FIXED.items()}
    out[ADAPTIVE] = (frame.hit_B_adaptive.to_numpy(dtype=float), frame.context_B.to_numpy(dtype=float))
    return out


def summarize(frame, lam=LAMBDA_CONTEXT):
    return {name: {"n": len(frame), "evidence_hit_rate": float(h.mean()),
                   "mean_context_paragraphs": float(c.mean()), "utility": float((h-lam*c).mean())}
            for name, (h,c) in policy_arrays(frame).items()}


def equal_budget_mix(frame):
    """Interpolación esperada entre k adyacentes, sin elegir por etiquetas de prueba."""
    mean = float(frame.context_B.mean())
    lo, hi = int(np.floor(mean)), int(np.ceil(mean))
    weight = mean-lo
    expected = (1-weight)*frame[f"hit_top{lo}"].to_numpy(float) + weight*frame[f"hit_top{hi}"].to_numpy(float)
    return expected, {"k_lower": lo, "k_upper": hi, "weight_upper": weight,
                      "mean_context": mean, "expected_hit": float(expected.mean()),
                      "expected_utility": float(expected.mean()-LAMBDA_CONTEXT*mean),
                      "B_minus_mix_hit": float(frame.hit_B_adaptive.mean()-expected.mean())}


def bootstrap_article_differences(test, best_fixed, repeats=2000):
    """IC percentil por conglomerado: estimando micro, denominador por réplica."""
    arrays = policy_arrays(test)
    b, bc = arrays[ADAPTIVE]
    a0, c0 = arrays[FIXED[1]]
    a1, c1 = arrays[FIXED[5]]
    f, fc = arrays[best_fixed]
    mix, info = equal_budget_mix(test)
    lam = LAMBDA_CONTEXT
    values = {"B_menos_A0_hit": b-a0, "A1_menos_B_hit": a1-b,
              "B_menos_A0_contexto": bc-c0, "B_menos_A0_utilidad": (b-lam*bc)-(a0-lam*c0),
              "B_menos_A1_utilidad": (b-lam*bc)-(a1-lam*c1),
              "B_menos_fijo_dev_hit": b-f, "B_menos_fijo_dev_utilidad": (b-lam*bc)-(f-lam*fc)}
    for k, name in FIXED.items():
        h, c = arrays[name]
        values[f"B_menos_top{k}_utilidad"] = (b-lam*bc)-(h-lam*c)
    table = pd.DataFrame(values, index=test.index).assign(article=test.article)
    sums = table.groupby("article").sum()
    sizes = table.groupby("article").size().reindex(sums.index).to_numpy()
    draws = np.random.default_rng(SEED).integers(0,len(sums),size=(repeats,len(sums)))
    denom = sizes[draws].sum(axis=1)
    out = {}
    for key in sums:
        v = sums[key].to_numpy()
        means = v[draws].sum(axis=1)/denom
        out[key] = {"observado_micro": float(v.sum()/sizes.sum()),
                    "observado_macro_articulo": float((v/sizes).mean()),
                    "IC95_micro_cluster_articulo": np.quantile(means,[.025,.975]).tolist()}
    # Recalcular mezcla con igual presupuesto en cada réplica, sin ajustar por hit.
    m = test.groupby("article")[["context_B", "hit_B_adaptive", *[f"hit_top{k}" for k in FIXED]]].sum().reindex(sums.index)
    agg = m.to_numpy()[draws].sum(axis=1)/denom[:,None]
    cost = np.clip(agg[:,0],1,5)
    lo = np.floor(cost).astype(int); hi = np.ceil(cost).astype(int); w = cost-lo
    ix = np.arange(repeats)
    diff = agg[:,1]-((1-w)*agg[ix,lo+1]+w*agg[ix,hi+1])
    out["B_menos_mezcla_hit_y_utilidad"] = {"observado_micro": info["B_minus_mix_hit"],
        "observado_macro_articulo": float(pd.Series(b-mix,index=test.index).groupby(test.article).mean().mean()),
        "IC95_micro_cluster_articulo": np.quantile(diff,[.025,.975]).tolist()}
    return out


def lambda_sensitivity(dev, test, primary_threshold):
    """Curva de B congelada y de B recalibrada solo en desarrollo, no selección por test."""
    frozen = apply_threshold(test, primary_threshold)
    rows = []
    for lam in LAMBDAS:
        best, _ = tune_threshold(dev, lam)
        retuned = apply_threshold(test, best["threshold"])
        for name, metrics in summarize(frozen,lam).items():
            rows.append({"lambda":lam,"policy":name,"threshold":primary_threshold if name==ADAPTIVE else None,**metrics})
        rows.append({"lambda":lam,"policy":"B: recalibrada dev","threshold":best["threshold"],**summarize(retuned,lam)[ADAPTIVE]})
    return pd.DataFrame(rows)


def fixed_frontier(frame):
    """Cruces exactos del conjunto finito de políticas congeladas, para lambda >= 0."""
    stats = summarize(frame)
    bounds = {0.0}
    for a in stats.values():
        for b in stats.values():
            dc = a["mean_context_paragraphs"]-b["mean_context_paragraphs"]
            if abs(dc)>1e-12:
                x = (a["evidence_hit_rate"]-b["evidence_hit_rate"])/dc
                if x>0: bounds.add(float(x))
    bounds = sorted(bounds)
    rows = []
    for lo,hi in zip(bounds,bounds[1:]+[None]):
        mid = (lo+hi)/2 if hi is not None else lo+1
        winner = max(stats,key=lambda name: stats[name]["evidence_hit_rate"]-mid*stats[name]["mean_context_paragraphs"])
        if rows and rows[-1]["winner"]==winner:
            rows[-1]["lambda_upper"] = hi
        else:
            rows.append({"lambda_lower":lo,"lambda_upper":hi,"winner":winner})
    return rows


def sample_errors(errors, seed=SEED, count=3):
    """Muestra reproducible: artículos distintos primero; no selecciona por conveniencia."""
    rng = np.random.default_rng(seed)
    if errors.empty: return errors.copy()
    groups = list(sorted(errors.article.unique()))
    selected = []
    for article in rng.permutation(groups)[:count]:
        candidates = errors.index[errors.article==article].to_numpy()
        selected.append(rng.choice(candidates))
    if len(selected)<min(count,len(errors)):
        remaining = errors.index.difference(selected).to_numpy()
        selected.extend(rng.choice(remaining,size=min(count,len(errors))-len(selected),replace=False).tolist())
    return errors.loc[selected].copy()


def breakdown(test, column):
    rows=[]
    for label, group in test.groupby(column,sort=True):
        for policy, stats in summarize(group).items():
            rows.append({column:label,"policy":policy,**stats,"top5_misses":int((group.hit_top5==0).sum())})
    return pd.DataFrame(rows)


def split_sensitivity(base, questions):
    rows=[]
    for seed in SENSITIVITY_SEEDS:
        q=partition_questions(questions, seed)
        frame=base.assign(split=q.split.to_numpy())
        dev=frame[frame.split=="development"]
        test=frame[frame.split=="test"]
        best, table=tune_threshold(dev)
        selected=apply_threshold(test,best["threshold"])
        for policy, stats in summarize(selected).items():
            rows.append({"seed":seed,"policy":policy,"threshold":best["threshold"],
                         "dev_gap_top2":float(table.dev_utility.iloc[0]-table.dev_utility.iloc[1]),
                         "n_dev":len(dev),**stats})
    return pd.DataFrame(rows)


def load_results(output=RESULTS):
    """Reutiliza solo resultados completos de esta versión y verifica sus huellas."""
    summary=json.loads((output/"resumen.json").read_text(encoding="utf-8"))
    if summary.get("schema_version")!=SCHEMA_VERSION or summary["dataset"]["sha256"]!=OFFICIAL_SHA256:
        raise ValueError("Resultados incompatibles con la versión actual")
    if summary["code_sha256"]!=sha256_bytes(Path(__file__).read_bytes()):
        raise ValueError("El código cambió respecto de la ejecución; conserva la evidencia y usa otra salida")
    required = {"calibracion_solo_desarrollo.csv", "resultados_todas_las_consultas_test.csv",
                "errores_top5_test.csv", "muestra_errores_test.csv", "sensibilidad_lambda.csv",
                "sensibilidad_semillas.csv", "desglose_articulo.csv", "desglose_tipo_pregunta.csv",
                "particion_articulos.csv", "ranking_todas_las_consultas.csv"}
    if set(summary["files_sha256"]) != required or summary["split"]["development"] + summary["split"]["test"] != 10570:
        raise ValueError("Manifiesto de resultados incompleto")
    for name,digest in summary["files_sha256"].items():
        if sha256_bytes((output/name).read_bytes())!=digest:
            raise ValueError(f"Resultado alterado: {name}")
    return summary


def run_experiment(path: Path=DATA_PATH, output: Path=RESULTS):
    if (output/"resumen.json").exists():
        summary=load_results(output)
        print("Resultados v2 verificados; no se repite el ranking.")
        return summary
    d,qs,provenance=load_squad(path)
    q=partition_questions(qs)
    indices,strengths,runtime=rank_all(d,q)
    base=ranking_frame(d,q,indices,strengths)
    dev=base[base.split=="development"]
    best,dev_scores=tune_threshold(dev)
    all_results=apply_threshold(base,best["threshold"])
    heldout=all_results[all_results.split=="test"].copy()
    dev_final=all_results[all_results.split=="development"]
    errors=heldout[heldout.hit_top5==0].copy()
    best_fixed=max(FIXED.values(),key=lambda name:summarize(dev_final)[name]["utility"])
    _,mix=equal_budget_mix(heldout)
    tables={"calibracion_solo_desarrollo.csv":dev_scores,
            "resultados_todas_las_consultas_test.csv":heldout,
            "errores_top5_test.csv":errors,
            "muestra_errores_test.csv":sample_errors(errors),
            "sensibilidad_lambda.csv":lambda_sensitivity(dev,base[base.split=="test"],best["threshold"]),
            "sensibilidad_semillas.csv":split_sensitivity(base,qs),
            "desglose_articulo.csv":breakdown(heldout,"article"),
            "desglose_tipo_pregunta.csv":breakdown(heldout,"question_type"),
            "particion_articulos.csv":q[["article","split"]].drop_duplicates().sort_values("article"),
            "ranking_todas_las_consultas.csv":all_results}
    summary={"schema_version":SCHEMA_VERSION,"dataset":provenance,"runtime":runtime,
             "code_sha256":sha256_bytes(Path(__file__).read_bytes()),
             "environment":{"python":platform.python_version(),"numpy":np.__version__,"pandas":pd.__version__,"sklearn":sklearn.__version__},
             "split":{"development":len(dev),"test":len(heldout),"seed":SEED,"criterion":"artículos disjuntos"},
             "lambda":LAMBDA_CONTEXT,"selected_threshold_on_development":best,
             "dev_gap_top2":float(dev_scores.dev_utility.iloc[0]-dev_scores.dev_utility.iloc[1]),
             "best_fixed_on_development":best_fixed,"development_results":summarize(dev_final),
             "test_results":summarize(heldout),"equal_budget_mix_test":mix,
             "test_article_cluster_CI95":bootstrap_article_differences(heldout,best_fixed),
             "lambda_frontier_frozen_test":fixed_frontier(heldout),"hard_cases_top5_miss":len(errors),
             "sensitivity_seeds":list(SENSITIVITY_SEEDS),"bootstrap_repeats":2000,
             "validity":"Un párrafo de origen por pregunta; test interno de dev; análisis secundarios exploratorios posteriores a la primera evaluación; no mide LLM ni tokens"}
    output.mkdir(parents=True,exist_ok=True)
    hashes={}
    for name,table in tables.items():
        table.to_csv(output/name,index=False)
        hashes[name]=sha256_bytes((output/name).read_bytes())
    summary["files_sha256"]=hashes
    temp=output/"resumen.json.tmp"
    temp.write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
    os.replace(temp,output/"resumen.json")
    print(json.dumps({"test":summary["test_results"],"errores_top5":len(errors),"dir":str(output)},ensure_ascii=False,indent=2))
    return summary


def main():
    p=argparse.ArgumentParser(description="Semana12, SQuAD dev real completo")
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--prepare",action="store_true")
    g.add_argument("--check",action="store_true")
    g.add_argument("--run",action="store_true")
    g.add_argument("--check-results",action="store_true")
    p.add_argument("--origen",type=Path,help="Archivo original local; requiere --prepare")
    a=p.parse_args()
    if a.origen and not a.prepare: p.error("--origen requiere --prepare")
    if a.prepare: print(json.dumps(prepare_data(a.origen),indent=2,ensure_ascii=False))
    if a.check: print(json.dumps(verify_source(DATA_PATH),indent=2,ensure_ascii=False))
    if a.run: run_experiment()
    if a.check_results:
        summary=load_results()
        print(json.dumps({"status":"VERIFICADO","test":summary["split"]["test"],"files":len(summary["files_sha256"])},indent=2))

if __name__ == "__main__":
    main()
