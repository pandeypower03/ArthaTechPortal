from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_seed_and_copy_roles"),
    ]

    operations = [
        migrations.RemoveField(model_name="user", name="role"),
    ]