
from Medical.users.medicine import medicine

class MedicineRepository:


    @staticmethod
    def get_all():
        return medicine.Medicine.objects.all()
    


    @staticmethod
    def get_by_if(medicine_id):
        return medicine.Medicine.objects.filter(id == medicine_id).first()
    

    @staticmethod
    def create( **kwargs):
        return medicine.Medicine.objects.create(**kwargs)
    

