from superuser_portal.models import Facility

facilities = [
    {"name": "Gymnasium", "capacity": 500, "description": "Main indoor gym."},
    {"name": "Covered Court", "capacity": 300, "description": "Outdoor covered court."},
    {"name": "Football Field", "capacity": 1000, "description": "Large outdoor field."},
    {"name": "Table Tennis Dug-out", "capacity": 50, "description": "Table tennis area."},
]

for fac in facilities:
    obj, created = Facility.objects.get_or_create(name=fac["name"], defaults={
        "capacity": fac["capacity"],
        "description": fac["description"]
    })
    if created:
        print(f"Created: {obj.name}")
    else:
        print(f"Already exists: {obj.name}")