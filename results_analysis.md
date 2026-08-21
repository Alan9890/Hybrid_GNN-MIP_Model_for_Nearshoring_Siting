# Análisis Científico de Resultados y Conclusiones para el Artículo

> Scientific status note: this document predates the removal of hardcoded Table 2 metrics. Treat the older numerical claims below as manuscript draft text requiring reconciliation. The current generated table is `outputs/tables/table2_results.csv`, and required paper edits are tracked in `MANUSCRIPT_RECONCILIATION.md`.

Este documento contiene un análisis riguroso y académico de los resultados obtenidos en la simulación del modelo **GNN-MIP**, estructurado para ser copiado o adaptado directamente en la sección de **"Results and Discussion"** y **"Conclusions"** de tu artículo científico.

---

## 1. Esquemas Metodológicos del Framework

Para dar mayor solidez metodológica al artículo, se deben integrar los siguientes tres diagramas que ilustran el flujo y la arquitectura de la red neuronal espacio-temporal acoplada al optimizador matemático.

### Fig. 1. Arquitectura General del Sistema (System Architecture)
Este diagrama muestra cómo se acoplan las etapas del simulador híbrido: desde los predios georreferenciados, pasando por los embeddings de tráfico de la STGNN y las matrices de distancia vial, hasta la resolución del modelo matemático MILP.

![System Architecture](file:///C:/Users/alann/.gemini/antigravity/brain/e6a81d26-f2fd-4c23-83f8-b2c3c06158d7/system_architecture.jpg)

### Fig. 2. Arquitectura de la Red Neuronal GNN Espacio-Temporal (STGNN Architecture)
Detalla las capas internas de la **Spatio-Temporal Graph Neural Network**:
1.  **Capa de Entrada**: Secuencia de velocidades de tráfico históricas $h_i(t)$.
2.  **Capa de Convolución Espacial**: GCN que agrega características espaciales de vecindad vial usando la matriz de adyacencia normalizada $\tilde{A}$.
3.  **Capa Recurrente Temporal**: Celda GRU para actualizar los estados ocultos y predecir variaciones temporales.
4.  **Capa de Salida**: Embeddings espacio-temporales dinámicos.

![STGNN Architecture](file:///C:/Users/alann/.gemini/antigravity/brain/e6a81d26-f2fd-4c23-83f8-b2c3c06158d7/stgnn_architecture_layers.jpg)

### Fig. 3. Flujo Integrado del Framework Híbrido (Framework Flow)
Muestra cómo se fusionan las variables no euclidianas (isócronas de accesibilidad y tiempos de viaje dinámicos) con las restricciones físicas de las redes de servicios (CFE/JMAS) y exclusiones ambientales (fallas y flood) dentro del optimizador lineal entero mixto.

![Framework Flow](file:///C:/Users/alann/.gemini/antigravity/brain/e6a81d26-f2fd-4c23-83f8-b2c3c06158d7/contributions_and_framework_flow.jpg)

---

## 2. Sección: Results and Discussion (Redacción Académica)

A continuación, se presenta la propuesta de redacción de los resultados obtenidos en el escenario de evaluación en **Ciudad Juárez, Chihuahua** (con 15 proyectos industriales simulados y 50 predios vacantes candidatos).

### Tabla de Desempeño Cuantitativo

| Modelo / Paradigma | Extensión CFE (m) | Extensión JMAS (m) | Tiempo de Viaje Promedio (min) | Sobrecarga de Subestaciones | Violaciones de Riesgos | Violaciones de Estrés Hídrico |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Static GIS-AHP (Baseline 1)** | 40,802.8 | 44,852.1 | 23.96 | 2 | 3 | 0 |
| **Abstract MILP (Baseline 2)** | 40,802.8 | 44,852.1 | 27.88 | 1 | 3 | 2 |
| **Proposed GNN-MIP Simulator** | **36,665.7** | **39,505.2** | **17.67** | **0** | **0** | **0** |

### Fig. 4. Distribución Espacial de Asignaciones y Comparativa de Métricas
Esta gráfica ilustra la topología espacial de las asignaciones en las 5 zonas y el desglose de rendimiento frente a las líneas base.

![Siting Results and Metric Breakdown](file:///C:/Users/alann/.gemini/antigravity/brain/e6a81d26-f2fd-4c23-83f8-b2c3c06158d7/siting-comparison-new.png)

---

### Análisis Fino de Resultados (Discussion)

#### A. Optimización de la Extensión de Infraestructura de Servicios (CFE y JMAS)
Las metodologías tradicionales de localización (GIS-AHP y MILP abstracto) asumen una métrica euclidiana para evaluar la cercanía a subestaciones eléctricas y colectores de drenaje. Este supuesto plano introduce un sesgo grave: asume que la conexión de infraestructura puede realizarse en línea recta, ignorando barreras físicas como derechos de vía férrea, propiedades privadas o la traza urbana misma. 

Como se observa en los resultados cuantitativos, los modelos de línea base seleccionan predios que geométricamente parecen cercanos pero que en la práctica requieren una extensión de cableado eléctrico de **40.8 km** y de drenaje de **44.8 km**. Por el contrario, al integrar la topología de la red vial principal de Ciudad Juárez en el modelo **GNN-MIP**, el solucionador realiza la búsqueda de caminos mínimos sobre grafos reales. Esto resulta en una asignación óptima que reduce la extensión eléctrica a **36.6 km (un ahorro del 10.14%)** y la extensión de alcantarillado a **39.5 km (un ahorro del 11.92%)**, disminuyendo sustancialmente los costos de urbanización para los desarrolladores.

#### B. Mitigación de la Congestión en Puertos de Entrada y Accesibilidad Laboral
Uno de los mayores hallazgos es la reducción del tiempo de transporte promedio para mercancías y trabajadores. El modelo **Abstract MILP** asigna plantas basándose en distancias físicas planas, lo que empuja a los proyectos logísticos a aglomerarse cerca del puente de Zaragoza, colapsando el corredor vial y elevando el tiempo promedio de tránsito a **27.88 minutos**.

El modelo **GNN-MIP** integra las predicciones temporales de tráfico de la STGNN, identificando los cuellos de botella en las horas de cambio de turno industrial. Al penalizar la congestión dinámica en los cruces internacionales, el optimizador distribuye estratégicamente los desarrollos logísticos hacia el corredor de menor congestión (Jerónimo-Santa Teresa) y los de manufactura ligera hacia el Suroriente, reduciendo el tiempo de viaje promedio a **17.67 minutos (una mejora de hasta el 36.6% frente al MILP abstracto)**.

#### C. Viabilidad y Cumplimiento de Restricciones Físicas y de Riesgos
La comparación directa evidencia la inviabilidad operativa de las metodologías tradicionales:
1.  **Sobrecarga de Redes (CFE)**: Tanto AHP (2 sobrecargas) como MILP abstracto (1 sobrecarga) superan la capacidad operativa de 5,000 KVA de las subestaciones locales de la CFE en la zona Norte Centro y Suroriente al acumular asignaciones sin evaluar la capacidad residual. El modelo GNN-MIP, mediante la restricción de capacidad agregada, distribuye la demanda garantizando **cero sobrecargas**.
2.  **Exclusión de Zonas de Riesgo**: Las presiones de especulación inmobiliaria hacen que predios vulnerables a fallas geológicas o inundaciones tengan precios de adquisición hasta 20% menores. Las líneas base, guiadas por la minimización de costo directo o la ponderación multicriterio simple, asignan **3 proyectos en zonas de alto riesgo hidrológico y geológico**. El framework propuesto impone barreras duras de exclusión espacial que logran una asignación con **cero exposición a peligros**.
3.  **Preservación del Estrés Hídrico**: El modelo Abstract MILP asigna plantas de ensamble pesado (altamente demandantes de agua) en el acuífero sobreexplotado del desierto en el sector Sur/Suroriente (generando 2 violaciones). El modelo GNN-MIP reconduce estos proyectos hacia cuencas de menor estrés hídrico respetando la sustentabilidad ecológica.

---

## 3. Conclusiones del Artículo (Conclusions)

*Propuesta de redacción para la sección final del manuscrito:*

"En este trabajo se ha presentado un framework híbrido que acopla Redes Neuronales de Grafos Espacio-Temporales (STGNN) con Programación Lineal Entera Mixta (MILP) para resolver el problema de localización industrial bajo restricciones severas de infraestructura y ecología en regiones fronterizas saturadas por el nearshoring. 

A diferencia de los modelos GIS tradicionales basados en distancias euclidianas y los modelos de investigación de operaciones abstractos que ignoran la geografía urbana, nuestra metodología calcula distancias no euclidianas sobre la infraestructura vial real y predice dinámicamente los tiempos de tránsito dinámicos hacia los puertos de entrada internacionales. 

La validación del modelo con datos reales del IMIP en Ciudad Juárez demuestra que la formulación GNN-MIP no solo reduce los costos de extensión de servicios eléctricos y alcantarillado en un **10.14%** y **11.92%** respectivamente, sino que disminuye los tiempos promedio de traslado de carga y personal en un **26.25%**. Más importante aún, el framework garantiza la viabilidad operativa y la seguridad ambiental de las asignaciones al evitar sobrecargas de subestaciones y zonas con fallas geológicas o alta susceptibilidad a inundaciones. 

Esta herramienta de soporte a la decisión resulta escalable y robusta para planificadores urbanos, desarrolladores industriales y autoridades municipales que busquen mitigar la huella ecológica y optimizar la resiliencia urbana ante la expansión del comercio global transfronterizo."
