from django.db import models

# Create your models here.

class Vendor(models.Model):
    fname = models.CharField(max_length=255, blank=False, null=False)
    lname = models.CharField(max_length=255, blank=False, null=False)
    username = models.CharField(max_length=150, unique=True, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    phone = models.CharField(max_length=15, unique=True, blank=False, null=False)
    password = models.CharField(max_length=128, blank=False, null=False)

    def __str__(self):
        return f"{self.fname} {self.lname}"

class Diamond(models.Model):
    
    TYPES = [
        ('CVD', 'CVD'),
        ('HPHT', 'HPHT'),
    ]
        
    LAB = [
        ('IGI', 'IGI'),
        ('GIA', 'GIA'),
    ]

    SHAPE = [
        ('RD', 'ROUND'),
        ('PR', 'PEAR'),
        ('OVL', 'OVAL'),
        ('RDNT', 'RADIANT'),
        ('EM', 'EMERALD'),
        ('SQ', 'SQUARE'),
        ('MQ', 'MARQUISE'),
        ('HT', 'HEART'),
        ('PRS', 'PRINCESS'),
        ('AS', 'ASSCHER'),
        ('CS', 'CUSHION'),
        ('OLD', 'OLD'),
        ('OT', 'OTHER')
    ]

    COLOUR = [
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
        ('G', 'G'),
        ('H', 'H'),
        ('I', 'I'),
        ('J', 'J'),
        ('FB', 'FANCY BLUE'),
        ('FIB', 'FANCY INTENSE BLUE'),
        ('LB', 'LIGHT BLUE'),
        ('FP', 'FANCY PINK'),
        ('FIP', 'FANCY INTENSE PINK'),
        ('LP', 'LIGHT PINK'),
    ]
  
    CLARITY = [
        ('FL', 'FL'),
        ('IF', 'IF'),   
        ('VVS1', 'VVS1'),
        ('VVS2', 'VVS2'),
        ('VS1', 'VS1'),
        ('VS2', 'VS2'),
        ('SI1', 'SI1'),
        ('SI2', 'SI2'),
        ('SI3', 'SI3'),
        ('I1', 'I1'),
        ('I2', 'I2'),
        ('I3', 'I3'),
    ]

    CUT = [
        ('ID', 'IDEAL'),
        ('EX', 'EXCELLENT'),
        ('VG', 'VERY GOOD'), 
        ('GD', 'GOOD'),
        ('FR', 'FAIR'),
    ]
    

    POLISH = [
        ('ID', 'IDEAL'), 
        ('EX', 'EXCELLENT'),
        ('VG', 'VERY GOOD'),
        ('GD', 'GOOD'),
        ('FR', 'FAIR'),
    ]
    
    
    SYMMETRY = [
        ('ID', 'IDEAL'),
        ('EX', 'EXCELLENT'),
        ('VG', 'VERY GOOD'),
        ('GD', 'GOOD'),
        ('FR', 'FAIR'),
    ]
    
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='diamonds')
    type = models.CharField(max_length=50, blank=False, null=False, choices=TYPES)
    stock_id = models.CharField(max_length=100, unique=True, blank=False, null=False)
    report_number = models.BigIntegerField(unique=True, blank=False, null=False)
    lab = models.CharField(max_length=50, blank=False, null=False, choices=LAB)
    shape = models.CharField(max_length=50, blank=False, null=False, choices=SHAPE)
    carat = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    color = models.CharField(max_length=10, blank=False, null=False, choices=COLOUR)
    clarity = models.CharField(max_length=10, blank=False, null=False, choices=CLARITY)
    rap_rate = models.IntegerField(blank=False, null=False)
    discount_percentage = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False)
    price_per_carat = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=False, null=False)
    cut = models.CharField(max_length=20, blank=False, null=False, choices=CUT)
    polish = models.CharField(max_length=20, blank=False, null=False, choices=POLISH)
    symmetry = models.CharField(max_length=20, blank=False, null=False, choices=SYMMETRY)
    fluorescence = models.CharField(max_length=20, blank=False, null=False)
    length = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False)
    width = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False)
    height = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False)
    measurements = models.CharField(max_length=100, blank=False, null=False)
    table_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)
    depth_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)
    crown_angle = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)
    crown_height_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)
    pavilion_angle = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)
    pavilion_depth = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)
    video_360 = models.URLField(blank=True, null=True)
    photo = models.URLField(blank=True, null=True)
    pdf = models.URLField(blank=True, null=True)
    ratio = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)
    bgm = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # calculation for price_per_carat and total_amount
        self.price_per_carat = self.rap_rate - (self.rap_rate * self.discount_percentage / 100) 
        self.total_amount = self.carat * self.price_per_carat
        # calculation of measurements
        self.measurements = f"{self.width} x {self.length} x {self.height}"
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.stock_id} - {self.vendor.username}"