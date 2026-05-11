from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserAccountManager(BaseUserManager):
    def create_user(self, email, password = None):
        if not email or len(email) <= 0:
            raise ValueError("Email filed is required!")
        if not password:
            raise ValueError("Password id must be!")
        

        user  = self.model(
            email = self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using = self._db)
        return user
    


    def create_superusers(self, email, password):
        user = self.create_user(
            email = self.normalize_email(email),
            password=password
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using = self._db)
        return user




class UserAccount(AbstractBaseUser):
    class Types(models.TextChoices):
        CUSTOMER = "CUSTOMER", "customer"
        PHARMACIST = "PHARMACIST", "pharmacist"

    type = models.CharField(max_length=8, choices=Types.choices,
                            default= Types.CUSTOMER)

    email = models.EmailField(max_length=200, unique=True)
    is_active = models.BooleanField(default = True)
    is_admin = models.BooleanField(default = False)
    is_staff = models.BooleanField(default = False)
    is_superuser = models.BooleanField(default = False)



    is_customer = models.BooleanField(default = False)
    is_pharmacist = models.BooleanField(default = False)


    USERNAME_FIELD = "email"
    
    objects = UserAccountManager()
    
    def __str__(self):
        return str(self.email)
    
    def has_perm(self , perm, obj = None):
        return self.is_admin
    
    def has_module_perms(self , app_label):
        return True
    
    def save(self , *args , **kwargs):
        if not self.type or self.type == None : 
            self.type = UserAccount.Types.CUSTOMER
        return super().save(*args , **kwargs)
