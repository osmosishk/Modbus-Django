from django.db import models

# Create your models here.
class Slaves(models.Model):
    IDSlaves = models.CharField(max_length=100)
    Name = models.CharField(max_length=100)
    Enable = models.BooleanField(default=True)
    MAC = models.CharField(max_length=50)

    def __str__(self):
        return self.Name

class Setting(models.Model):
    CHOICES = (
    ('E', 'Even'), ('N', 'None'), ('O', 'Odd'),(0, 'default'))
    Baud = (
        ('9600', '9600'), ('19200', '19200'), ('38400', '38400'))
    Slaves = models.ForeignKey('Slaves',on_delete=models.CASCADE)
    Slaveaddres =models.IntegerField(default=4)
    Baudrate =models.CharField(max_length=10, choices=Baud ,blank=False)
    Parity =  models.CharField(max_length=5, choices=CHOICES ,blank=False)
    Stop = models.PositiveSmallIntegerField(default=1)
    Bits = models.PositiveSmallIntegerField(default=8)

    def __str__(self):
        return self.Slaves.Name

class Address(models.Model):
    value_class_choices = (('FLOAT32', 'REAL (FLOAT32)'),
                           ('FLOAT32', 'SINGLE (FLOAT32)'),
                           ('FLOAT32', 'FLOAT32'),
                           ('UNIXTIMEF32', 'UNIXTIMEF32'),
                           ('FLOAT64', 'LREAL (FLOAT64)'),
                           ('FLOAT64', 'FLOAT  (FLOAT64)'),
                           ('FLOAT64', 'DOUBLE (FLOAT64)'),
                           ('FLOAT64', 'FLOAT64'),
                           ('UNIXTIMEF64', 'UNIXTIMEF64'),
                           ('INT64', 'INT64'),
                           ('UINT64', 'UINT64'),
                           ('UNIXTIMEI64', 'UNIXTIMEI64'),
                           ('UNIXTIMEI32', 'UNIXTIMEI32'),
                           ('INT32', 'INT32'),
                           ('UINT32', 'DWORD (UINT32)'),
                           ('UINT32', 'UINT32'),
                           ('INT16', 'INT (INT16)'),
                           ('INT16', 'INT16'),
                           ('UINT16', 'WORD (UINT16)'),
                           ('UINT16', 'UINT (UINT16)'),
                           ('UINT16', 'UINT16'),
                           ('BOOLEAN', 'BOOL (BOOLEAN)'),
                           ('BOOLEAN', 'BOOLEAN'),
                           ('STRING', 'STRING'),
                           )
    IDAddress = models.AutoField(primary_key=True)
    Slaves = models.ForeignKey('Slaves', on_delete=models.CASCADE)
    Address = models.CharField(max_length=50,blank=False)
    Name = models.CharField(max_length=200, blank=False)
    Unit = models.CharField(max_length=50, blank=False)
    value_class = models.CharField(max_length=15, default='INT16', verbose_name="value_class",
                                   choices=value_class_choices)

    def __str__(self):
        return self.Name



