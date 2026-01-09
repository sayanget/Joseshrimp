# Manual de Usuario - Sistema de Gestión de Ventas

**Versión:** 1.0.0  
**Fecha:** Enero 2026  
**Operador:** Jose Burgueno

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Inicio de Sesión](#inicio-de-sesión)
4. [Panel Principal](#panel-principal)
5. [Gestión de Ventas](#gestión-de-ventas)
6. [Gestión de Inventario](#gestión-de-inventario)
7. [Reportes y Estadísticas](#reportes-y-estadísticas)
8. [Administración del Sistema](#administración-del-sistema)
9. [Cambio de Idioma](#cambio-de-idioma)
10. [Preguntas Frecuentes](#preguntas-frecuentes)
11. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

### ¿Qué es el Sistema de Gestión de Ventas?

El Sistema de Gestión de Ventas es una aplicación web completa diseñada para gestionar eficientemente las operaciones de ventas, inventario y reportes de su negocio. El sistema está construido con tecnología moderna y ofrece una interfaz intuitiva y fácil de usar.

### Características Principales

- ✅ **Gestión de Ventas**: Crear, visualizar y anular órdenes de venta
- ✅ **Control de Inventario**: Seguimiento completo de movimientos de stock
- ✅ **Reportes Avanzados**: Estadísticas y gráficos de ventas por fecha, cliente y producto
- ✅ **Administración**: Gestión de especificaciones, clientes y registros de auditoría
- ✅ **Multiidioma**: Soporte para Español, Inglés y Chino
- ✅ **Cálculo Automático**: El sistema calcula automáticamente pesos y totales
- ✅ **Trazabilidad Completa**: Todos los movimientos son auditables y rastreables

### Principios del Sistema

1. **Sin Entrada Libre de Especificaciones**: Todas las especificaciones deben seleccionarse de una lista predefinida
2. **Cálculo Automático de Peso**: El peso total es calculado automáticamente por el sistema
3. **Inventario Rastreable**: Todos los movimientos de inventario son rastreables y recalculables
4. **Sin Eliminación Física**: Los registros solo pueden anularse, nunca eliminarse
5. **Registro de Auditoría Completo**: Todas las operaciones críticas quedan registradas

---

## Requisitos del Sistema

### Para Usar el Sistema

- **Navegador Web Moderno**: 
  - Google Chrome (recomendado)
  - Mozilla Firefox
  - Safari
  - Microsoft Edge
- **Resolución de Pantalla**: Mínimo 1024x768 (funciona en móviles y tablets)
- **Conexión a Internet**: Requerida para acceso al sistema
- **JavaScript**: Debe estar habilitado en el navegador

### Dispositivos Compatibles

- 💻 Computadoras de escritorio (Windows, Mac, Linux)
- 💻 Laptops
- 📱 Tablets
- 📱 Teléfonos móviles (interfaz responsive)

---

## Inicio de Sesión

### Acceder al Sistema

1. Abra su navegador web
2. Navegue a la dirección del sistema (proporcionada por su administrador)
3. Ingrese sus credenciales de usuario:
   - **Usuario**: Su nombre de usuario asignado
   - **Contraseña**: Su contraseña personal
4. Haga clic en **"Iniciar Sesión"**

### Roles de Usuario

El sistema soporta diferentes roles con distintos permisos:

| Rol | Permisos |
|-----|----------|
| **Operador** | Crear órdenes de venta, ver estadísticas, consultar inventario |
| **Administrador** | Todos los permisos del operador + anular órdenes, gestionar especificaciones y clientes, ver registros de auditoría |

### Recuperación de Contraseña

Si olvidó su contraseña, contacte al administrador del sistema para que la restablezca.

---

## Panel Principal

### Vista General

Al iniciar sesión, verá el panel principal con un resumen de las operaciones del día:

- **Ventas del Día**: Total de kilogramos vendidos hoy
- **Órdenes del Día**: Número de órdenes de venta creadas
- **Inventario Actual**: Stock disponible en kilogramos
- **Alertas**: Notificaciones de inventario bajo u otras alertas importantes

### Navegación

La barra de navegación superior contiene los siguientes menús:

- **🏠 Inicio**: Panel principal con resumen del día
- **📋 Ventas**: Gestión de órdenes de venta
- **📦 Inventario**: Control de stock y movimientos
- **📊 Reportes**: Estadísticas y análisis de ventas
- **⚙️ Admin**: Configuración del sistema (solo administradores)
- **🌐 Idioma**: Selector de idioma (ES/EN/中文)

---

## Gestión de Ventas

### Crear una Nueva Orden de Venta

#### Paso 1: Acceder al Formulario

1. Haga clic en **"Ventas"** en el menú superior
2. Haga clic en el botón **"Nueva Venta"** o **"+ Crear Venta"**

#### Paso 2: Información General

Complete los siguientes campos obligatorios:

**Cliente**
- Seleccione el cliente de la lista desplegable
- Si el cliente no existe, solicite al administrador que lo agregue

**Tipo de Pago**
- **Efectivo**: Pago inmediato en efectivo
- **Crédito**: Pago diferido (solo disponible si el cliente tiene crédito habilitado)

**Fecha y Hora**
- Se completa automáticamente con la fecha y hora actual
- Puede modificarse si es necesario

#### Paso 3: Agregar Productos

Para cada producto que desea vender:

1. Haga clic en el botón **"+ Agregar Producto"**
2. Complete los siguientes campos:

**Especificación**
- Seleccione el tipo de producto de la lista (ejemplo: "20 KG", "JAVA 39x110")
- Cada especificación tiene un peso definido por caja

**Cantidad de Cajas**
- Ingrese el número de cajas completas
- Debe ser un número entero (0, 1, 2, 3, etc.)

**Kilogramos Extra (Producto Suelto)**
- Ingrese el peso de producto suelto adicional
- Este campo es opcional
- Use punto decimal si es necesario (ejemplo: 10.5)

**Subtotal**
- Se calcula automáticamente: **(Cajas × KG por Caja) + KG Extra**
- No puede editarse manualmente

**Ejemplo Práctico:**
- Especificación: "20 KG" (cada caja pesa 20 kg)
- Cantidad de Cajas: 5
- Kilogramos Extra: 10
- **Subtotal calculado**: (5 × 20) + 10 = **110 KG**

#### Paso 4: Agregar Más Productos (Opcional)

Si la orden incluye varios productos:
- Repita el Paso 3 para cada producto adicional
- Puede agregar tantos productos como necesite
- Para eliminar un producto, haga clic en el botón **"✖ Eliminar"** junto a ese producto

#### Paso 5: Revisar y Guardar

1. Revise el **Total General (KG)** que se muestra al final del formulario
2. Verifique que todos los datos sean correctos
3. Haga clic en el botón **"💾 Guardar Venta"**

**El sistema automáticamente:**
- Generará un ID único para la venta (ejemplo: `SALE-20260108-001`)
- Actualizará el inventario (restará el stock vendido)
- Creará un registro de auditoría
- Mostrará un mensaje de confirmación

### Ver Lista de Ventas

#### Acceder a la Lista

1. Haga clic en **"Ventas"** en el menú principal
2. Verá una tabla con todas las órdenes de venta

#### Filtrar Ventas

Utilice los filtros disponibles para encontrar ventas específicas:

**Por Fecha**
- Seleccione fecha de inicio y fecha de fin
- Haga clic en "Filtrar"

**Por Cliente**
- Seleccione un cliente específico del menú desplegable

**Por Estado**
- **Activo**: Ventas válidas y vigentes
- **Anulado**: Ventas canceladas

#### Información en la Lista

La tabla muestra las siguientes columnas:

| Columna | Descripción |
|---------|-------------|
| **ID** | Número único de identificación de la orden |
| **Fecha** | Fecha y hora en que se creó la venta |
| **Cliente** | Nombre del cliente |
| **Total (KG)** | Peso total vendido en kilogramos |
| **Tipo de Pago** | Efectivo o Crédito |
| **Estado** | Activo o Anulado |
| **Acciones** | Botones para ver detalles o anular |

### Ver Detalles de una Venta

1. En la lista de ventas, localice la orden que desea consultar
2. Haga clic en el botón **"👁️ Ver"** o **"Ver Detalles"**
3. Se abrirá una ventana emergente mostrando:
   - Información general de la venta
   - Lista completa de productos vendidos
   - Subtotales por producto
   - Total general
   - Historial de cambios (si aplica)

### Anular una Venta

⚠️ **Importante**: Las ventas NO se pueden eliminar del sistema, solo se pueden anular. Esto garantiza la trazabilidad completa de todas las operaciones.

#### Cuándo Anular una Venta

- Error en la captura de datos
- Cliente canceló la orden
- Devolución completa de mercancía
- Cualquier situación que invalide la venta

#### Proceso de Anulación

1. Abra los detalles de la venta que desea anular
2. Haga clic en el botón **"❌ Anular Venta"**
3. Aparecerá un cuadro de confirmación
4. **Ingrese el motivo de anulación** (obligatorio)
   - Sea específico y claro
   - Ejemplo: "Cliente canceló la orden", "Error en captura"
5. Haga clic en **"Confirmar Anulación"**

#### Efectos de la Anulación

Cuando anula una venta, el sistema automáticamente:
- ✅ Cambia el estado de la venta a "Anulado"
- ✅ Devuelve el inventario (suma el stock vendido)
- ✅ Crea un registro de auditoría con el motivo
- ✅ Mantiene la venta visible para consultas futuras
- ✅ Registra quién anulé la venta y cuándo

### Resumen de Ventas del Día

Para ver un resumen rápido de las ventas del día actual:

1. En el menú **"Ventas"**, haga clic en **"Resumen del Día"**
2. Verá información consolidada:
   - **Total de Ventas**: Kilogramos vendidos hoy
   - **Número de Órdenes**: Cantidad de ventas realizadas
   - **Desglose por Tipo de Pago**:
     - Total en Efectivo
     - Total en Crédito
   - **Clientes Atendidos**: Número de clientes diferentes

---

## Gestión de Inventario

### Ver Inventario Actual

#### Acceder al Inventario

1. Haga clic en **"Inventario"** en el menú principal
2. En la parte superior verá el **Stock Actual** en kilogramos

#### Indicadores de Inventario

El sistema usa colores para indicar el estado del inventario:

- **🟢 Verde**: Inventario normal (más de 100 KG)
- **🟡 Amarillo**: Inventario bajo (entre 50 y 100 KG) - Considere reabastecer
- **🔴 Rojo**: Inventario crítico (menos de 50 KG) - Reabastezca urgentemente

### Movimientos de Inventario

#### Ver Historial de Movimientos

1. En la sección **"Inventario"**, haga clic en **"Movimientos"** o **"Historial"**
2. Verá una lista cronológica de todos los movimientos de inventario

#### Información de Movimientos

Cada movimiento muestra:

| Columna | Descripción |
|---------|-------------|
| **Fecha y Hora** | Cuándo ocurrió el movimiento |
| **Tipo** | Categoría del movimiento (ver tipos abajo) |
| **Origen/Fuente** | De dónde proviene el movimiento |
| **Cantidad (KG)** | Peso (positivo = entrada, negativo = salida) |
| **Referencia** | ID de venta u orden relacionada |
| **Estado** | Activo o Anulado |

#### Tipos de Movimientos

- **📤 Venta**: Salida de mercancía por venta (automático)
- **📥 Compra**: Entrada de mercancía nueva
- **🔧 Ajuste**: Corrección manual de inventario
- **🚚 Traslado**: Movimiento entre ubicaciones
- **↩️ Devolución**: Mercancía devuelta por cliente
- **➕ Inventario Positivo**: Diferencia positiva en conteo físico
- **➖ Inventario Negativo**: Diferencia negativa en conteo físico

### Agregar Movimiento de Inventario

#### Registrar Entrada de Mercancía (Compra)

Cuando recibe mercancía nueva:

1. Haga clic en **"+ Nuevo Movimiento"**
2. Complete el formulario:
   - **Tipo de Movimiento**: Seleccione "Compra" o "Entrada"
   - **Cantidad (KG)**: Ingrese el peso recibido (número positivo)
   - **Origen/Proveedor**: Nombre del proveedor o fuente
   - **Número de Factura**: Referencia de la factura (opcional)
   - **Notas**: Información adicional (opcional)
3. Haga clic en **"Guardar"**

El inventario se actualizará automáticamente sumando la cantidad ingresada.

#### Registrar Ajuste de Inventario

Para correcciones manuales del inventario:

1. Seleccione **"Ajuste"** como tipo de movimiento
2. Ingrese la cantidad:
   - **Número positivo**: Para aumentar el inventario
   - **Número negativo**: Para disminuir el inventario
3. **Agregue notas explicativas** (muy importante para auditoría)
   - Ejemplo: "Ajuste por merma", "Corrección de error de captura"
4. Guarde el movimiento

### Inventario Físico (Conteo)

#### Realizar Conteo Físico

El conteo físico es importante para verificar que el inventario del sistema coincida con la realidad:

**Paso 1: Contar Físicamente**
- Cuente toda la mercancía en su almacén o bodega
- Use una báscula para obtener el peso exacto
- Anote el resultado

**Paso 2: Registrar en el Sistema**
1. Vaya a **"Inventario"** → **"Inventario Físico"** o **"Conteo"**
2. Complete el formulario:
   - **Inventario Real (KG)**: Cantidad que contó físicamente
   - **Fecha de Conteo**: Fecha en que realizó el conteo
   - **Notas**: Observaciones o comentarios
3. El sistema mostrará automáticamente:
   - **Inventario Teórico**: Lo que el sistema tiene registrado
   - **Diferencia**: Real - Teórico
     - Positivo = Hay más mercancía de la registrada
     - Negativo = Hay menos mercancía de la registrada

**Paso 3: Confirmar**
- Revise la diferencia
- Haga clic en **"Registrar Conteo"**

#### Ajustar Diferencias

Si hay diferencias entre el conteo físico y el sistema:

1. El sistema creará automáticamente un movimiento de ajuste
2. El inventario se actualizará al valor real contado
3. Se registrará en el historial de auditoría para trazabilidad
4. Investigue las causas de la diferencia (merma, robo, error de captura, etc.)

### Análisis de Tendencias de Inventario

Para ver cómo evoluciona el inventario en el tiempo:

1. Vaya a **"Inventario"** → **"Tendencias"** o **"Gráficos"**
2. Seleccione el período que desea analizar (última semana, mes, etc.)
3. Verá un gráfico mostrando:
   - Evolución del inventario día a día
   - Entradas (compras, devoluciones)
   - Salidas (ventas)
   - Puntos donde el inventario estuvo bajo

---

## Reportes y Estadísticas

### Panel de Reportes

El módulo de reportes le permite analizar el desempeño de su negocio desde diferentes perspectivas.

**Acceso**: Haga clic en **"📊 Reportes"** en el menú principal

### Reporte de Ventas por Fecha

Este reporte muestra la evolución de las ventas en el tiempo.

#### Generar el Reporte

1. Haga clic en **"Ventas por Fecha"** o **"Reporte Diario"**
2. Seleccione el período de análisis:
   - **Fecha Inicio**: Primer día del período
   - **Fecha Fin**: Último día del período
3. Haga clic en **"Generar Reporte"** o **"Consultar"**

#### Información Mostrada

**Gráfico de Líneas**
- Muestra la tendencia de ventas día a día
- Eje horizontal: Fechas
- Eje vertical: Kilogramos vendidos

**Tabla Detallada**
- Fecha
- Número de órdenes de venta
- Total vendido en kilogramos
- Promedio por orden

#### Exportar Datos

- Haga clic en **"📥 Exportar a Excel"** para descargar los datos
- El archivo se guardará en su carpeta de descargas

### Reporte de Ventas por Cliente

Identifique quiénes son sus mejores clientes.

#### Generar Ranking de Clientes

1. Seleccione **"Ventas por Cliente"** o **"Ranking de Clientes"**
2. Elija el período de análisis
3. Haga clic en **"Generar"**

#### Información Disponible

**Top 10 Clientes**
- Lista de los 10 clientes que más compran
- Ordenados por volumen de compra (kilogramos)

**Gráfico de Barras**
- Comparación visual entre clientes
- Facilita identificar los clientes más importantes

**Tabla Completa**
- Nombre del cliente
- Número de órdenes realizadas
- Total comprado en kilogramos
- Porcentaje del total de ventas
- Tipo de pago predominante

**Utilidad**: Use este reporte para:
- Identificar clientes VIP
- Diseñar programas de lealtad
- Priorizar atención a clientes importantes

### Reporte de Ventas por Producto

Analice qué productos se venden más.

#### Generar Análisis de Especificaciones

1. Acceda a **"Ventas por Producto"** o **"Productos Más Vendidos"**
2. Seleccione el período
3. Genere el reporte

#### Información Presentada

**Productos Más Vendidos**
- Top 10 especificaciones más vendidas
- Ordenadas por volumen

**Gráfico Circular (Pie Chart)**
- Distribución porcentual de ventas por producto
- Visualiza qué productos dominan las ventas

**Tabla Detallada**
- Nombre de la especificación
- Número de cajas vendidas
- Total en kilogramos
- Porcentaje del total
- Número de órdenes que lo incluyeron

**Utilidad**: Use este reporte para:
- Planificar compras de inventario
- Identificar productos de baja rotación
- Optimizar su catálogo de productos

### Análisis de Producto Suelto

Este reporte analiza la proporción de producto suelto (kilogramos extra) versus producto en cajas completas.

#### Generar Reporte de Kilogramos Extra

1. Vaya a **"Análisis de Suelto"** o **"Producto Suelto"**
2. Seleccione el período
3. Consulte el análisis

#### Métricas Mostradas

- **Porcentaje de Suelto**: (KG Extra / Total KG) × 100
- **Tendencia**: Evolución del porcentaje en el tiempo
- **Alertas**: Notificaciones si el porcentaje es alto

#### Interpretación de Resultados

| Porcentaje | Interpretación | Acción |
|------------|----------------|--------|
| **< 20%** | ✅ Normal | Ninguna |
| **20-30%** | ⚠️ Revisar | Monitorear tendencia |
| **> 30%** | 🔴 Alerta | Investigar causas |

**Causas comunes de alto porcentaje de suelto:**
- Problemas en el empaque del proveedor
- Cajas dañadas
- Preferencias específicas de clientes
- Merma o desperdicio

### Resumen Ejecutivo

El dashboard ejecutivo consolida todas las métricas importantes en una sola vista.

#### Acceder al Dashboard

1. Vaya a **"Reportes"** → **"Resumen"** o **"Dashboard"**
2. Seleccione el período de análisis

#### Métricas Incluidas

**Ventas**
- Ventas totales del período (KG y valor)
- Número total de órdenes
- Ticket promedio (KG por orden)
- Comparación con período anterior (% de crecimiento)

**Clientes**
- Clientes activos (que compraron en el período)
- Nuevos clientes
- Cliente top (el que más compró)

**Productos**
- Producto más vendido
- Número de especificaciones activas
- Porcentaje de producto suelto

**Inventario**
- Stock actual
- Días de inventario (estimado)
- Alertas de stock bajo

**Gráficos de Tendencias**
- Ventas diarias
- Comparación semanal
- Evolución mensual

---

## Administración del Sistema

**Nota**: Las funciones de administración solo están disponibles para usuarios con rol de Administrador.

### Gestión de Especificaciones

Las especificaciones definen los tipos de productos que puede vender.

#### Ver Especificaciones

1. Vaya a **"Admin"** → **"Especificaciones"** o **"Productos"**
2. Verá una tabla con todas las especificaciones disponibles

#### Agregar Nueva Especificación

Cuando necesite agregar un nuevo tipo de producto:

1. Haga clic en **"+ Nueva Especificación"**
2. Complete el formulario:
   - **Nombre**: Nombre descriptivo del producto
     - Ejemplo: "20 KG", "JAVA 39x110", "Camarón Grande"
   - **Kilogramos por Caja**: Peso de una caja completa
     - Debe ser un número mayor a cero
     - Ejemplo: 20, 39, 45.5
   - **Descripción**: Información adicional (opcional)
     - Ejemplo: "Caja de camarones JAVA 39 piezas x 110 gramos"
   - **Activo**: Marque para que esté disponible en ventas
3. Haga clic en **"Guardar"**

**Ejemplo Completo:**
- Nombre: "JAVA 39x110"
- KG por Caja: 39
- Descripción: "Caja de camarones JAVA, 39 piezas de 110 gramos cada una"
- Activo: ✓

#### Editar Especificación

Para modificar una especificación existente:

1. En la lista de especificaciones, localice la que desea editar
2. Haga clic en el botón **"✏️ Editar"**
3. Modifique los campos necesarios
4. Haga clic en **"Guardar Cambios"**

⚠️ **Importante**: 
- Cambiar el peso por caja NO afecta las ventas anteriores
- Las ventas antiguas mantienen el peso que tenían al momento de crearse
- Solo las nuevas ventas usarán el peso actualizado

#### Desactivar Especificación

Para especificaciones que ya no se usan pero no desea eliminar:

1. Localice la especificación en la lista
2. Haga clic en **"🚫 Desactivar"** o desmarque "Activo"
3. Confirme la acción

**Efectos de desactivar:**
- ✅ No aparecerá en el formulario de nuevas ventas
- ✅ Permanece visible en ventas antiguas
- ✅ Puede reactivarse en cualquier momento
- ✅ Se mantiene en reportes históricos

### Gestión de Clientes

Administre la información de sus clientes y sus permisos de crédito.

#### Ver Clientes

1. Vaya a **"Admin"** → **"Clientes"**
2. Verá la lista completa de clientes registrados

#### Agregar Nuevo Cliente

Cuando tenga un nuevo cliente:

1. Haga clic en **"+ Nuevo Cliente"**
2. Complete el formulario:
   - **Nombre**: Nombre del cliente o empresa (obligatorio)
     - Ejemplo: "Restaurante El Camarón", "María González"
   - **Teléfono**: Número de contacto (opcional)
     - Ejemplo: "555-1234"
   - **Dirección**: Dirección de entrega (opcional)
     - Ejemplo: "Calle Principal #123, Colonia Centro"
   - **Email**: Correo electrónico (opcional)
   - **Permitir Crédito**: Marque si el cliente puede comprar a crédito
     - ☑️ Marcado = Cliente puede usar "Crédito" en ventas
     - ☐ Desmarcado = Cliente solo puede pagar en "Efectivo"
   - **Notas**: Información adicional (opcional)
3. Haga clic en **"Guardar Cliente"**

#### Editar Cliente

Para actualizar información de un cliente:

1. En la lista de clientes, haga clic en **"✏️ Editar"**
2. Modifique los campos necesarios
3. Para habilitar o deshabilitar crédito:
   - Marque o desmarque la casilla **"Permitir Crédito"**
4. Guarde los cambios

**Efecto del Crédito:**
- ✅ **Crédito Habilitado**: El operador puede seleccionar "Crédito" al crear ventas para este cliente
- ❌ **Crédito Deshabilitado**: Solo aparecerá la opción "Efectivo" para este cliente

#### Desactivar Cliente

Para clientes que ya no son activos:

1. Haga clic en **"Desactivar"**
2. El cliente no aparecerá en la lista de nuevas ventas
3. Las ventas antiguas del cliente permanecen visibles
4. Puede reactivarse después si es necesario

### Registros de Auditoría

El sistema registra automáticamente todas las operaciones importantes para garantizar trazabilidad completa.

#### Acceder a Logs de Auditoría

1. Vaya a **"Admin"** → **"Auditoría"** o **"Registros"**
2. Verá una lista cronológica de todos los cambios en el sistema

#### Filtrar Registros

Use los filtros para encontrar información específica:

**Por Tabla/Módulo**
- Ventas
- Inventario
- Clientes
- Especificaciones

**Por Acción**
- Crear (INSERT)
- Actualizar (UPDATE)
- Anular (DELETE/VOID)

**Por Fecha**
- Seleccione rango de fechas

**Por Usuario**
- Filtre por operador específico

#### Información en los Logs

Cada registro de auditoría muestra:

| Campo | Descripción |
|-------|-------------|
| **Fecha y Hora** | Cuándo ocurrió el cambio |
| **Usuario** | Quién realizó la acción |
| **Tabla** | Qué módulo se modificó |
| **Acción** | Tipo de operación (Crear/Actualizar/Anular) |
| **ID de Registro** | Identificador del registro afectado |
| **Detalles** | Botón para ver cambios específicos |

#### Ver Detalles de Cambios

Para ver exactamente qué cambió:

1. Haga clic en el botón **"🔍 Ver Detalles"**
2. Se abrirá una ventana mostrando:
   - **Valor Anterior**: Cómo estaba antes del cambio
   - **Valor Nuevo**: Cómo quedó después del cambio
   - **Diferencias**: Campos que cambiaron resaltados

#### Casos de Uso Comunes

**Auditar una venta específica**
- Filtre por "Ventas" y busque el ID de la venta
- Vea quién la creó, cuándo, y si fue anulada

**Investigar discrepancias de inventario**
- Filtre por "Inventario" en el rango de fechas sospechoso
- Revise todos los movimientos registrados

**Verificar cambios en clientes**
- Filtre por "Clientes" y el nombre del cliente
- Vea quién habilitó/deshabilitó el crédito y cuándo

**Cumplimiento normativo**
- Exporte los registros de auditoría para auditorías externas
- Demuestre trazabilidad completa de operaciones

---

## Cambio de Idioma

### Idiomas Disponibles

El sistema soporta tres idiomas:

- 🇪🇸 **Español** (ES)
- 🇬🇧 **English** (EN)
- 🇨🇳 **中文** (ZH - Chino)

### Cambiar el Idioma de la Interfaz

#### Método 1: Selector en la Barra de Navegación

1. Localice el selector de idioma en la esquina superior derecha de la pantalla
2. Haga clic en el idioma actual (ejemplo: "ES")
3. Se desplegará un menú con los idiomas disponibles
4. Seleccione el idioma deseado
5. La página se recargará automáticamente mostrando la interfaz en el nuevo idioma

#### Método 2: Detección Automática

El sistema detecta automáticamente el idioma preferido de su navegador web y lo usa por defecto la primera vez que accede.

### Persistencia del Idioma

- El idioma que seleccione se guarda en su navegador
- Se mantendrá en futuras visitas al sistema
- Se aplica a todas las páginas y módulos
- Cada usuario puede tener su propio idioma preferido

### Elementos Traducidos

El cambio de idioma afecta:
- ✅ Menús de navegación
- ✅ Botones y etiquetas
- ✅ Mensajes del sistema
- ✅ Títulos de páginas
- ✅ Nombres de columnas en tablas
- ✅ Gráficos y reportes

**Nota**: Los datos ingresados por usuarios (nombres de clientes, especificaciones, notas) no se traducen automáticamente.

---

## Preguntas Frecuentes

### Sobre Ventas

**P: ¿Puedo modificar una venta después de crearla?**  
R: No, las ventas no se pueden modificar una vez guardadas. Si hay un error, debe anular la venta incorrecta y crear una nueva con los datos correctos. Esto garantiza la integridad de los registros.

**P: ¿Qué pasa con el inventario cuando anulo una venta?**  
R: El inventario se ajusta automáticamente. El sistema devuelve (suma) el stock que había sido vendido, como si la venta nunca hubiera ocurrido.

**P: ¿Por qué no puedo seleccionar "Crédito" para un cliente?**  
R: El cliente debe tener el crédito habilitado en su configuración. Contacte al administrador del sistema para que habilite el crédito para ese cliente.

**P: ¿Cómo se calcula el peso total de una venta?**  
R: El sistema suma los subtotales de todos los productos. Cada subtotal se calcula como: (Número de Cajas × KG por Caja) + KG Extra.

**P: ¿Puedo vender a un cliente que no está en la lista?**  
R: No, primero debe solicitar al administrador que agregue al cliente al sistema. Esto asegura que todos los clientes estén debidamente registrados.

**P: ¿Qué significa el ID de venta (ejemplo: SALE-20260108-001)?**  
R: Es un identificador único. El formato es: SALE-AAAAMMDD-XXX, donde AAAA es el año, MM el mes, DD el día, y XXX es un número secuencial del día.

### Sobre Inventario

**P: ¿Cómo agrego inventario inicial al sistema?**  
R: Use "Nuevo Movimiento" con tipo "Compra" e ingrese la cantidad inicial que tiene en stock.

**P: ¿Qué hago si el inventario del sistema no coincide con el físico?**  
R: Realice un conteo físico y regístrelo en "Inventario Físico". El sistema ajustará automáticamente el inventario al valor real que usted contó.

**P: ¿Puedo ver quién hizo cada movimiento de inventario?**  
R: Sí, en los registros de auditoría (menú Admin → Auditoría) puede ver todos los detalles de cada movimiento, incluyendo quién lo realizó y cuándo.

**P: ¿El inventario puede ser negativo?**  
R: Técnicamente sí, pero el sistema mostrará una alerta. Un inventario negativo indica que se vendió más de lo que había en stock, lo cual debe investigarse.

**P: ¿Con qué frecuencia debo hacer conteos físicos?**  
R: Se recomienda hacer conteos físicos al menos una vez por semana, o con mayor frecuencia si maneja grandes volúmenes.

### Sobre Reportes

**P: ¿Puedo exportar los reportes a Excel?**  
R: Sí, la mayoría de reportes tienen un botón "Exportar a Excel" que descarga los datos en formato .xlsx.

**P: ¿Los reportes incluyen ventas anuladas?**  
R: No, los reportes solo incluyen ventas con estado "Activo". Las ventas anuladas no se cuentan en las estadísticas.

**P: ¿Cómo veo las ventas de un mes específico?**  
R: Use el filtro de fechas y seleccione el primer día del mes como fecha inicio y el último día como fecha fin.

**P: ¿Los gráficos se actualizan en tiempo real?**  
R: Los gráficos muestran los datos al momento de generar el reporte. Para ver datos actualizados, regenere el reporte.

### Sobre el Sistema

**P: ¿Puedo acceder al sistema desde mi teléfono móvil?**  
R: Sí, el sistema tiene diseño responsive y funciona perfectamente en teléfonos y tablets.

**P: ¿Se hacen copias de seguridad automáticas?**  
R: Depende de la configuración del servidor. Consulte con su administrador de sistemas sobre la política de respaldos.

**P: ¿Qué navegador es mejor para usar el sistema?**  
R: Google Chrome o Microsoft Edge ofrecen la mejor experiencia. Firefox y Safari también funcionan bien.

**P: ¿Puedo usar el sistema sin conexión a Internet?**  
R: No, el sistema requiere conexión a Internet para funcionar, ya que los datos se almacenan en el servidor.

**P: ¿Cuántos usuarios pueden usar el sistema simultáneamente?**  
R: El sistema soporta múltiples usuarios simultáneos sin límite específico, dependiendo de la capacidad del servidor.

---

## Solución de Problemas

### Problemas Comunes y Soluciones

#### El sistema no carga o muestra página en blanco

**Posibles causas y soluciones:**

1. **Verificar conexión a Internet**
   - Asegúrese de que su dispositivo esté conectado a Internet
   - Intente abrir otros sitios web para confirmar

2. **Verificar la URL**
   - Confirme que está usando la dirección correcta del sistema
   - Verifique que no haya errores de escritura

3. **Limpiar caché del navegador**
   - Presione `Ctrl + F5` para recargar forzadamente
   - O vaya a Configuración → Privacidad → Borrar datos de navegación

4. **Probar con otro navegador**
   - Intente acceder desde Chrome, Firefox o Edge
   - Esto ayuda a identificar si es un problema del navegador

5. **Verificar que JavaScript esté habilitado**
   - El sistema requiere JavaScript para funcionar
   - Revise la configuración de su navegador

#### Error al crear o guardar una venta

**Mensaje de error al intentar guardar:**

1. **Verificar campos obligatorios**
   - Asegúrese de haber seleccionado un cliente
   - Verifique que haya al menos un producto agregado
   - Confirme que las cantidades sean números válidos

2. **Problema con crédito**
   - Si seleccionó "Crédito" y aparece error, el cliente probablemente no tiene crédito habilitado
   - Cambie a "Efectivo" o contacte al administrador

3. **Problema con especificaciones**
   - Si una especificación no aparece, puede estar desactivada
   - Contacte al administrador para reactivarla

4. **Inventario insuficiente**
   - Si el error menciona inventario, no hay suficiente stock
   - Verifique el inventario actual antes de vender

#### El inventario muestra un valor incorrecto

**El stock no coincide con la realidad:**

1. **Realizar conteo físico**
   - Cuente físicamente toda la mercancía
   - Registre el resultado en "Inventario Físico"
   - El sistema se ajustará automáticamente

2. **Revisar movimientos recientes**
   - Vaya a "Inventario" → "Movimientos"
   - Verifique que todos los movimientos sean correctos
   - Busque movimientos duplicados o erróneos

3. **Verificar ventas anuladas**
   - Las ventas anuladas devuelven el inventario
   - Confirme que las anulaciones sean correctas

4. **Contactar al administrador**
   - Si el problema persiste, puede haber un error en el sistema
   - El administrador puede revisar los logs de auditoría

#### No puedo ver ciertos menús o funciones

**Menús o botones no aparecen:**

**Causa**: Permisos de usuario insuficientes

**Solución**:
- Contacte al administrador del sistema
- Verifique su rol de usuario
- Algunas funciones (como Administración) requieren rol de Administrador
- El administrador puede actualizar sus permisos si es necesario

#### Los gráficos no se muestran

**Los reportes no muestran gráficos:**

1. **Verificar JavaScript**
   - Asegúrese de que JavaScript esté habilitado
   - Los gráficos requieren JavaScript para renderizarse

2. **Actualizar la página**
   - Presione F5 para recargar
   - A veces los gráficos tardan en cargar

3. **Verificar que haya datos**
   - Si no hay datos en el período seleccionado, no habrá gráfico
   - Intente con un rango de fechas diferente

4. **Probar con otro navegador**
   - Algunos navegadores antiguos pueden tener problemas
   - Use Chrome o Edge para mejor compatibilidad

#### La sesión se cierra sola

**El sistema pide iniciar sesión frecuentemente:**

**Causa**: Tiempo de inactividad

**Solución**:
- El sistema cierra sesión automáticamente después de cierto tiempo de inactividad (por seguridad)
- Simplemente vuelva a iniciar sesión
- Si trabaja con el sistema constantemente, la sesión se mantendrá activa

#### Mensajes de error comunes

| Error | Causa | Solución |
|-------|-------|----------|
| "Cliente no encontrado" | ID de cliente inválido | Seleccione un cliente válido de la lista |
| "Especificación no encontrada" | Especificación desactivada | Seleccione otra especificación activa |
| "Crédito no permitido para este cliente" | Cliente sin crédito habilitado | Use "Efectivo" o pida al admin habilitar crédito |
| "Inventario insuficiente" | Stock bajo | Agregue inventario antes de vender |
| "Sesión expirada" | Tiempo de inactividad excedido | Inicie sesión nuevamente |
| "Acceso denegado" | Permisos insuficientes | Contacte al administrador |

### Obtener Ayuda Adicional

Si el problema persiste después de intentar las soluciones anteriores:

#### 1. Revisar los Logs del Sistema

Si es administrador:
- Vaya a Admin → Auditoría
- Busque errores o eventos inusuales en las fechas relevantes
- Los logs pueden dar pistas sobre qué salió mal

#### 2. Tomar Capturas de Pantalla

Antes de contactar soporte:
- Tome una captura de pantalla del error
- Anote exactamente qué estaba haciendo cuando ocurrió
- Documente los pasos para reproducir el problema

#### 3. Contactar al Soporte Técnico

Proporcione la siguiente información:
- Descripción detallada del problema
- Capturas de pantalla
- Pasos para reproducir el error
- Navegador y sistema operativo que usa
- Fecha y hora aproximada del problema

#### 4. Documentación Técnica

Para información más técnica, consulte:
- `README.md` - Información general del proyecto
- `DATABASE_DESIGN.md` - Estructura de la base de datos
- `PROJECT_SUMMARY.md` - Resumen técnico completo

---

## Apéndices

### A. Glosario de Términos

**Especificación**: Tipo de producto con un peso definido por caja. Ejemplo: "20 KG", "JAVA 39x110".

**KG Extra**: Producto suelto vendido fuera de cajas completas. También llamado "producto suelto".

**Anular**: Cancelar una venta sin eliminar el registro del sistema. La venta anulada permanece visible pero no cuenta en estadísticas.

**Auditoría**: Registro automático de todos los cambios importantes en el sistema. Permite rastrear quién hizo qué y cuándo.

**Inventario Teórico**: Stock calculado por el sistema según los movimientos registrados (compras - ventas + ajustes).

**Inventario Real**: Stock contado físicamente en el almacén o bodega.

**Diferencia de Inventario**: Discrepancia entre el inventario teórico y el real. Puede ser positiva (hay más) o negativa (hay menos).

**Ticket Promedio**: Peso promedio por orden de venta. Se calcula dividiendo el total vendido entre el número de órdenes.

**Estado Activo**: Registro válido y vigente que cuenta en estadísticas.

**Estado Anulado**: Registro cancelado que no cuenta en estadísticas pero permanece visible.

**Rol de Usuario**: Nivel de permisos asignado a un usuario (Operador o Administrador).

**Crédito Habilitado**: Permiso para que un cliente pueda comprar con pago diferido.

### B. Atajos de Teclado

| Atajo | Acción |
|-------|--------|
| `Ctrl + N` | Nueva venta (cuando está en la página de ventas) |
| `Ctrl + S` | Guardar formulario actual |
| `Esc` | Cerrar ventana emergente o diálogo |
| `F5` | Actualizar página |
| `Ctrl + F5` | Actualizar página ignorando caché |
| `Ctrl + P` | Imprimir página actual |

### C. Convenciones de Nomenclatura

**IDs de Venta**
- Formato: `SALE-AAAAMMDD-XXX`
- Ejemplo: `SALE-20260108-001`
- AAAA = Año (2026)
- MM = Mes (01)
- DD = Día (08)
- XXX = Número secuencial del día (001, 002, 003...)

**Interpretación**: La venta `SALE-20260108-001` es la primera venta del 8 de enero de 2026.

### D. Límites y Capacidades del Sistema

| Concepto | Límite |
|----------|--------|
| Productos por venta | Sin límite |
| Ventas por día | Sin límite |
| Clientes registrados | Sin límite |
| Especificaciones activas | Sin límite |
| Tamaño de archivo de exportación | 10 MB |
| Período máximo de reportes | 1 año |
| Retención de logs de auditoría | Indefinida |
| Usuarios simultáneos | Depende del servidor |

### E. Mejores Prácticas

**Para Operadores:**
1. Verifique siempre los datos antes de guardar una venta
2. Use notas descriptivas en movimientos de inventario
3. Realice conteos físicos regularmente
4. Revise el resumen del día antes de cerrar
5. Anote el motivo claramente al anular ventas

**Para Administradores:**
1. Revise los logs de auditoría semanalmente
2. Mantenga actualizada la lista de especificaciones
3. Verifique los permisos de crédito de clientes regularmente
4. Realice respaldos de la base de datos frecuentemente
5. Capacite a los operadores en el uso correcto del sistema

**Para Todos:**
1. Use contraseñas seguras
2. Cierre sesión al terminar de usar el sistema
3. No comparta sus credenciales
4. Reporte problemas inmediatamente
5. Mantenga su navegador actualizado

---

## Contacto y Soporte

**Operador del Sistema**: Jose Burgueno  
**Versión del Sistema**: 1.0.0  
**Última Actualización del Manual**: Enero 2026

Para soporte técnico, consultas o sugerencias, contacte al administrador del sistema.

---

**© 2026 Sistema de Gestión de Ventas. Todos los derechos reservados.**

Este manual es propiedad del sistema y está destinado exclusivamente para uso interno. Queda prohibida su reproducción total o parcial sin autorización.
