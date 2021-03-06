# Generated by Django 3.0.8 on 2020-07-12 08:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('slaves', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setting',
            name='Bits',
            field=models.PositiveSmallIntegerField(default=8),
        ),
        migrations.AlterField(
            model_name='setting',
            name='Parity',
            field=models.CharField(choices=[('E', 'Even'), ('N', 'None'), ('O', 'Odd'), (0, 'default')], max_length=5),
        ),
        migrations.AlterField(
            model_name='setting',
            name='Stop',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('IDAddress', models.AutoField(primary_key=True, serialize=False)),
                ('Address', models.CharField(max_length=50)),
                ('Name', models.CharField(max_length=200)),
                ('Unit', models.CharField(max_length=50)),
                ('value_class', models.CharField(choices=[('FLOAT32', 'REAL (FLOAT32)'), ('FLOAT32', 'SINGLE (FLOAT32)'), ('FLOAT32', 'FLOAT32'), ('UNIXTIMEF32', 'UNIXTIMEF32'), ('FLOAT64', 'LREAL (FLOAT64)'), ('FLOAT64', 'FLOAT  (FLOAT64)'), ('FLOAT64', 'DOUBLE (FLOAT64)'), ('FLOAT64', 'FLOAT64'), ('UNIXTIMEF64', 'UNIXTIMEF64'), ('INT64', 'INT64'), ('UINT64', 'UINT64'), ('UNIXTIMEI64', 'UNIXTIMEI64'), ('UNIXTIMEI32', 'UNIXTIMEI32'), ('INT32', 'INT32'), ('UINT32', 'DWORD (UINT32)'), ('UINT32', 'UINT32'), ('INT16', 'INT (INT16)'), ('INT16', 'INT16'), ('UINT16', 'WORD (UINT16)'), ('UINT16', 'UINT (UINT16)'), ('UINT16', 'UINT16'), ('BOOLEAN', 'BOOL (BOOLEAN)'), ('BOOLEAN', 'BOOLEAN'), ('STRING', 'STRING')], default='INT16', max_length=15, verbose_name='value_class')),
                ('Slaves', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='slaves.Slaves')),
            ],
        ),
    ]
