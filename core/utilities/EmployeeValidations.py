from django.core.management.base import BaseCommand
from core.models import Employee

class ValidationObject:
    def __init__(self) -> None:
        self.status = True
        self.error_msg = ""
        self.input = ""

    @property
    def _status(self):
        return self.status

    @_status.setter
    def _status(self, value):
        if isinstance(value, bool):
            self.status = value
        else:
            raise ValueError("Status must be a boolean value.")

    @property
    def _input(self):
        return self.input

    @_input.setter
    def _input(self, value):
        if isinstance(value, str):
            self.input = value
        else:
            raise ValueError("Input must be a string value.")

    @property
    def _error_msg(self):
        return self.error_msg

    @_error_msg.setter
    def _error_msg(self, value):
        if isinstance(value, str):
            self.error_msg = value
        else:
            raise ValueError("Error message must be a string value.")
    def refresh(self):
        self._status = True
        self._error_msg = ""
        self._input = ""

class EmployeeValidation(BaseCommand):
    validation_obj = ValidationObject()
    
    def initialse_arguments(self):
        self.name_mapping_with_methods = {
            "name":self.validate_name,
            "age":self.validate_age,
            "department":self.validate_department,
            "default_validation":self.default_validation,
        }
    
    def take_input(self,prompt,argument_name=""):
        self.initialse_arguments()
        argument_name = argument_name if argument_name in self.name_mapping_with_methods else "default_validation"
        validation_function = self.name_mapping_with_methods[argument_name]
        
        while True:
            user_input = input(prompt)
            validation_obj = validation_function(user_input)
            if validation_obj.status:
                return validation_obj.input
            self.stdout.write(self.style.ERROR(validation_obj.error_msg))

    def default_validation(self,input):
        self.validation_obj.refresh()
        input = input.strip()
        self.validation_obj.input = input
        return self.validation_obj
     
    def check_user_exists(self,name):
        return bool(Employee.objects.filter(name=name).first())
    
    def validate_name(self,name):
        name = name.strip()
        self.validation_obj.refresh()
        
        # Check for empty input
        # if not name:
        #     self.validation_obj.error_msg = "Name can not be empty"
        #     self.validation_obj.status = False
        #     return self.validation_obj
        self.check_empty_input(input=name,input_name="Name")
        if not self.validation_obj.status:
            return self.validation_obj
        
        try:
            if self.check_user_exists(name):
                self.validation_obj.error_msg = f"name {name} exisits in database, You can try to change a spelling"
                self.validation_obj.status = False
                self.validation_obj.input = name
                return self.validation_obj
        
        except Exception:
            self.validation_obj.error_msg = "Internal Server Error, Please try after some time"
            self.validation_obj.status = False
            self.validation_obj.input = name
            return self.validation_obj
        
        
        self.validation_obj.input = name
        return self.validation_obj

    def validate_age(self,age):
        age=age.strip()
        self.validation_obj.refresh()
        
        # if not age:
        #     self.validation_obj.error_msg = "Age can not be empty"
        #     self.validation_obj.status = False
        #     return self.validation_obj
        
        self.check_empty_input(input=age,input_name="Age")
        if not self.validation_obj.status:
            return self.validation_obj
        
        
        if age[0] =="0":
            self.validation_obj.status = False
            self.validation_obj.error_msg = "Age can not start with 0"
            return self.validation_obj
        
        if age.count(" ") > 0:
            self.validation_obj.status = False
            self.validation_obj.error_msg = "Please Dont use spaces between"
            return self.validation_obj
        
        try:
            age = int(age)

        # Check for letters in input
        except ValueError:
            self.validation_obj.status=False
            self.validation_obj.error_msg = "Please Enter a Valid Age only in numbers"
            return self.validation_obj
        
        
        # checks valid age 
        if age<18 or age>50:
            self.validation_obj.status=False
            self.validation_obj.error_msg = "Valid Age range is between 18 and 50, Please enter valid age"
            return self.validation_obj
        
        self.validation_obj.input = str(age)
        return self.validation_obj
        
    def refresh_validation_obj(self):
        self.validation_obj.status = True
        self.validation_obj.error_msg = ""
        self.validation_obj.input = ""

    def validate_department(self,department):
        department = department.strip()
        self.validation_obj.refresh()
        
        # if not department:
        #     self.validation_obj.error_msg = "Department can not be empty, Please Enter Department"
        #     self.validation_obj.status = False
        #     return self.validation_obj
        
        self.check_empty_input(input=department,input_name="Department")
        if not self.validation_obj.status:
            return self.validation_obj
        
        
        self.validation_obj.input = department
        return self.validation_obj

    def check_empty_input(self,input,input_name):
        self.validation_obj.refresh()
        if not input:
            self.validation_obj.error_msg = f"{input_name} can not be empty"
            self.validation_obj.status = False
            return self.validation_obj

