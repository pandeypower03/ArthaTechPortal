from django.db import migrations


def seed_and_copy(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    User = apps.get_model("accounts", "User")

    roles = {}
    for name in ("super_admin", "admin", "normal_user"):
        roles[name], _ = Role.objects.get_or_create(name=name)

    for user in User.objects.all():
        user.roles.add(roles[user.role])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_role_alter_user_role_user_roles"),
    ]

    operations = [
        migrations.RunPython(seed_and_copy, migrations.RunPython.noop),
    ]