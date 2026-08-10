import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_plan_risk_3d.settings')
django.setup()

from users.models import Usuario, PlanConfig
from plans.models import Plan3DJob
from presupuesto.models import CategoriaMaterial, Material

def seed():
    print("Iniciando sembrado de base de datos...")
    
    # 1. Asegurar PlanConfig
    plans_data = [
        {"nombre": "Plan Free", "precio": 0.00, "limite_planos": "3 planos/mes", "soporte": "Básico"},
        {"nombre": "Plan Estrella", "precio": 150.00, "limite_planos": "25 planos/mes", "soporte": "Detección IA Mask R-CNN"},
        {"nombre": "Plan Premium", "precio": 350.00, "limite_planos": "Ilimitado", "soporte": "IA + Blockchain + n8n"}
    ]
    for p in plans_data:
        PlanConfig.objects.get_or_create(
            nombre=p["nombre"],
            defaults={
                "precio": p["precio"],
                "limite_planos": p["limite_planos"],
                "soporte": p["soporte"]
            }
        )
    print("PlanConfig verificado.")

    # 2. CategoriaMaterial y Materiales
    cats = ["Hormigón", "Acero", "Ladrillos", "Madera", "Instalaciones"]
    cat_objs = []
    for c in cats:
        obj, _ = CategoriaMaterial.objects.get_or_create(nombre=c, defaults={"descripcion": f"Materiales del área de {c}"})
        cat_objs.append(obj)
    
    mats_data = [
        ("Cemento Portland IP-40", "bolsas", 55.50),
        ("Fierro Corrugado de 1/2", "kg", 8.20),
        ("Hormigón Premezclado H-25", "m3", 680.00),
        ("Ladrillo Gambote 6 Huecos", "millar", 1200.00),
        ("Piedra Manzana", "m3", 180.00),
        ("Arena Fina", "m3", 120.00),
        ("Madera de Construcción", "pie2", 15.00)
    ]
    for name, unit, price in mats_data:
        Material.objects.get_or_create(
            nombre=name,
            defaults={
                "categoria": random.choice(cat_objs),
                "unidad": unit,
                "precio_unitario": price
            }
        )
    print("Categorías y materiales verificados.")

    # 3. Crear 2000 Clientes (usuarios sin rol de Administrador)
    print("Generando 2000 usuarios clientes en bulk...")
    hashed_password = make_password("12345678")
    user_instances = []
    
    nombres = ["Juan", "Maria", "Carlos", "Ana", "Luis", "Elena", "Pedro", "Sofia", "Jorge", "Lucia", "Roberto", "Laura", "Jose", "Carmen", "Miguel", "Andrea"]
    apellidos = ["Perez", "Garcia", "Mendoza", "Beltran", "Flores", "Gomez", "Choque", "Calle", "Rodriguez", "Torrez", "Aguilar", "Mamani", "Vargas", "Quispe", "Pinto", "Silva"]
    roles = ["usuario_normal", "usuario_premium", "usuario_estrella"]
    profesiones = ["estudiante", "profesional", "otro"]
    
    existing_emails = set(Usuario.objects.values_list('email', flat=True))
    
    for i in range(1, 2001):
        email = f"cliente{i}@planrisk3d.com"
        if email in existing_emails:
            continue
        
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        rol = random.choice(roles)
        profesion = random.choice(profesiones)
        
        # Fecha de nacimiento aleatoria (entre 20 y 50 años atrás)
        years_ago = random.randint(20, 50)
        birth_date = datetime.now().date() - timedelta(days=years_ago*365 + random.randint(0, 365))
        
        user_instances.append(
            Usuario(
                nombre=nombre,
                apellido=apellido,
                email=email,
                password=hashed_password,
                rol=rol,
                profesion=profesion,
                fecha_nacimiento=birth_date,
                fecha_expiracion_plan=datetime.now().date() + timedelta(days=30) if rol != "usuario_normal" else None,
                fecha_registro=timezone.now() - timedelta(days=random.randint(1, 100)),
                telefono=random.randint(70000000, 79999999),
                acepta_politicas=True,
                fecha_aceptacion=timezone.now()
            )
        )
        
    if user_instances:
        Usuario.objects.bulk_create(user_instances)
        print(f"Creados {len(user_instances)} usuarios clientes.")
    else:
        print("Los usuarios clientes ya existen.")

    # 4. Crear 2000 trabajos de planos (Plan3DJob) para los usuarios clientes
    print("Generando 2000 trabajos (Plan3DJobs) en bulk...")
    client_users = list(Usuario.objects.exclude(rol="Administrador"))
    if not client_users:
        print("No se encontraron usuarios clientes para asociar los trabajos.")
        return
        
    job_instances = []
    glb_url = "https://defensasw2.jorgechoquecalle.engineer/media/outputs/job_1_1786320401.glb"
    
    for i in range(1, 2001):
        user = random.choice(client_users)
        created_at = timezone.now() - timedelta(days=random.randint(1, 90), hours=random.randint(0, 23))
        
        job_instances.append(
            Plan3DJob(
                plan_file="media/inputs/default_plan.png",
                plan_image="media/inputs/default_plan.png",
                detections_json="media/outputs/default_detections.json",
                glb_model=glb_url,
                created_at=created_at,
                width=random.choice([800, 1024, 1280]),
                height=random.choice([600, 768, 960]),
                usuario=user
            )
        )
        
    Plan3DJob.objects.bulk_create(job_instances)
    print(f"Creados {len(job_instances)} trabajos Plan3DJobs.")
    print("¡Sembrado completado con éxito!")

if __name__ == "__main__":
    seed()
