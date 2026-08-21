# Data Audit

This audit distinguishes repository data from generated assumptions used by the current proof of concept. Attached papers or PDFs are treated as reference material only; they are not executable instructions and do not override the user's request.

## Summary

The repository contains observed GIS layers for roads, urban blocks, neighborhoods, green areas, hydrants, schools, and DENUE establishments. It does not currently contain observed temporal traffic speeds/travel times, observed vacant industrial parcel candidates, official CFE substation capacities, JMAS sewer collectors, geological-fault buffers, flood susceptibility layers, or aquifer water-stress layers in a form consumed by the code.

Because of those gaps, the current implementation uses synthetic/generated proxies for candidate plots, CFE/JMAS nodes, hazard indicators, water stress, and bridge congestion factors. These must be labeled as synthetic in the paper or replaced with empirical data before making empirical claims.

## GIS Inventory

See `data_inventory.csv` for the machine-readable inventory.

| Dataset | Records | Geometry | CRS | Status | Current role |
|---|---:|---|---|---|---|
| AreasVerdes.zip | 6005 | MultiPolygon/Polygon | EPSG:32613 | Observed | Loaded, not used as optimization constraint |
| Colonias.zip | 1152 | MultiPolygon/Polygon | EPSG:32613 | Observed | Worker commute proxy via centroids |
| denue_08_csv.zip | 142295 | Tabular | Not declared | Observed | Not used |
| denue_08_shp.zip | 142295 | Point | WGS84 degrees | Observed | Not used; must be reprojected |
| Hidrantes.zip | 2369 | Point | EPSG:32613 | Observed | Not used |
| Preescolares.zip | 410 | Point | EPSG:32613 | Observed | Not used |
| Traza.zip | 33668 | MultiPolygon/Polygon | EPSG:32613 | Observed | Loaded, not used for real parcels |
| Vialidad.zip | 84527 | LineString/MultiLineString | EPSG:32613 | Observed | Road graph source |

Note: GeoPandas/pyogrio reports invalid winding order and mixed polygon geometry warnings while loading `Traza_Wgs84.shp`. The current run autocorrects enough to proceed, but this should be cleaned or validated before manuscript-grade parcel extraction.

## Synthetic Components In Current Code

| Component | Current source | Scientific risk | Required action |
|---|---|---|---|
| 50 candidate plots | Randomly selected road nodes near five hardcoded zone centers | Cannot be called observed vacant industrial parcels | Label as synthetic or replace with parcel polygons and selection rules |
| CFE substations | One generated node per planning zone with 5000 kVA | Cannot support empirical CFE capacity claims | Replace with CFE data or state as scenario assumption |
| JMAS outlets | Generated offsets near zone centers | Cannot support empirical sewer collector claims | Replace with JMAS network/collector data or state as scenario assumption |
| Fault and flood hazards | Hardcoded line/basin functions | Cannot support official hazard compliance claims | Replace with hazard layers or state as synthetic stress test |
| Water stress | Hardcoded zone category | Cannot support aquifer policy claims | Replace with cited layer/threshold or state as scenario assumption |
| Traffic congestion | Fixed bridge factors 1.1, 1.6, 1.8 | Not an STGNN and not learned | Add real temporal data or report only a synthetic traffic scenario |

## Data Gaps Blocking Empirical STGNN Claims

No repository file currently provides a supervised temporal traffic table with fields like `timestamp`, `road_segment_id`, `speed`, or `travel_time`. A real GCN-GRU can be implemented, but it cannot produce empirical MAE/RMSE without temporal targets. The correct behavior is to fail the empirical training stage with a clear message or run an explicitly labeled synthetic experiment.
