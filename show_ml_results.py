import json, numpy as np, joblib, os

print('=' * 65)
print('  MODEL USED')
print('=' * 65)
km = joblib.load('ml/outputs/kmeans_model.joblib')
print(f'  Algorithm    : K-Means (sklearn.cluster.KMeans)')
print(f'  k (clusters) : {km.n_clusters}')
print(f'  n_init       : {km.n_init}')
print(f'  max_iter     : {km.max_iter}')
print(f'  random_state : {km.random_state}')
print(f'  Inertia      : {km.inertia_:.2f}')
print()
print('  Secondary    : Gaussian Mixture Model (covariance_type=diag, reg_covar=1e-3)')
print('  Anomaly      : Isolation Forest (contamination=0.02, n_estimators=200)')

print()
print('=' * 65)
print('  FEATURE SET (after correlation analysis)')
print('=' * 65)
with open('ml/outputs/preprocessing_meta.json') as f:
    pre = json.load(f)
for feat in pre['feature_columns']:
    print(f'  {feat}')
print('  [roughness_m dropped: r=+0.989 with slope_deg]')
print('  [ice_score   dropped: r=-0.999 with sunlight_score]')

print()
print('=' * 65)
print('  EVALUATION METRICS')
print('=' * 65)
with open('ml/outputs/evaluation_metrics.json') as f:
    m = json.load(f)
print(f'  Silhouette Score      : {m["silhouette"]:.4f}   (range -1 to +1, higher=better)')
print(f'  Davies-Bouldin Index  : {m["davies_bouldin"]:.4f}   (lower=better)')
print(f'  Calinski-Harabasz     : {m["calinski_harabasz"]:.1f}  (higher=better)')
print(f'  Min cluster size      : {m["min_cluster_size"]:,} cells')
print(f'  Max cluster size      : {m["max_cluster_size"]:,} cells')
print(f'  Total cells           : {m["n_cells"]:,}')

print()
print('=' * 65)
print('  DISCOVERED ARCHETYPES (from data, not pre-defined)')
print('=' * 65)
with open('ml/outputs/cluster_stats.json') as f:
    stats = json.load(f)
for cid, prof in stats.items():
    print(f'  Cluster {cid}: {prof["archetype_label"]}')
    print(f'    Cells      : {prof["n_cells"]:,}  ({prof["pct_of_region"]}% of region)')
    mn = prof["mean"]
    print(f'    Mean       : elevation={mn["elevation_m"]:.1f}m  slope={mn["slope_deg"]:.1f}deg  sunlight={mn["sunlight_score"]:.1f}%')
    sd = prof["std"]
    print(f'    Std        : elevation={sd["elevation_m"]:.1f}m  slope={sd["slope_deg"]:.1f}deg  sunlight={sd["sunlight_score"]:.1f}%')
    print(f'    Strengths  : {prof["strengths"]}')
    print(f'    Limitations: {prof["limitations"]}')
    print()

print('=' * 65)
print('  NAMED SITE ARCHETYPE ASSIGNMENTS')
print('=' * 65)
with open('ml/outputs/named_site_archetypes.json') as f:
    sites = json.load(f)
print(f'  {"Site":<28} {"Cluster":>7}  {"Archetype":<40}  Anomaly')
print(f'  {"-"*28} {"-"*7}  {"-"*40}  -------')
for name, rpt in sites.items():
    anom = '[ANOMALY]' if rpt.get('is_anomaly') else 'no'
    print(f'  {name:<28} C{rpt["cluster_id"]:>6}  {rpt["archetype_label"]:<40}  {anom}')

print()
print('  Per-site feature values vs cluster mean:')
for name, rpt in sites.items():
    print(f'  {name}:')
    sv = rpt["site_feature_values"]
    cm = rpt["cluster_mean"]
    zz = rpt["z_within_cluster"]
    of = rpt["outlier_flags"]
    for feat in sv:
        flag = ' <-- OUTLIER (>2sd)' if of.get(feat) else ''
        print(f'    {feat:<18}: site={sv[feat]:8.2f}  cluster_mean={cm.get(feat,0):8.2f}  z={zz.get(feat,0):+.2f}{flag}')
    print()

print('=' * 65)
print('  GEOGRAPHIC BIAS CHECK')
print('=' * 65)
with open('ml/outputs/clustering_summary.json') as f:
    cs = json.load(f)
geo = cs.get('geographic_bias', {})
agree = geo.get('model_A_env_only_agreement_with_B', 0)
print(f'  Env-only vs Env+Spatial agreement : {agree*100:.1f}%')
print(f'  Verdict: {">80% = spatial coords do NOT dominate" if agree>0.80 else "spatial proximity has influence"}')
gmm_a = cs.get('gmm_agreement')
print(f'  GMM vs K-Means agreement          : {(gmm_a or 0)*100:.1f}%')

print()
print('=' * 65)
print('  ANOMALY DETECTION')
print('=' * 65)
flags = np.load('ml/outputs/anomaly_flags.npy')
print(f'  Total anomalous cells : {flags.sum():,}  ({flags.sum()/len(flags)*100:.1f}%)')
with open('ml/outputs/top_anomalies.json') as f:
    top = json.load(f)
print(f'  Top 5 anomalies:')
print(f'  {"row":>4} {"col":>4}  {"C":>2}  {"elevation":>10}  {"slope":>7}  {"sunlight":>9}')
print(f'  {"-"*4} {"-"*4}  {"-"*2}  {"-"*10}  {"-"*7}  {"-"*9}')
for a in top[:5]:
    print(f'  {a["row"]:>4} {a["col"]:>4}  C{a["cluster_id"]}  {a["elevation_m"]:>9.1f}m  {a["slope_deg"]:>6.1f}deg  {a["sunlight_score"]:>8.1f}%')

print()
print('=' * 65)
print('  SENSITIVITY TESTS')
print('=' * 65)
with open('ml/outputs/sensitivity_tests.json') as f:
    sens = json.load(f)
print(f'  {"Model":<32}  {"k":>3}  {"Silhouette":>10}  {"DB":>8}  {"CH":>10}')
print(f'  {"-"*32}  {"-"*3}  {"-"*10}  {"-"*8}  {"-"*10}')
for model, ks in sens.items():
    for k, met in ks.items():
        print(f'  {model:<32}  {k:>3}  {met["silhouette"]:>10.4f}  {met["davies_bouldin"]:>8.4f}  {met["calinski_harabasz"]:>10.1f}')

print()
print('=' * 65)
print('  OUTPUT FILES')
print('=' * 65)
out = 'ml/outputs'
for fname in sorted(os.listdir(out)):
    size = os.path.getsize(os.path.join(out, fname))
    print(f'  {fname:<45}  {size:>12,} bytes')
