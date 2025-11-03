# SPDX-FileCopyrightText: 2025-present Harry Kodden
# SPDX-License-Identifier: Apache-2.0

# Generated migration

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="OIDCUserProfile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "oidc_id",
                    models.CharField(
                        help_text="The unique identifier from the OIDC provider",
                        max_length=255,
                        unique=True,
                        verbose_name="OIDC ID",
                    ),
                ),
                (
                    "provider",
                    models.CharField(
                        default="oidc", max_length=100, verbose_name="OIDC Provider"
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="oidc_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "OIDC User Profile",
                "verbose_name_plural": "OIDC User Profiles",
            },
        ),
    ]
