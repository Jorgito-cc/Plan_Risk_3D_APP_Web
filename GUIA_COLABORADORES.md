# 🚀 Guia de Instalacion para Colaboradores (Backend y Modelo IA)

Este documento contiene los pasos detallados para poder clonar el repositorio, configurar el entorno y hacer funcionar el servidor backend junto con el modelo de Inteligencia Artificial (Mask R-CNN) correctamente.

---

## 1. Clonar el Repositorio

Abre tu terminal y ejecuta:

```bash
git clone https://github.com/Jorgito-cc/Plan_Risk_3D_APP_Web.git
cd Plan_Risk_3D_APP_Web/back_plan_risk_3d
```

## 2. Crear y Activar el Entorno Virtual (Conda)

Como el proyecto requiere librerias especificas de procesamiento de imagenes, Inteligencia Artificial y Tensorflow, es obligatorio el uso de Conda. Ejecuta:

```bash
conda env create -f environment_full.yml
conda activate imageTo3D
```

*(Opcional: Si el entorno marca errores por alguna dependencia faltante, asegurate de correr `pip install -r requirements.txt`)*

## 3. Instalar la libreria de Autenticacion (JWT)

Asegurate de tener instalada la libreria que maneja los tokens de inicio de sesion:

```bash
pip install djangorestframework-simplejwt
```

## 4. ⚠️ PASO CRITICO: Descargar el modelo de IA (.h5)

Debido a que el modelo preentrenado de Inteligencia Artificial pesa **255 MB**, Git lo ignora automaticamente (`.gitignore`) para no saturar el repositorio. Debes descargarlo y colocarlo manualmente:

1. Crea una carpeta llamada `weights` justo dentro de la ruta `back_plan_risk_3d/`.
2. Descarga el archivo `maskrcnn_15_epochs.h5` desde nuestro Google Drive corporativo:
   - **[LINK_A_TU_GOOGLE_DRIVE]** *(Reemplazar con el enlace de descarga)*
3. Pega el archivo `.h5` dentro de la carpeta `weights/` que acabas de crear.

**Nota importante:** La ruta final del archivo debe quedar exactamente de esta manera:
`back_plan_risk_3d/weights/maskrcnn_15_epochs.h5`

## 5. Migrar la Base de Datos y Arrancar el Servidor

Una vez el archivo pesado de la IA este en su sitio correcto, sincroniza la base de datos y levanta el servidor:

```bash
python manage.py migrate
python manage.py runserver
```

Si todo se configuro correctamente, deberias ver en consola que el servidor esta corriendo en `http://127.0.0.1:8000/`.
