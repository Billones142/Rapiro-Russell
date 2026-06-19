# **Trabajo Práctico Integrador \- Extensión de Sistema Experto Híbrido para Ayuda al Diagnóstico Dermatológico con Visión por Computadora**

## 

## Gabriel S. Martinez A., Stefano Merino De R.

## Universidad de la Cuenca del Plata

## Lic. Escalante Jaquelin, Ing. Gilda R. Romero, Ing. Sergio Lapertosa, Lic. Silvina Podestá

## Junio 2026

**Índice**

[**Resumen del Problema	3**](#resumen-del-problema)

[**Descripción general del Sistema Inteligente	4**](#descripción-general-del-sistema-inteligente)

[**Comportamiento Esperado	5**](#comportamiento-esperado)

[**Alcance del Proyecto	6**](#alcance-del-proyecto)

[Incluido en el alcance	6](#heading)

[**Fuera del alcance:	7**](#heading)

[**● Diagnóstico definitivo o automatizado: el sistema entrega una orientación de apoyo; la decisión es del especialista.	7**](#heading)

[**● Acceso del paciente al resultado o autodiagnóstico.	7**](#heading)

[**● Interacción hablada con el paciente (síntesis y reconocimiento de voz): descartada por confiabilidad y simplicidad; la anamnesis la conduce y registra la especialista.	7**](#heading)

[**● Clasificación diagnóstica completa de la afección por imagen: la red neuronal se limita a extraer rasgos observables, no a emitir el diagnóstico.	7**](#heading)

[**● Habilitación regulatoria o uso clínico en producción: el proyecto es un prototipo funcional de validación.	7**](#heading)

[**● Cobertura dermatológica exhaustiva: se limita al conjunto de cuadros de la base de conocimiento.	7**](#heading)

[**● Realizar la planificación, el seguimiento del cronograma y el control de riesgos con metodología ágil o híbrida.	7**](#heading)

[**● Elaborar el análisis de viabilidad técnica, organizacional y económica.	7**](#heading)

[**● Identificar los ODS relacionados y definir objetivos de responsabilidad social.	7**](#heading)

[**● Redactar el paper académico y el póster bajo formato de congreso.	7**](#redactar-el-paper-académico-y-el-póster-bajo-formato-de-congreso.)

[**Objetivos	8**](#objetivos)

[Objetivo General	8](#objetivo-general)

[Objetivos Específicos	8](#objetivos-específicos)

[**Antecedentes Académicos	9**](#antecedentes-académicos)

[**Arquitectura Preliminar	10**](#arquitectura-preliminar)

[**Tecnologías y Modelos de Inteligencia Artificial Propuestos	12**](#tecnologías-y-modelos-de-inteligencia-artificial-propuestos)

[Modelo de Visión	12](#modelo-de-visión)

[Capa de Preprocesamiento e Integración	12](#capa-de-preprocesamiento-e-integración)

[Motor Experto Híbrido	13](#motor-experto-híbrido)

[Servicios Cognitivos de Voz	13](#servicios-cognitivos-de-voz)

[Decisiones de Diseño de la Capa de Visión	14](#decisiones-de-diseño-de-la-capa-de-visión)

[Matriz de Riesgos	18](#matriz-de-riesgos)

[Plan de Contingencia	20](#plan-de-contingencia)

[Métricas de Seguimiento	21](#métricas-de-seguimiento)

[Viabilidad Inicial	22](#viabilidad-inicial)

[Objetivos de Desarrollo Sostenible (ODS)	22](#objetivos-de-desarrollo-sostenible-\(ods\))

[Objetivos de Responsabilidad Social	23](#objetivos-de-responsabilidad-social)

[Hitos de Control	24](#hitos-de-control)

[**Estimaciones y Análisis Económico	25**](#estimaciones-y-análisis-económico)

[Premisas	25](#premisas)

[Estimación de horas hombre	25](#estimación-de-horas-hombre)

[Estimación simplificada del tamaño: Puntos de Función frente a COCOMO	26](#estimación-simplificada-del-tamaño:-puntos-de-función-frente-a-cocomo)

[Conteo simplificado de Puntos de Función (UFP)	27](#conteo-simplificado-de-puntos-de-función-\(ufp\))

[Costos de hardware	28](#costos-de-hardware)

[Costos cloud	28](#costos-cloud)

[Costos operativos	29](#costos-operativos)

[Estimación de costos recurrentes anuales para el escenario de producción	29](#estimación-de-costos-recurrentes-anuales-para-el-escenario-de-producción)

[Análisis costo-beneficio	30](#análisis-costo-beneficio)

[VAN, TIR y Tiempo de Recupero	30](#van,-tir-y-tiempo-de-recupero)

[Escenario pesimista	31](#escenario-pesimista)

[Comparación de escenarios	32](#comparación-de-escenarios)

[Etapa 2 — Avance de Ejecución	34](#etapa-2-—-avance-de-ejecución)

[Avance funcional del sistema	34](#avance-funcional-del-sistema)

[Integración inicial del robot	34](#integración-inicial-del-robot)

[Pruebas preliminares del componente inteligente	35](#pruebas-preliminares-del-componente-inteligente)

[Evidencias de inferencia	36](#evidencias-de-inferencia)

[Integración inicial con servicios cloud	36](#integración-inicial-con-servicios-cloud)

[Configuración básica de infraestructura y monitoreo	37](#configuración-básica-de-infraestructura-y-monitoreo)

[Avance del paper académico	38](#avance-del-paper-académico)

[Seguimiento y control del proyecto	38](#seguimiento-y-control-del-proyecto)

[Gestión de riesgos	39](#gestión-de-riesgos)

[Métricas e indicadores	40](#métricas-e-indicadores)

[Retrospectiva parcial	41](#retrospectiva-parcial)

[Responsabilidad social en la definición y justificación del caso	41](#responsabilidad-social-en-la-definición-y-justificación-del-caso)

[**Anexo	43**](#anexo)

[**Referencias	44**](#referencias)

# **Resumen del Problema** {#resumen-del-problema}

El interrogatorio clínico en dermatología opera sistemáticamente sobre información imprecisa: el paciente confunde tiempos, subestima la antigüedad de las lesiones y carece de vocabulario morfológico, lo que obliga al especialista a filtrar y corregir cada dato antes de razonar sobre él. A esto se suma la disponibilidad limitada de dermatólogos, especialmente en el primer nivel de atención y en regiones con baja densidad de especialistas, donde el médico generalista debe resolver consultas cutáneas sin soporte experto. El diagnóstico diferencial entre cuadros de presentación similar (por ejemplo eccema y psoriasis) requiere tiempo y pericia que no siempre están disponibles, y un error o demora puede derivar en la cronificación o complicación del cuadro.  
Existe, por lo tanto, la necesidad de una herramienta que sistematice el razonamiento heurístico del especialista, organice el interrogatorio clínico, ofrezca un diagnóstico diferencial fundamentado y deje trazabilidad del razonamiento, sin reemplazar el criterio médico.

# **Descripción general del Sistema Inteligente** {#descripción-general-del-sistema-inteligente}

El comportamiento inteligente se sustenta en un motor de inferencias híbrido que combina tres capas de razonamiento: reglas deterministas de encadenamiento hacia adelante para síntomas unívocos, factores de certeza para variables contextuales como el estrés (Shortliffe & Buchanan, 1975\) y lógica difusa con defuzzificación por centroide para variables subjetivas como el nivel de prurito (Zadeh, 1965; Klir & Yuan, 1995).  
RAPIRO aporta la capa de interacción y visión principalmente: conduce el interrogatorio clínico enunciando las preguntas en voz alta, solicita al paciente que acerque la zona afectada a su cámara para capturar la imagen de la lesión, y exhibe un comportamiento observable durante la consulta. Un rasgo central del diseño es la doble entrada de datos por variable: el sistema registra lo que reporta el paciente y lo que evalúa clínicamente el especialista, que puede corregir el dato autorreportado (por ejemplo, la antigüedad o el nivel de prurito) antes de la inferencia, de modo que el motor razona con los valores clínicos y no con los relatados por el paciente. Esto replica una heurística clínica documentada en la entrevista de elicitación (Alarcón, 2026).  
La orientación diagnóstica resultante se entrega al especialista, no al paciente, presentándole así segundas y terceras posibles interpretaciones de diagnóstico, ayudando a considerar abarcativamente todas las opciones de tratamiento y contribuyendo a mejorar su servicio para con el paciente.

# 

# **Comportamiento Esperado** {#comportamiento-esperado}

El flujo observable de una consulta asistida por SEADD es el siguiente:

* Inicio: el paciente se ubica frente a RAPIRO. El robot saluda y explica brevemente que asistirá en la consulta.  
* Interrogatorio por voz: RAPIRO pregunta de forma estructurada por localización, morfología, antigüedad y factores contextuales (por ejemplo estrés).  
* Captura de imagen: el robot solicita al paciente que acerque la lesión a su cámara y captura una o varias imágenes de la zona afectada.  
* Doble entrada y corrección clínica: el especialista revisa, a través de una interfaz web, los valores registrados y corrige los que su observación clínica contradiga (la imagen capturada queda disponible como apoyo visual).  
* Inferencia: el motor experto híbrido procesa los valores clínicos y produce el diagnóstico principal con nivel de certeza y porcentaje de severidad difusa, los diagnósticos alternativos (segundo y tercero más probables) con las reglas que los sustentan, el estado del cuadro (agudo o crónico) y una sugerencia terapéutica.  
* Entrega y trazabilidad: la orientación se muestra al especialista junto con la cadena de razonamiento (reglas disparadas) como justificación auditable. El resultado no se lee al paciente.

La evidencia de comportamiento inteligente que se mostrará en la defensa incluye la cadena de razonamiento explícita, el diagnóstico diferencial con su nivel de certeza, y casos de prueba donde el sistema réplica el criterio de la experta.

# 

# **Alcance del Proyecto** {#alcance-del-proyecto}

## **Incluido en el alcance** {#heading}

* Implementación del motor experto híbrido (reglas con encadenamiento hacia adelante, factores de certeza y lógica difusa) con su base de conocimiento validada con la experta.  
* Capa de visión (red neuronal) que extrae dos rasgos observables de la lesión —morfología y color— y alimenta las variables correspondientes del motor, por aprendizaje por transferencia sobre PAD-UFES-20.  
* Integración de RAPIRO como plataforma física de percepción, ubicada junto a la especialista, con cámara webcam USB de buena calidad y módulo de captura asistida (autocaptura por encuadre y cercanía, con disparo manual de respaldo).  
* Interfaz web para el especialista: revisión, doble entrada y corrección de variables (incluido el rasgo propuesto por la visión) y visualización del diagnóstico diferencial y de la cadena de razonamiento.  
* Despliegue del backend en una nube pública, gestionado mediante IaC, con monitoreo de servicios.  
* Documentación de gestión, análisis económico, paper académico y póster.

# **Fuera del alcance:** {#heading}

* # **Diagnóstico definitivo o automatizado: el sistema entrega una orientación de apoyo; la decisión es del especialista.** {#heading}

* # **Acceso del paciente al resultado o autodiagnóstico.** {#heading}

* # **Interacción hablada con el paciente (síntesis y reconocimiento de voz): descartada por confiabilidad y simplicidad; la anamnesis la conduce y registra la especialista.** {#heading}

* # **Clasificación diagnóstica completa de la afección por imagen: la red neuronal se limita a extraer rasgos observables, no a emitir el diagnóstico.** {#heading}

* # **Habilitación regulatoria o uso clínico en producción: el proyecto es un prototipo funcional de validación.** {#heading}

* # **Cobertura dermatológica exhaustiva: se limita al conjunto de cuadros de la base de conocimiento.** {#heading}

* # **Realizar la planificación, el seguimiento del cronograma y el control de riesgos con metodología ágil o híbrida.** {#heading}

* # **Elaborar el análisis de viabilidad técnica, organizacional y económica.** {#heading}

* # **Identificar los ODS relacionados y definir objetivos de responsabilidad social.** {#heading}

* # **Redactar el paper académico y el póster bajo formato de congreso.** {#redactar-el-paper-académico-y-el-póster-bajo-formato-de-congreso.}

#  {#heading}

# **Objetivos** {#objetivos}

## **Objetivo General** {#objetivo-general}

 Diseñar, implementar y gestionar un sistema inteligente de apoyo al pre-diagnóstico dermatológico utilizando RAPIRO como plataforma física, capaz de conducir un interrogatorio clínico estructurado por voz, capturar la imagen de la lesión, inferir una orientación diagnóstica diferencial mediante un motor experto híbrido y entregarla al especialista con su cadena de razonamiento, apoyado en infraestructura cloud, con el fin de aumentar la consistencia diagnóstica y reducir la carga cognitiva del especialista.

## **Objetivos Específicos** {#objetivos-específicos}

* Implementar el motor de inferencias híbrido (reglas, factores de certeza y lógica difusa) y su base de conocimiento, validada con la experta.  
* Dotar a RAPIRO de servicios cognitivos para conducir el interrogatorio (realizar preguntas).  
* Integrar la captura de imagen de la lesión como apoyo visual para el especialista.  
* Desarrollar la interfaz web del especialista con la doble entrada de datos y la visualización de la cadena de razonamiento.  
* Desplegar el backend en una nube pública mediante IaC para garantizar la replicabilidad del entorno.  
* Configurar monitoreo cloud de disponibilidad, tiempos de respuesta y desempeño del sistema.

# 

# **Antecedentes Académicos** {#antecedentes-académicos}

Los sistemas expertos de apoyo al diagnóstico médico tienen una tradición consolidada. El antecedente central que se analiza es el trabajo de Shortliffe y Buchanan (1975), que introdujo el modelo de razonamiento inexacto mediante factores de certeza en el contexto del sistema MYCIN para el diagnóstico de infecciones. Ese modelo es precisamente el que SEADD adopta para manejar variables contextuales cuya contribución al diagnóstico no es categórica. La lección que se toma de ese trabajo es la viabilidad de representar el razonamiento clínico bajo incertidumbre de forma trazable y explicable, sin requerir grandes volúmenes de datos.  
Como complemento teórico, la lógica difusa (Zadeh, 1965; Klir & Yuan, 1995\) fundamenta el tratamiento de variables subjetivas como el prurito, permitiendo convertir una apreciación gradual ("cuánto pica del 1 al 10") en una salida interpretable mediante defuzzificación por centroide. El encuadre del sistema como herramienta de apoyo que no reemplaza al médico se alinea con la noción de inteligencia artificial responsable orientada al bienestar humano (Russell & Norvig, 2022).  
Como aplicación actual del tipo de sistema, los sistemas de apoyo a la decisión clínica y los asistentes basados en conocimiento se utilizan hoy para estandarizar diagnósticos diferenciales y reducir la variabilidad entre profesionales, especialmente en contextos de recursos limitados.

# **Arquitectura Preliminar** {#arquitectura-preliminar}

La arquitectura es híbrida edge-cloud. El robot maneja la interacción y la captura en el borde; la nube aloja el motor de inferencia, la base de conocimiento, los servicios cognitivos de voz, la persistencia y el monitoreo.  
Capa de borde (RAPIRO \+ Raspberry Pi \+ webcam USB y parlante):

* Conducción del interrogatorio por voz (reproducción de preguntas y captura de respuestas).  
* Captura de la imagen de la lesión.  
* Orquestación local de la consulta y acceso a la interfaz web del especialista.  
* Comportamiento observable del robot (voz, LEDs, orientación).

Capa de nube (AWS):

* Servicio de inferencia del motor experto (expuesto como API).  
* Base de conocimiento y reglas.  
* Servicios cognitivos de voz (texto a voz y voz a texto) y, opcionalmente, comprensión del lenguaje para interpretar respuestas.  
* Persistencia de consultas y de imágenes de lesiones (con consentimiento).  
* Monitoreo y observabilidad.  
* Aprovisionamiento mediante IaC.

Interfaz del especialista:

* Aplicación web para la doble entrada (corrección de variables), la visualización del diagnóstico diferencial con niveles de certeza y severidad, y la cadena de razonamiento auditable.

La figura 1 resume el flujo de datos de la arquitectura: RAPIRO conduce el interrogatorio por voz, el dermatologo toma las notas, captura la imagen, el servicio de inferencia procesa los valores clínicos y devuelve la orientación con su cadena de razonamiento al especialista.  
![][image1]  
Fig 1\.

# **Tecnologías y Modelos de Inteligencia Artificial Propuestos** {#tecnologías-y-modelos-de-inteligencia-artificial-propuestos}

El sistema combina dos técnicas de inteligencia artificial que operan en cascada: un modelo de visión por computadora que percibe e infiere atributos clínicos a partir de la imagen de la lesión, y el motor experto híbrido, que razona sobre esos atributos para producir la orientación diagnóstica.

## **Modelo de Visión** {#modelo-de-visión}

Se propone una red neuronal convolucional para la inferencia de atributos morfológicos observables de la lesión a partir de la imagen capturada por RAPIRO. Este modelo no emite el diagnóstico: infiere los valores de las variables que el motor experto consume (principalmente morfología y coloración predominante, y de ser viable, una orientación de la localización). De este modo, la red cumple el rol de percepción y el motor experto conserva el rol de razonamiento y decisión, evitando que ambos componentes se superpongan y se omita el uso de la base de conocimiento experto. Para la implementación se prevé aprovechar una arquitectura pre entrenada mediante aprendizaje por transferencia (por ejemplo, de la familia ResNet o MobileNet), ajustada a las categorías de atributos del sistema. Como insumo de entrenamiento se contemplan datasets públicos de dermatología (HAM10000, ISIC) y se evaluará el uso de un conjunto propio de imágenes etiquetadas según los atributos del modelo experto.

## 

## **Capa de Preprocesamiento e Integración** {#capa-de-preprocesamiento-e-integración}

 Entre el modelo de visión y el motor experto se incorpora una capa de preprocesamiento que adapta y normaliza la salida de la red al formato de entrada del sistema experto. Su función es mapear las predicciones de atributos (por ejemplo, morfología igual a escama, color igual a blanco nacarado) a las variables y los valores admitidos por la base de conocimiento, y acompañarlas de su grado de confianza. Las variables que el modelo de visión no puede observar (como antigüedad de la lesión y presencia de estrés previo) las registra el especialista. El alcance del modelo podrá acotarse a la morfología según la disponibilidad de datos etiquetados (ver matriz de riesgos, R16)

## 

## **Motor Experto Híbrido** {#motor-experto-híbrido}

El componente de IA central por la vía de la inferencia. Combina reglas con encadenamiento hacia adelante para síntomas unívocos, factores de certeza para variables contextuales como el estrés (Shortliffe & Buchanan, 1975\) y lógica difusa con defuzzificación por centroide para variables subjetivas como la intensidad de la picazón (Zadeh, 1965; Klir & Yuan, 1995). Produce el diagnóstico principal con su nivel de certeza, los diagnósticos alternativos, el estado del cuadro y una cadena de razonamiento explícita.

## 

## **Servicios Cognitivos de Voz** {#servicios-cognitivos-de-voz}

Síntesis de voz (texto a voz) con el fin de que RAPIRO conduzca la interacción enunciando el interrogatorio, que puede resultar repetitivo para el profesional de la salud, y guiando al paciente durante la captura de la imagen.

### **Decisiones de Diseño de la Capa de Visión** {#decisiones-de-diseño-de-la-capa-de-visión}

La capa neuronal del sistema se definió como un extractor de rasgos observables y no como un clasificador de diagnóstico. La red no emite una afección dermatológica, sino que infiere dos variables descriptivas de la lesión —morfología y color— que se incorporan como entradas adicionales al motor de inferencia simbólico. Esta subordinación es deliberada: mantiene el razonamiento diagnóstico en el componente experto, que es explicable y auditable, y reserva para la red únicamente la tarea perceptiva en la que aporta valor.  
Se decidió que la red prediga dos variables independientes mediante una arquitectura de doble cabeza sobre un backbone compartido: una imagen de entrada produce dos salidas categóricas simultáneas. La variable morfología contempla cinco categorías (mácula, pápula, ampolla, escama y engrosamiento) y la variable color, cuatro (amarillento, blanco nacarado, rosado y rojo). Estas categorías no son arbitrarias: replican exactamente la taxonomía que utiliza la base de conocimiento del motor experto, de modo que la salida de la red es directamente consumible por las reglas sin necesidad de capas de traducción intermedias.  
Se asumió explícitamente que la red no necesita ser perfecta. El sistema incorpora un esquema de doble entrada en el que la profesional médica revisa y corrige tanto los datos aportados por el paciente como los rasgos propuestos por la red antes de que el motor ejecute la inferencia. Esta supervisión humana contiene el margen de error del componente neuronal y evita que una predicción incorrecta se propague a la orientación diagnóstica. En consecuencia, el criterio de desarrollo priorizó la corrección metodológica y la evaluación honesta del modelo por sobre la maximización de la exactitud a cualquier costo.  
Como fuente de imágenes se adoptó el conjunto de datos PAD-UFES-20, compuesto por imágenes clínicas capturadas con teléfonos móviles, por su correspondencia con las condiciones reales de captura mediante la cámara del robot, en contraposición a los conjuntos dermatoscópicos que no representan ese escenario. Ahora bien, se identificó una restricción determinante: PAD-UFES-20 está etiquetado por diagnóstico y metadatos del paciente, y no por morfología ni color. Por lo tanto, sus etiquetas originales no son utilizables para esta tarea. Se decidió, en consecuencia \-considerando que aún con esta limitación fue el mejor dataset hallado para la tarea propuesta-, etiquetar manualmente un subconjunto de sus imágenes conforme a las dos taxonomías propias del sistema, asumiendo el costo de ese trabajo manual a cambio de garantizar la correspondencia exacta entre lo que la red predice y lo que las reglas esperan. El pipeline de entrenamiento se diseñó para regirse íntegramente por un archivo de etiquetas propio y no por las etiquetas originales del dataset.ROLES DEL EQUIPO

Equipo de 2 integrantes; ambos programan, por lo que los roles indican responsabilidad principal, no exclusividad.

* Integrante A \- Líder Técnico: motor experto y base de conocimiento, integración de voz e imagen, integración física con RAPIRO.  
* Integrante B \- Líder de Proyecto: planificación y seguimiento, infraestructura cloud e IaC, interfaz web del especialista, monitoreo y documentación (paper y póster).  
* Compartido: arquitectura, validación con la experta, pruebas, preparación de la defensa, con revisión cruzada de código y documentación.  
   (Completar con los nombres reales de cada integrante.)  
11. METODOLOGÍA DE TRABAJO

Metodología híbrida ágil, apropiada para un equipo reducido y plazo corto: marco iterativo de Scrum (Schwaber & Sutherland, 2020\) con tablero Kanban para visualizar el flujo. Sprints semanales, puntos de control diarios entre los dos integrantes, revisión y retrospectiva al cierre de cada sprint, y definición de "terminado" por tarea (código funcionando, probado y documentado). Se opta por híbrida y no Scrum puro por el tamaño del equipo y el horizonte de tres semanas.

12. CRONOGRAMA (GANTT)

Ventana de trabajo: 1 al 19 de junio de 2026\. A \= Líder Técnico, B \= Líder de Proyecto.

Sprint 0 \- Cierre de Etapa 1 y aprobación del enfoque (1 al 3 de junio):

* Consolidar documento de Etapa 1 (B) \- 1 a 2 jun  
* Readaptar la base de conocimiento de SEADD al nuevo encuadre (A) \- 1 a 2 jun  
* Setup del entorno (Raspberry Pi, Python, motor experto) (A) \- 1 a 2 jun  
* Demo mínima de voz (pregunta por voz) (A) \- 2 a 3 jun  
* Presentación del enfoque a los docentes (A+B) \- 3 jun

Sprint 1 \- Núcleo experto y base cloud (4 al 10 de junio):

* Portar e implementar el motor híbrido (reglas, certeza, difusa) (A) \- 4 a 8 jun  
* Flujo de diálogo del interrogatorio por voz (A) \- 6 a 9 jun  
* Módulo de captura de imagen (A) \- 8 a 10 jun  
* Base AWS con Terraform (Lambda, DynamoDB, S3) (B) \- 4 a 8 jun  
* Integración de servicios de voz (Polly, Transcribe) (B) \- 8 a 10 jun

Sprint 2 \- Integración (11 al 14 de junio):

* Interfaz web del especialista con doble entrada (B) \- 11 a 13 jun  
* Integración de extremo a extremo sobre RAPIRO (A+B) \- 12 a 14 jun  
* Monitoreo en CloudWatch (B) \- 13 a 14 jun  
* Cadena de razonamiento visible en la salida (A) \- 13 a 14 jun

Sprint 3 \- Pruebas y entrega final (15 al 19 de junio):

* Pruebas con casos clínicos y medición de métricas (A+B) \- 15 a 16 jun  
* Ajuste de reglas y rangos difusos (Kaizen) (A) \- 15 a 17 jun  
* Paper académico (B) \- 15 a 18 jun  
* Póster académico (B) \- 16 a 18 jun  
* Preparación de la defensa y demo (A+B) \- 18 jun

## **Matriz de Riesgos** {#matriz-de-riesgos}

Escala: probabilidad (Baja/Media/Alta), impacto (Bajo/Medio/Alto), nivel resultante y estado.

* R01 — Cambio de tema del proyecto. Gestión/Alcance. Alta / Alto / Crítico. Estado: materializado (dos veces: primero desde una propuesta de RAPIRO como sistema de aviso temprano de inundaciones, luego desde el proyecto de asistencia a adultos mayores, hasta el sistema dermatológico actual). Mitigación: reutilización máxima del trabajo existente, acotamiento al mínimo defendible y repriorización por hitos.  
* R02 — Baja disponibilidad de RAPIRO y de la Raspberry Pi asignada. Recursos/Hardware. Alta / Medio / Alto. Estado: vigente / parcialmente materializado (RAPIRO prestado; la Raspberry Pi original tiene acceso limitado). Mitigación: uso de la Raspberry Pi 5 personal, disponible de forma permanente, reservando RAPIRO para integración y demo.  
* R03 — Recursos de cómputo limitados de la Raspberry Pi. Técnico/Hardware. Media / Medio / Medio. Estado: latente. Mitigación: descarga de procesamiento a la nube, reducción de carga y uso de la Raspberry Pi 5\.  
* R04 — Desorganización y descoordinación entre integrantes. Equipo/Gestión. Alta / Alto / Crítico. Estado: materializado. Mitigación: tablero de tareas, puntos de control frecuentes, reparto explícito de responsabilidades y repositorio y documentos compartidos como fuente única.  
* R05 — Baja disponibilidad horaria de los integrantes. Equipo/Recursos. Alta / Alto / Crítico. Estado: materializado. Mitigación: concentración del esfuerzo en el núcleo demostrable, recorte de funcionalidad no esencial y trabajo asíncrono coordinado por repositorio y documentos.  
* R06 — Mala gestión del tiempo. Gestión. Alta / Alto / Crítico. Estado: materializado (agravado por los cambios de tema). Mitigación: priorización por mínimo viable, hitos cortos y avances honestos (lo hecho como hecho, lo pendiente como diseñado).  
* R07 — Pérdida de datos del proyecto (informe y recursos no versionados). Técnico/Información. Media / Alto / Alto. Estado: latente (el código está en GitHub, pero el informe y otros recursos solo en Google Drive). Mitigación: versionado en GitHub y Drive; respaldo periódico adicional fuera de Drive.  
* R08 — Acceso intermitente a RAPIRO para integración física. Recursos/Hardware. Alta / Medio / Alto. Estado: vigente (foco en la ventana de integración final, distinto de R02). Mitigación: desarrollar y probar todo el flujo sobre la Raspberry Pi 5, dejando para las ventanas de acceso solo el ajuste de servos, LEDs y la demo integrada.  
* R09 — Calidad de cámara insuficiente para una imagen clínica útil. Técnico/Hardware. Media / Medio / Medio. Estado: latente (la docente puso como condición una cámara de buena calidad). Mitigación: webcam USB de buena calidad, control de iluminación y distancia de captura.  
* R10 — Alcance excesivo frente al tiempo disponible. Gestión/Alcance. Alta / Alto / Crítico. Estado: materializado y en gestión activa. Mitigación: proceso de reducción de alcance, migración de cloud serverless a una VM más simple, y acotamiento de la visión a la extracción de rasgos.  
* R11 — Sobreesfuerzo de integración técnica (cloud, IaC, monitoreo). Técnico. Media / Alto / Alto. Estado: latente (es el conjunto de mayor riesgo de integración). Mitigación: simplificación a una VM en nube pública con reverse proxy y firewall, IaC mínima por código y monitoreo básico (logs más métricas del sistema).  
* R12 — Indefinición de requisitos por parte de la cátedra. Externo/Requisitos. Media / Alto / Alto. Estado: vigente (interpretación de qué significa "analizar la imagen"). Mitigación: consulta explícita a la docente antes de comprometer trabajo de visión.  
* R13 — Reincorporación de funcionalidad descartada (reconocimiento de voz). Técnico/Alcance. Media / Medio / Medio. Estado: latente. Mitigación: mantener el robot sin entrada de voz; de requerirse, respuestas guiadas o registro por el especialista.  
* R14 — Dependencia de conocimiento experto externo (validación clínica). Externo/Conocimiento. Media / Medio / Medio. Estado: latente. Mitigación: usar los casos de prueba ya validados y agendar tempranamente cualquier nueva validación.  
* R15 — Dependencia crítica de un integrante en equipo reducido. Equipo. Baja / Alto / Medio. Estado: latente. Mitigación: documentación compartida, código versionado y revisión cruzada para que ninguno sea punto único de falla.  
* R16 — Etiquetado insuficiente para entrenar el modelo de visión en morfología y color. Técnico/Datos. Media / Alto / Alto. Estado: latente. Los datasets públicos (HAM10000, ISIC, PAD-UFES-20) vienen etiquetados por enfermedad y no por estos atributos, lo que obliga a etiquetar a mano un subconjunto según las categorías del sistema y puede exceder el tiempo disponible. Mitigación: ante etiquetado o desempeño insuficiente, reducir el alcance de la visión a un solo atributo (la morfología), dejando el color como entrada manual del especialista vía la doble entrada; esto baja a la mitad la necesidad de etiquetado sin romper la arquitectura.

## **Plan de Contingencia** {#plan-de-contingencia}

* Ante R02 u R08 (sin RAPIRO o acceso breve): demostrar el sistema completo sobre la Raspberry Pi 5 con webcam; mostrar la integración con RAPIRO como evidencia parcial si el acceso es breve.  
* Ante R03, R06 o R10 (cómputo o plazo): el motor experto, la doble entrada y la entrega de la orientación son lo no negociable; la red de visión se recorta primero a un solo atributo y la autocaptura a captura manual.  
* Ante R09 (cámara): acotar la demo a casos con buena captura y documentar la calidad de cámara como limitación.  
* Ante R11 (integración cloud): mantener la VM mínima con monitoreo básico; de ser necesario, ejecutar la inferencia en local simulando el servicio para la demo.  
* Ante R16 (etiquetado): aplicar la mitigación de un solo atributo (morfología por la red, color por entrada manual).

### **Métricas de Seguimiento** {#métricas-de-seguimiento}

Métricas técnicas y de calidad (heredadas y adaptadas de SEADD):

* Tasa de acierto del diagnóstico principal respecto del criterio de la experta (valor base 85,7 %, meta Kaizen ≥ 90 %).  
* Tiempo de inferencia desde el último dato hasta el diagnóstico diferencial (base \< 2 s en local, meta \< 1 s sobre la VM).  
* Porcentaje de casos "no determinado" por datos insuficientes (base 14,3 %, meta ≤ 5 %).  
* Exactitud del extractor de la red de visión, desagregada por variable (morfología y color) y por clase, con evaluación por subgrupo de tono de piel cuando sea posible.  
* Tasa de capturas útiles (bien encuadradas y enfocadas) del módulo de captura.

Métricas de gestión:

* Porcentaje de tareas completadas (planificado frente a real).  
* Desviación respecto de los hitos.  
* Velocidad por sprint.

Métricas operativas y cloud:

* Disponibilidad del servicio y latencia de la inferencia.  
* Costo acumulado de la nube frente al presupuesto.

La mejora se gestiona con ciclos Kaizen: identificar la causa raíz de cada error de clasificación, ajustar reglas, rangos difusos o el umbral de la red, y re-ejecutar los casos de prueba hasta alcanzar la meta.

### **Viabilidad Inicial** {#viabilidad-inicial}

* Técnica: alta para el motor experto, ya desarrollado y validado en el TP previo de SEADD, sin entrenamiento ni grandes volúmenes de datos. La red de visión introduce el principal riesgo técnico, acotado al limitarla a dos rasgos, entrenarla en GPU local, servirla en CPU y mantener la entrada manual como respaldo.  
* Económica: alta. Hardware principal prestado o propio, GPU de entrenamiento propia y nube cubierta con créditos y capa gratuita durante el desarrollo; el detalle se desarrolla en el análisis económico.  
* Temporal: ajustada y sensible al compromiso de la red de visión; alcanzable por la reutilización del trabajo existente, el alcance acotado y la priorización por hitos.  
* Operativa: media-alta. Condicionada por el acceso al robot y la calidad de la cámara, ambos mitigados.

### **Objetivos de Desarrollo Sostenible (ODS)** {#objetivos-de-desarrollo-sostenible-(ods)}

* ODS 3 — Salud y bienestar: acerca orientación diagnóstica especializada a contextos con escasa disponibilidad de dermatólogos, reduce el tiempo diagnóstico y favorece la detección temprana.  
* ODS 9 — Industria, innovación e infraestructura: aplica inteligencia artificial híbrida a un problema de salud real, desplegable en contextos de recursos limitados mediante una arquitectura accesible.

### **Objetivos de Responsabilidad Social** {#objetivos-de-responsabilidad-social}

Mejora del bienestar de la comunidad:

* Aumentar la consistencia y la fundamentación del diagnóstico diferencial, especialmente en el primer nivel de atención.  
* Reducir la variabilidad entre profesionales y dejar trazabilidad auditable del razonamiento.

Reducción de impactos negativos:

* Posicionar el sistema como apoyo y no como reemplazo del médico; la salida es una orientación, no un diagnóstico definitivo.  
* Restringir el resultado al especialista para evitar el autodiagnóstico y la ansiedad del paciente.  
* Trazabilidad y atribución del conocimiento incorporado (cita a la experta).  
* Minimización y consentimiento en el tratamiento de imágenes y datos clínicos.  
* Transparencia sobre los límites del sistema y sobre la ausencia de habilitación regulatoria.

## 

## **Hitos de Control** {#hitos-de-control}

* H0 (3 jun): enfoque aprobado por los docentes. Entregable: Etapa 1 completa más demo mínima de voz.  
* H1 (8 jun): motor experto ejecutando inferencia sobre casos de prueba.  
* H2 (10 jun): voz, captura de imagen y base cloud operativas.  
* H3 (13 jun): interfaz del especialista con doble entrada funcionando.  
* H4 (14 jun): integración de extremo a extremo sobre RAPIRO, con monitoreo.  
* H5 (16 jun): sistema probado y métricas medidas.  
* H6 (15 al 19 jun): entrega y defensa final (paper, póster, demo en vivo).

# **Estimaciones y Análisis Económico** {#estimaciones-y-análisis-económico}

## **Premisas** {#premisas}

El análisis se expresa en dólares estadounidenses (USD) por dos motivos: el modelo de comercialización del sistema ya está definido en esa moneda y trabajar en USD evita que la proyección plurianual quede distorsionada por la inflación local; la conversión a moneda local debe hacerse con la cotización vigente a la fecha de presentación. El costo de la mano de obra se imputa a un valor de referencia de USD 10 por hora, correspondiente a un perfil junior de Ingeniería en Sistemas, que debe ajustarse al criterio de la cátedra. Las cifras son estimaciones sujetas a los supuestos declarados.

## **Estimación de horas hombre** {#estimación-de-horas-hombre}

La estimación se construye por paquetes de trabajo, alineados con el cronograma del proyecto. El equipo está compuesto por dos integrantes (A, Líder Técnico; B, Líder de Proyecto) que trabajan en paralelo durante la ventana del 1 al 19 de junio.

| Paquete de trabajo | Resp. | Horas |
| :---- | :---- | :---- |
| Readaptación del motor experto y base de conocimiento (reúso) | A | 18 |
| Guía de etiquetado y validación con la experta | A+B | 12 |
| Etiquetado manual del subconjunto de imágenes | A+B | 28 |
| Pipeline y entrenamiento de la red de visión | A | 22 |
| Servicio de inferencia de visión (CPU) | A | 10 |
| Módulo de captura (manual \+ autocaptura) | A | 14 |
| Infraestructura cloud e IaC (Terraform) | B | 24 |
| Servicio de inferencia del motor (API) | B | 12 |
| Interfaz web del especialista (doble entrada) | B | 26 |
| Monitoreo y observabilidad | B | 8 |
| Integración extremo a extremo sobre RAPIRO | A+B | 18 |
| Pruebas, métricas y ajuste Kaizen | A+B | 16 |
| Documentación de gestión (Etapa 1 \+ informe de ejecución) | B | 20 |
| Paper académico | B | 16 |
| Póster | B | 8 |
| Gestión, coordinación y reuniones | A+B | 12 |
| Total |  | 264 |

El esfuerzo total estimado es de 264 horas hombre, repartidas de forma aproximadamente equitativa entre los dos integrantes. A la tarifa de referencia, el costo de mano de obra asciende a USD 2.640 (264 h × USD 10). Conviene destacar que esta cifra ya está contenida por la reutilización de SEADD: aproximadamente la mitad de la funcionalidad (motor experto y base de conocimiento) proviene del trabajo previo y no se vuelve a desarrollar, lo que se cuantifica en el apartado siguiente.

## **Estimación simplificada del tamaño: Puntos de Función frente a COCOMO** {#estimación-simplificada-del-tamaño:-puntos-de-función-frente-a-cocomo}

Se recomienda utilizar Puntos de Función (PF) y no COCOMO. La razón es metodológica: COCOMO básico estima el esfuerzo a partir de líneas de código (KLOC), una magnitud que en esta etapa temprana es poco confiable, que asume desarrollo desde cero y cuyas constantes están calibradas para proyectos de mayor porte; además no modela bien la reutilización, que aquí es central. Los Puntos de Función, en cambio, se derivan de los requisitos funcionales \-ya disponibles, son independientes del lenguaje, se adaptan mejor a un proyecto pequeño y dominado por la integración, y mantienen continuidad con el trabajo previo de SEADD, que ya empleó puntos de función.

## **Conteo simplificado de Puntos de Función (UFP)** {#conteo-simplificado-de-puntos-de-función-(ufp)}

| Tipo | Función | Complejidad | PF |
| :---- | :---- | :---- | :---- |
| EE (Entrada) | Registro de variables clínicas | Media | 4 |
| EE (Entrada) | Doble entrada / corrección de variables | Media | 4 |
| EE (Entrada) | Carga y captura de imagen | Media | 4 |
| SE (Salida) | Diagnóstico diferencial con certeza y severidad | Alta | 7 |
| SE (Salida) | Cadena de razonamiento (reglas disparadas) | Media | 5 |
| CE (Consulta) | Inferencia de rasgo por la red de visión | Media | 4 |
| CE (Consulta) | Visualización de imagen de apoyo | Baja | 3 |
| ALI (Lógico interno) | Base de conocimiento y reglas | Alta | 15 |
| ALI (Lógico interno) | Registro de consultas | Media | 10 |
| AIE (Interfaz externa) | Modelo de visión / dataset externo | Media | 7 |
| Total UFP |  |  | 63 |

Con un factor de ajuste neutro, el tamaño se estima en 63 Puntos de Función. A una productividad de referencia de mercado para desarrollo desde cero (del orden de 8 h/PF) el esfuerzo proyectado sería de unas 500 horas; sin embargo, dado el fuerte reúso (la base de conocimiento y el motor —los componentes ALI de mayor peso— ya están construidos) y el uso de frameworks y servicios gestionados, la productividad efectiva del trabajo nuevo se aproxima a 4 h/PF, lo que arroja unas 250 horas, consistente con las 264 horas estimadas de forma ascendente. La diferencia entre ambos números (≈ 500 h teóricas frente a ≈ 264 h reales) cuantifica el ahorro atribuible a la reutilización.

## **Costos de hardware** {#costos-de-hardware}

El costo de hardware incremental del proyecto es nulo (USD 0). Todo el equipamiento utilizado ya era propiedad del equipo o es prestado, y no se adquirió nada nuevo:

| Activo | Origen | Costo para el proyecto |
| :---- | :---- | :---- |
| Robot RAPIRO | Prestado | USD 0 |
| Raspberry Pi | Propia | USD 0 |
| GPU NVIDIA 3090 (entrenamiento) | Propia | USD 0 |
| Cámara webcam USB | Propia | USD 0 |
| Estaciones de trabajo del equipo | Propias | USD 0 |

Se aclara que un despliegue comercial real sí requeriría incorporar como costo de capital el robot y la cámara por consultorio, magnitud relevante para el modelo de negocio pero ajena al prototipo, que es el alcance de este trabajo.

## **Costos cloud** {#costos-cloud}

Fase de desarrollo (situación actual): ≈ USD 0\. El proyecto opera bajo el nivel gratuito de AWS. Conviene precisar que AWS modificó este esquema: desde julio de 2025 los nuevos clientes reciben hasta USD 200 en créditos (USD 100 al registrarse y hasta USD 100 adicionales por usar servicios), y el plan gratuito expira a los seis meses o cuando se agotan los créditos, lo que ocurra primero. Las cuentas creadas antes del 15 de julio de 2025 conservan el modelo anterior: 750 horas mensuales de una instancia t3.micro durante 12 meses, suficiente para mantener una instancia encendida de forma continua; en ninguno de los dos planes EC2 es gratuito de forma permanente. En la práctica, como la instancia EC2 con la máquina virtual se apaga cada vez que no se la usa para probar integraciones, el consumo se mantiene dentro de los créditos o de las horas gratuitas, y el costo efectivo de la etapa es nulo.  
Proyección de producción (post-créditos): una vez agotado el nivel gratuito, la instancia persistente sí genera costo. Con precios de referencia de la región us-east-1: una t3.small (2 vCPU, 2 GiB) cuesta unos USD 15,18 mensuales encendida de forma continua, una t3.micro unos USD 7,59 y una t3.medium unos USD 30,37. Sumando almacenamiento, un volumen EBS gp3 de 100 GB ronda los USD 8 a 20 mensuales y la transferencia de salida cuesta USD 0,09 por GB luego de los primeros 100 GB gratuitos mensuales. Para este sistema, que mantiene en memoria el servicio de inferencia, se adopta como base una t3.small a t3.medium más almacenamiento, del orden de USD 25 a 35 mensuales (≈ USD 360 anuales). Si el costo fuera una restricción, una instancia Graviton t4g.nano baja a unos USD 3 mensuales, aunque con menor margen de memoria. Cabe señalar que la decisión de descartar la interacción por voz eliminó los costos por uso de servicios cognitivos (síntesis y reconocimiento de voz) que el diseño anterior habría devengado.

## **Costos operativos** {#costos-operativos}

### ***Estimación de costos recurrentes anuales para el escenario de producción*** {#estimación-de-costos-recurrentes-anuales-para-el-escenario-de-producción}

| Concepto | Costo anual (USD) |
| :---- | :---- |
| Hosting cloud (instancia \+ almacenamiento) | 360 |
| Mantenimiento y soporte (≈ 60 h × USD 10\) | 600 |
| Dominio y certificado | 20 |
| Contingencia operativa | 120 |
| Total operativo anual | 1.100 |

## 

## **Análisis costo-beneficio** {#análisis-costo-beneficio}

La inversión del proyecto (su costo de desarrollo) se compone casi exclusivamente de mano de obra: USD 2.640, con hardware y nube en cero durante el desarrollo. Frente a ello, los beneficios se dividen en dos planos. En el plano académico y social, no monetizado, el sistema aporta mayor consistencia y trazabilidad del diagnóstico diferencial, reducción del tiempo diagnóstico y soporte al primer nivel de atención en regiones con escasez de especialistas. En el plano económico, el modelo de comercialización SaaS prevé USD 30 mensuales por consultorio individual y USD 150 mensuales por institución de hasta 10 usuarios, base sobre la que se construye la proyección financiera siguiente.

## **VAN, TIR y Tiempo de Recupero** {#van,-tir-y-tiempo-de-recupero}

La proyección se construye a tres años, con una tasa de descuento del 15 % anual y supuestos de adopción conservadores y explícitos.  
Supuestos de adopción: Año 1, 5 consultorios; Año 2, 12 consultorios y 1 institución; Año 3, 25 consultorios y 3 instituciones.

| Concepto | Año 0 | Año 1 | Año 2 | Año 3 |
| :---- | :---- | :---- | :---- | :---- |
| Inversión (desarrollo) | −2.640 |  |  |  |
| Ingresos SaaS |  | 1.800 | 6.120 | 14.400 |
| Costos operativos |  | −1.000 | −1.200 | −1.500 |
| Flujo neto | −2.640 | 800 | 4.920 | 12.900 |
| Flujo descontado (15 %) | −2.640 | 696 | 3.720 | 8.481 |

Resultados:

* VAN (15 %) ≈ USD \+10.260. El proyecto crea valor: el valor presente de los flujos supera ampliamente la inversión.  
* TIR ≈ 118 %. Muy por encima de cualquier costo de capital razonable.  
* Tiempo de Recupero ≈ 1,4 años (la inversión se recupera promediando el segundo año).

Lectura honesta de estos números: los indicadores son fuertes en buena parte porque la inversión monetaria es muy baja —la mano de obra es de estudiantes y no se capitaliza a valor de mercado— y porque la curva de adopción es optimista. No deben leerse como una promesa de rentabilidad sino como evidencia de que, bajo supuestos razonables, el modelo es económicamente viable y su punto de equilibrio es temprano. A modo de sensibilidad, si la adopción se redujera a la mitad en los tres años, el VAN se mantiene positivo y el período de recupero se extiende a aproximadamente 2,5 años, lo que indica que la conclusión de viabilidad es robusta frente a escenarios más pesimistas.

## **Escenario pesimista** {#escenario-pesimista}

Para acotar el riesgo del análisis se construye un escenario adverso que tensiona simultáneamente los tres supuestos más sensibles: un sobrecosto de desarrollo del 15 % por desvíos de esfuerzo (304 horas en lugar de 264, es decir USD 3.040 de inversión), una adopción marcadamente más lenta y costos operativos algo mayores por carga de soporte. Se mantiene la tasa de descuento del 15 % para que la comparación con el caso base aísle el efecto de los supuestos operativos.  
Supuestos de adopción pesimistas: Año 1, 2 consultorios; Año 2, 6 consultorios; Año 3, 12 consultorios y 1 institución.

| Concepto | Año 0 | Año 1 | Año 2 | Año 3 |
| :---- | :---- | :---- | :---- | :---- |
| Inversión (con sobrecosto) | −3.040 |  |  |  |
| Ingresos SaaS |  | 720 | 2.160 | 6.120 |
| Costos operativos |  | −1.100 | −1.300 | −1.600 |
| Flujo neto | −3.040 | −380 | 860 | 4.520 |
| Flujo descontado (15 %) | −3.040 | −330 | 650 | 2.972 |

Resultados del escenario pesimista:

* VAN (15 %) ≈ USD \+252. El proyecto apenas crea valor: queda marginalmente por encima del punto de equilibrio.  
* TIR ≈ 18 %. Todavía supera la tasa de descuento del 15 %, aunque por un margen estrecho.  
* Tiempo de Recupero ≈ 2,6 años. La inversión se recupera promediando el tercer año.

Una observación de sensibilidad adicional: este escenario es sensible a la tasa de descuento. Si en lugar del 15 % se aplicará un 20 % —reflejando un mayor riesgo país o un costo de capital más exigente—, el VAN se torna levemente negativo (≈ USD −144), es decir, el proyecto quedaría apenas por debajo del punto de equilibrio en el horizonte de tres años, recuperándose recién hacia el cuarto.

## **Comparación de escenarios** {#comparación-de-escenarios}

| Indicador | Escenario base | Escenario pesimista |
| :---- | :---- | :---- |
| VAN (15 %) | ≈ USD \+10.260 | ≈ USD \+252 |
| TIR | ≈ 118 % | ≈ 18 % |
| Tiempo de Recupero | ≈ 1,4 años | ≈ 2,6 años |

En el escenario base el proyecto es ampliamente rentable, y aún en el escenario pesimista \-con sobrecosto, adopción reducida a menos de la mitad y mayores costos operativos-, el VAN se mantiene positivo y la TIR sigue por encima del costo de capital, con el punto de equilibrio apenas desplazado al tercer año. Esto indica que la viabilidad económica del proyecto es robusta: no depende de un escenario optimista para sostenerse, sino que resiste condiciones claramente adversas antes de comprometerse. El margen estrecho del caso pesimista, no obstante, señala que la rentabilidad real es muy sensible al ritmo de adopción, que sería por lo tanto la variable a vigilar.

## **Etapa 2 — Avance de Ejecución** {#etapa-2-—-avance-de-ejecución}

### **Avance funcional del sistema** {#avance-funcional-del-sistema}

El núcleo del sistema está operativo. Se cuenta con una aplicación funcional del Sistema Experto Dermatológico que implementa un motor de inferencias híbrido que combina reglas deterministas, factores de certeza (Shortliffe & Buchanan, 1975\) y lógica difusa (Zadeh, 1965; Klir & Yuan, 1995), con su subsistema de explicación. La base de conocimiento sistematiza el razonamiento heurístico de la especialista entrevistada (Alarcón, 2026). La interfaz permite cargar las variables clínicas (localización, morfología, coloración, intensidad de picazón, antigüedad y estrés), ejecutar el diagnóstico y visualizar el resultado junto con la trazabilidad completa del razonamiento.

La aplicación entrega, para cada consulta: diagnóstico principal con nivel de certeza, estado del cuadro (agudo o crónico), valor difuso de la picazón con sus grados de membresía, diagnósticos alternativos (segundo y tercero más probables) cuando corresponde, recomendaciones generadas, y la cadena de reglas activadas que justifica la conclusión. Incluye además la advertencia explícita de que el sistema es orientativo y no reemplaza la consulta con un médico especialista.

### **Integración inicial del robot** {#integración-inicial-del-robot}

Estado: diseñada, en curso. La arquitectura prevé a RAPIRO como plataforma física de percepción ubicada junto a la especialista: captura la imagen de la lesión con su cámara (webcam USB de buena calidad) y exhibe comportamiento observable (autocaptura al detectar encuadre y cercanía adecuados, LEDs y orientación). El robot no conduce interrogatorio hablado ni interactúa de forma autónoma con el paciente; la anamnesis la realiza y registra la profesional. En coherencia con esta decisión, el reconocimiento y la síntesis de voz quedaron fuera del alcance.

A la fecha de este avance, el componente inteligente corre sobre equipo de desarrollo propio; la integración sobre RAPIRO y el módulo de captura están planificados en el cronograma (Sprint 2). El desarrollo se realiza sobre la Raspberry Pi 5 propia para no depender de la disponibilidad del robot prestado.

### **Pruebas preliminares del componente inteligente** {#pruebas-preliminares-del-componente-inteligente}

Se ejecutaron los siete casos de prueba (C1 a C7) que cubren el espectro de cuadros de la base de conocimiento. En los siete, el sistema produjo un diagnóstico principal determinado con su cadena de razonamiento trazable. El resumen de resultados es el siguiente:

* C1 Psoriasis: codos / escama / blanco nacarado / picazón 7 (Moderada) / 8 meses / estrés Sí. Resultado: Psoriasis, certeza 99 %, Crónico. Reglas R05, R06, R16, R07 (heurística por estrés) y R20 (derivación). Recomendación: derivación urgente a dermatólogo.  
* C2 Acné: cara / pápula / rojo / picazón 2 (Nula) / 1 mes / estrés No. Resultado: Acné, certeza 85 %, Agudo. Reglas R03, R15 y R17. Recomendación: tratamiento tópico leve.  
* C3 Dishidrosis: pies / ampolla / rosado / picazón 8 (Intensa) / 2 meses / estrés No. Resultado: Dishidrosis, certeza 83 %, Agudo. Reglas R09 y R15.  
* C4 Pitiriasis alba: cara / mácula / rosado / picazón 1 (Nula) / 5 meses / estrés No. Resultado: Pitiriasis alba, certeza 99 %, Crónico. Reglas R10, R16 y R19 (difusa).  
* C5 Onicomicosis: uñas / engrosamiento / amarillento / picazón 0 (Nula) / 10 meses / estrés No. Resultado: Onicomicosis, certeza 99 %, Crónico. Reglas R01, R02 y R16.  
* C6 Eccema: flexuras / escama / rojo / picazón 8 (Intensa) / 2 meses / estrés Sí. Resultado: Eccema, certeza 99 %, Agudo. Reglas R12 y R13 (difusas), R15 y R14 (heurística, origen psicosomático).  
* C7 Crítico (ambigüedad eccema/psoriasis): flexuras / escama / blanco nacarado / picazón 8 (Intensa) / 6 meses / estrés Sí. Resultado: Psoriasis 87 %, con Eccema 82 % como alternativo cercano, Crónico. Reglas R06, R12, R16, R07, R14 y R20. El sistema expone la ambigüedad residual en lugar de ocultarla.

### **Evidencias de inferencia** {#evidencias-de-inferencia}

La técnica de IA central del sistema es la inferencia (no el aprendizaje automático), por lo que la evidencia no es un entrenamiento sino la trazabilidad del razonamiento. Las capturas de los siete casos documentan, para cada uno: las entradas recibidas, las membresías de la lógica difusa de la picazón (grados Nula, Leve, Moderada, Intensa), las reglas activadas con su tipo (determinista, difusa, heurística) y su aporte de certeza, las recomendaciones generadas y la certeza acumulada por diagnóstico. Esta trazabilidad explícita es la prueba observable de que el sistema infiere y explica, y no opera como una caja negra. Las siete capturas se adjuntan como anexo de evidencia.

Se destaca el caso C7: ante una combinación de síntomas compatible con dos cuadros, el motor combina reglas deterministas, difusas y heurísticas, y entrega un diagnóstico principal (Psoriasis 87 %) sin descartar el alternativo cercano (Eccema 82 %). Esto demuestra el manejo de incertidumbre mediante factores de certeza y lógica difusa.

*(Nota: la capa de visión —red neuronal que infiere morfología y color— es un componente comprometido pero aún no entrenado a esta fecha; sus evidencias de desempeño, por variable y por clase, se incorporarán una vez completados el etiquetado y el entrenamiento.)*

### **Integración inicial con servicios cloud** {#integración-inicial-con-servicios-cloud}

Estado: parcialmente implementada, en curso. El modelo de cómputo (serverless frente a máquina virtual) permanece como decisión abierta A7. A la fecha se aprovisionó y está operativa una **máquina virtual en Amazon EC2**, que será el entorno de despliegue del servicio de inferencia del motor experto y del servicio de inferencia de la red de visión (este último servido sobre CPU). La inferencia del motor se ejecuta hoy localmente; su exposición como servicio sobre la VM está planificada en el Sprint 1–2. La persistencia de consultas e imágenes (con consentimiento y minimización de datos) y su esquema de seguridad están en definición. Al haberse descartado la interacción por voz, no se utilizan servicios cognitivos de síntesis ni reconocimiento de voz.

### **Configuración básica de infraestructura y monitoreo** {#configuración-básica-de-infraestructura-y-monitoreo}

Estado: en curso, con la base de la infraestructura ya implementada. El criterio de diseño es mínimo viable y reproducible por código (IaC con Terraform). El monitoreo se resolverá según A7: en el camino de VM, mediante logs de acceso del reverse proxy y métricas básicas del sistema (CPU, memoria, disco), complementables con el agente de CloudWatch.

Trabajo de infraestructura ya realizado sobre la VM:

* Acceso administrativo por consola remota vía SSH con autenticación por clave (par de claves generado previamente y cargado en la instancia mediante la CLI de AWS), de modo que solo quien posee la clave privada puede acceder.  
* Gestión de accesos del equipo: la VM se creó sobre la cuenta de AWS de Stefano y se creó un usuario IAM (gabriel-seadd-user) para dar acceso a Gabriel mediante aws-cli.  
* DNS dinámico configurado con noIP apuntando a seadd.ddns.net; las credenciales de actualización dinámica se almacenaron en /etc/default/noip-duc y se creó y habilitó un servicio systemd (noip-duc) para mantener el registro actualizado de forma automática y resiliente a reinicios.

*(Pendiente: aprovisionamiento por Terraform del conjunto completo de recursos, despliegue de los servicios de inferencia y panel de métricas.)*

### **Avance del paper académico** {#avance-del-paper-académico}

El paper se encuentra en estado de borrador avanzado, con la siguiente estructura y nivel de avance:

* Resumen / Abstract: redactado.  
* Introducción y problema: redactado, con citas en el cuerpo incorporadas.  
* Antecedentes y marco teórico (sistemas expertos, factores de certeza, lógica difusa, arquitectura neuro-simbólica): redactado, con referencias APA 7 cargadas.  
* Arquitectura y metodología: redactado, con diagrama de arquitectura de alto nivel incorporado.  
* Resultados (casos de prueba y trazabilidad): redactado a partir de los datos de los siete casos, con la salvedad de que las métricas del componente de visión quedan pendientes de medición.  
* Discusión, responsabilidad social y conclusiones: esbozado.

### **Seguimiento y control del proyecto** {#seguimiento-y-control-del-proyecto}

El seguimiento y control se realizó bajo el marco híbrido Scrum-Kanban (Schwaber & Sutherland, 2020).

Tareas completadas: readaptación del caso de estudio y consolidación del documento de Etapa 1; componente inteligente (motor híbrido y subsistema de explicación) funcional y probado sobre los siete casos; provisión de la máquina virtual y configuración base de acceso y DNS.

Tareas pendientes: etiquetado del subconjunto de imágenes y entrenamiento de la red de visión; integración visión→motor; integración física sobre RAPIRO y módulo de captura; exposición del motor y de la visión como servicios sobre la VM; infraestructura como código (Terraform) y monitoreo; paper y póster finales.

Desviaciones detectadas: el cambio de enfoque, decidido de forma tardía, comprimió el cronograma original y reordenó las prioridades. Como consecuencia, el avance es asimétrico respecto del plan: el componente inteligente ya está funcional, mientras que la integración con hardware y nube está retrasada. La estrategia adoptada fue priorizar el núcleo de IA —el corazón demostrable del proyecto— y declarar la integración como diseñada y en curso, con avances concretos ya verificables en la infraestructura.

### **Gestión de riesgos** {#gestión-de-riesgos}

Riesgos materializados: el cambio de tema del proyecto (R01) y el plazo ajustado derivado de él (R03/R06) son los de mayor impacto en esta etapa; también se materializaron la descoordinación entre integrantes (R04) y la baja disponibilidad horaria (R05). El acceso limitado a RAPIRO (R02/R08) permanece vigente y condicionó la decisión de desarrollar sobre equipo propio.

Acciones preventivas aplicadas: reutilización del trabajo previo de SEADD (motor, base de conocimiento y casos de prueba) en lugar de construir desde cero; desarrollo del componente inteligente sobre Raspberry Pi 5 y equipo propio, desacoplado de la disponibilidad del robot.

Acciones correctivas aplicadas: acotamiento del alcance al mínimo defendible (núcleo de IA funcional más diseño e implementación parcial de la integración); repriorización por hitos; adopción de tablero de tareas y puntos de control frecuentes, con repositorio y documentos compartidos como fuente única.

Contingencias aplicadas: presentación del avance como entregable documentado y honesto —lo hecho como hecho y lo pendiente como diseñado—, apoyado en la evidencia de inferencia ya disponible, en lugar de forzar una demo integral incompleta.

*(El registro de riesgos detallado R01–R16, con categoría, probabilidad, impacto, nivel y estado, se incorpora en la sección Matriz de Riesgos.)*

### **Métricas e indicadores** {#métricas-e-indicadores}

Precisión del modelo experto: en los siete casos de prueba, el sistema produjo un diagnóstico principal determinado con trazabilidad (7/7 con salida determinada). La concordancia con el criterio de la experta se estima en 85,7 % (6/7) según la línea base del trabajo previo y se encuentra en revalidación sobre estas corridas. El caso C7 (ambigüedad psoriasis/eccema, 87 % y 82 %) es el caso piloto de mejora.

Tiempos de respuesta: inferencia en menos de 2 segundos en ejecución local (meta menor a 1 segundo en versión sobre la VM).

Desempeño de la red de visión: pendiente de medición; se reportará de forma desagregada por variable (morfología y color) y por clase, con evaluación por subgrupos de tono de piel cuando sea posible, una vez completado el entrenamiento.

Disponibilidad: medible una vez expuestos los servicios sobre la VM.

Cumplimiento de objetivos: el objetivo del componente inteligente (inferencia con razonamiento explicable) está cumplido; los de integración física, visión, cloud, IaC y monitoreo están en curso, con la base de infraestructura ya iniciada.

La mejora se gestiona con ciclos Kaizen: identificar la causa raíz de cada error de clasificación, ajustar reglas o rangos difusos, y re-ejecutar los casos de prueba hasta alcanzar la meta.

### **Retrospectiva parcial** {#retrospectiva-parcial}

Dificultades encontradas: el cambio de tema a mitad del proceso obligó a reorganizar el proyecto con muy poco margen; la integración de múltiples tecnologías nuevas (robot, visión, nube, IaC) con un equipo de dos personas presiona el cronograma.

Decisiones tomadas: reutilizar SEADD como base por estar validado y funcional; priorizar el componente inteligente como núcleo demostrable y diferir la integración a sprints posteriores; mantener el reconocimiento y la síntesis de voz fuera del alcance (la médica conduce la anamnesis y registra), por confiabilidad y simplicidad; comprometer la capa de visión como extractor de morfología y color (opción 2\) contenido por la doble entrada.

Mejoras implementadas: acotamiento explícito del alcance con criterios de mínimo viable por ítem; documentación de la trazabilidad de los siete casos como evidencia central; identificación del caso C7 como piloto de mejora Kaizen (incorporar mensaje de ambigüedad y sugerencia de biopsia o raspado).

La retrospectiva se versiona en un documento compartido del equipo. \[Insertar aquí el link al documento compartido antes de la entrega.\]

### **Responsabilidad social en la definición y justificación del caso** {#responsabilidad-social-en-la-definición-y-justificación-del-caso}

La perspectiva de responsabilidad social es parte constitutiva del caso de estudio y no un agregado posterior. El problema que aborda SEADD —la disponibilidad limitada de dermatólogos y la imprecisión del interrogatorio clínico— tiene impacto directo en la equidad del acceso a un diagnóstico de calidad. La solución se justifica socialmente en tres planos:

* Acceso: acerca orientación diagnóstica basada en conocimiento experto a contextos con escasa disponibilidad de especialistas, especialmente el primer nivel de atención, reduciendo la brecha de acceso.  
* No sustitución del criterio médico: el sistema se posiciona explícitamente como herramienta de apoyo; su salida es una orientación, no un diagnóstico definitivo, y así lo declara en pantalla. El resultado se entrega al especialista y no al paciente, lo que evita el autodiagnóstico y la ansiedad por resultados preliminares.  
* Responsabilidad y trazabilidad: la cadena de razonamiento auditable permite que el profesional entienda y cuestione por qué el sistema llegó a una conclusión, y el conocimiento incorporado está atribuido a la experta entrevistada. Esto aborda el dilema ético central del uso diagnóstico sin habilitación regulatoria mediante transparencia, restricción de acceso y trazabilidad.

Estos objetivos se alinean con el ODS 3 (Salud y bienestar) y el ODS 9 (Industria, innovación e infraestructura) de la Agenda 2030 (United Nations, 2015\) y con la noción de inteligencia artificial responsable orientada al bienestar humano (Russell & Norvig, 2022).

# **Anexo** {#anexo}

Retrospectiva 3 little pigs: [https://docs.google.com/spreadsheets/d/1pPtgKfjcHifu3S8MKGhKT76qw8Vdsr8kCD-z1hBGyOw/edit?usp=sharing](https://docs.google.com/spreadsheets/d/1pPtgKfjcHifu3S8MKGhKT76qw8Vdsr8kCD-z1hBGyOw/edit?usp=sharing) 

# **Referencias** {#referencias}

Alarcón, C. E. (2026). Entrevista de elicitación de conocimiento para sistema experto en dermatología \[Comunicación personal\].  
Filho, F., Santos, E., Mota, R., Cunha, K., Papais, F., Arruda, A., Baltazar, M., Vieira, C., Tavares, J. G., Barros, R., Souza, O., Bezerra, T., Lopes, N., Medeiros, E., Guido, J., Cruz, S., Borba, P., & Ren, T. I. (2025). An analysis of data variation and bias in image-based dermatological datasets for machine learning classification \[Preprint\]. arXiv. https://arxiv.org/abs/2501.08962  
Klir, G. J., & Yuan, B. (1995). Fuzzy sets and fuzzy logic: Theory and applications. Prentice Hall.  
Nawaz, U., Anees-ur-Rahaman, M., & Saeed, Z. (2025). A review of neuro-symbolic AI integrating reasoning and learning for advanced cognitive systems. Intelligent Systems with Applications, 26, Article 200541\. https://doi.org/10.1016/j.iswa.2025.200541  
Pacheco, A. G. C., Lima, G. R., Salomão, A. S., Krohling, B., Biral, I. P., de Angelo, G. G., Alves, F. C. R., Jr., Esgario, J. G. M., Simora, A. C., Castro, P. B. C., Rodrigues, F. B., Frasson, P. H. L., Krohling, R. A., Knidel, H., Santos, M. C. S., do Espírito Santo, R. B., Macedo, T. L. S. G., Canuto, T. R. P., & de Barros, L. F. S. (2020). PAD-UFES-20: A skin lesion dataset composed of patient data and clinical images collected from smartphones. Data in Brief, 32, Article 106221\. https://doi.org/10.1016/j.dib.2020.106221  
Russell, S., & Norvig, P. (2022). Artificial intelligence: A modern approach (4.ª ed.). Pearson.  
Schwaber, K., & Sutherland, J. (2020). The Scrum Guide: The definitive guide to Scrum: The rules of the game. https://scrumguides.org  
Shortliffe, E. H., & Buchanan, B. G. (1975). A model of inexact reasoning in medicine. Mathematical Biosciences, 23(3-4), 351-379. https://doi.org/10.1016/0025-5564(75)90047-4  
United Nations. (2015). Transforming our world: The 2030 Agenda for Sustainable Development (A/RES/70/1). https://sdgs.un.org/2030agenda  
Zadeh, L. A. (1965). Fuzzy sets. Information and Control, 8(3), 338-353. https://doi.org/10.1016/S0019-9958(65)90241-X

[image1]: <data:image/png;base64,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>