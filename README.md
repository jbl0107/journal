# Simple Journal API (Experimental)

Este proyecto es una API básica de **journal / bloc de notas** implementada en Python con **FastAPI**, **Pydantic** y **SQLAlchemy**.

FastAPI fue escogido por su rapidez, tipado fuerte con Pydantic y documentación automática de APIs. 

El objetivo principal ha sido **experimentar y aprender** sobre estas tecnologías, por lo que no sigue buenas prácticas ni principios de arquitectura completos.

---

## Descripción

El proyecto cuenta con dos entidades principales:

- **User**: Representa a un usuario de la aplicación.  
- **Note**: Representa una nota o entrada de diario asociada a un usuario.  

La base de datos utilizada es **PostgreSQL local**. La configuración de conexión se gestiona mediante un archivo `.env` ubicado en la raíz del proyecto.

---

## Configuración de la base de datos

1. Crea un archivo `.env` en la raíz del proyecto.  
   En este archivo deberás definir tus propias claves y credenciales de conexión a PostgreSQL.

2. Los nombres exactos de las variables necesarias se encuentran al inicio del archivo `db.py`.

3. Una vez configurado el entorno, puedes **ejecutar el archivo `db.py` como un módulo** para crear la base de datos e insertar datos de prueba:

   ```bash
   python -m db.py

4. Dentro de la función main() de db.py, encontrarás comentadas las llamadas a:
   - create_all()
   - insert_sample_data()
     
  Simplemente descoméntalas para crear las tablas e insertar los datos de ejemplo.

     
## Estado del proyecto
* Proyecto en desarrollo y experimental.
* Los repositorios pueden contener lógica de negocio, lo cual no es recomendable en proyectos de producción.
* No se han aplicado principios de arquitectura como Clean Architecture ni separación estricta de capas.
* Se han testeado todos los endpoints y operaciones CRUD utilizando PyTest y Mock.
* Existe un workflow de CI que se ejecuta en cada Pull Request a main, realizando setup y ejecución de tests automáticamente.

## Instalación
Instala todas las dependencias necesarias con:
```bash
pip install -r requirements.txt
```

## Uso
Levanta la aplicación localmente con:
```bash
fastapi dev main.py --reload
```
La API estará disponible en:
👉 http://127.0.0.1:8000

La documentación interactiva (Swagger/OpenAPI) estará en:
👉 http://127.0.0.1:8000/docs

*Nota*:
Este proyecto sirve como ejemplo de aprendizaje inicial con FastAPI y SQLAlchemy, no como modelo de arquitectura o buenas prácticas.
Fue desarrollado con el propósito de aprender sobre APIs, validación de datos, testing y CI/CD en Python.
