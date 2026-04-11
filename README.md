# Análisis de reposición ficticio

## Descripción

Este proyecto consiste en la construcción de un modelo de análisis de reposición en un entorno ficticio de retail. El objetivo es simular un escenario real de gestión de inventario, considerando demanda, niveles de stock y riesgo de quiebre, utilizando Python como herramienta principal de análisis.

El desarrollo se realiza a partir de datos generados artificialmente, estructurados de forma que permitan replicar un flujo de trabajo similar al de un analista de reposición en una operación real.

---

## Construcción de la base de datos

Dado que no se cuenta con datos reales, se generaron tres bases de datos en formato CSV:

- `productos.csv`: contiene información de los productos, incluyendo categoría, precios y tiempos de entrega.
- `ventas.csv`: registra ventas diarias por producto y tienda.
- `inventario.csv`: representa un snapshot del inventario, incluyendo stock disponible y stock en tránsito.

La generación de estas bases se realizó mediante scripts en Python, incorporando lógica de negocio para simular comportamientos realistas.

---

## Supuestos del modelo

Para dar consistencia al análisis, se definieron los siguientes supuestos:

### Demanda

- La demanda depende de la categoría del producto.
- Se asignan distintos niveles de variabilidad según tipo de producto.
- Se incorporan diferencias por tienda, asociadas a tamaño o volumen de operación.
- Existen productos con demanda baja o intermitente.

### Inventario

- El stock disponible se calcula en función de la demanda promedio y días de cobertura.
- El stock en tránsito se modela de forma probabilística.
- No todos los productos tienen órdenes en tránsito activas.

### Cobertura

- Se establecen rangos de cobertura distintos por categoría.
- La cobertura se basa en la demanda promedio diaria.

---

## Procesamiento y análisis

El flujo desarrollado hasta este punto es el siguiente:

### 1. Cálculo de demanda promedio

Se calcula la demanda promedio diaria por producto y tienda a partir del histórico de ventas.

Demanda promedio diaria = promedio(unidades vendidas)

---

### 2. Análisis de demanda

Se generan visualizaciones que permiten entender el comportamiento de la demanda:

- Demanda promedio por categoría (visión general)
- Demanda promedio por categoría y tienda (visión local)

Esto permite identificar diferencias en el mix de productos entre tiendas.

---

### 3. Construcción de stock total

Se define el stock total como la suma de:

Stock total = stock disponible + stock en tránsito

---

### 4. Cálculo de Days of Supply

Se calcula la cobertura de inventario en días utilizando la demanda promedio:

Days of Supply = stock total / demanda promedio diaria

Se consideran casos donde la demanda es cero para evitar divisiones inválidas.

---

### 5. Análisis de cobertura

Se generan visualizaciones para evaluar la cobertura:

- Days of Supply promedio por categoría (general)
- Days of Supply promedio por categoría y tienda

Se incorporan referencias para interpretación:

- Bajo 7 días: riesgo de quiebre
- Sobre 20 días: posible sobrestock

---

### 6. Identificación de riesgo

Se identifican productos con menor cobertura, permitiendo detectar riesgo de quiebre a nivel de producto y tienda.

---

## Estado actual

El proyecto actualmente permite:

- Generar bases de datos ficticias con lógica de negocio
- Calcular demanda promedio por producto y tienda
- Analizar demanda a nivel general y por tienda
- Calcular cobertura de inventario (Days of Supply)
- Detectar riesgo de quiebre
- Generar gráficos para análisis comercial y operativo

---

## Próximas implementaciones

En la siguiente etapa se incorporarán modelos de decisión de reposición.

### Reorder Point (ROP)

ROP = demanda promedio diaria × tiempo de entrega

Permitirá determinar el momento en que se debe emitir una orden de compra.

---

### Cantidad a pedir

Cantidad a pedir = stock objetivo - stock actual

El stock objetivo se definirá en función de una cobertura deseada.

---

### EOQ (Economic Order Quantity)

Se implementará un modelo de cantidad económica de pedido para optimizar el tamaño de las órdenes de reposición.

---

## Herramientas utilizadas

- Python
- Pandas
- NumPy
- Matplotlib
- Git / GitHub

---

## Autor

Ricardo Tapia Pinto