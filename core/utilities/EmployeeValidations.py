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
            "user_is_unique":self.validate_user_is_unique,
            "empty_input":self.validate_empty_input,
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

    # default validation is called even if there is no validation is passed in take_input method
    def default_validation(self,input):
        self.validation_obj.refresh()
        input = input.strip()
        self.validation_obj.input = input
        return self.validation_obj
     
    # validation fails if user exists
    def validate_user_is_unique(self,name):
        self.default_validation(name)
        try:
            if Employee.objects.filter(name=name).exists():
                self.validation_obj.status = False
                self.validation_obj.error_msg = f"user {name} already exists in Database please try with diffrent name"
                self.validation_obj.input = name
            return self.validation_obj
        except Exception as e:
            return self.initiate_internal_server_error(e)    
    
    def validate_length(self,input,min,max):
        self.default_validation(input)
        input = self.validation_obj.input

        if len(input)<min or len(input)>max:
            self.validation_obj.status = False
            self.validation_obj.error_msg = f"Input length must be in the range of {str(min)} and {str(max)}"
        
        #self.validation_obj = input
        return self.validation_obj
    
    def validate_name(self,name):
        self.default_validation(name)
        invalid_symbols = ["!","@","#","$","%","^","*","(",")","-","+","[","]","~",",","'",'"']
        invalid_digits = [str(i) for i in range(10)]
 
        # checks for invalid symbol or digit
        # validation 1
        constains_symbol = any(symbol in name for symbol in invalid_symbols)
        constains_digit = any(digit in name for digit in invalid_digits)
        if constains_digit or constains_symbol:
            self.validation_obj.status=False
            self.validation_obj.error_msg = "Name can not have a digit or symbol in it"
            return self.validation_obj
        
        # checks for empty input
        # validation 2
        self.validate_empty_input(input=name,input_name="Name")
        if not self.validation_obj.status:
            return self.validation_obj
        
        # checks if name is already availabel in database
        # validation 3
        try:
            self.validate_user_is_unique(name)
            if not self.validation_obj:
                return self.validation_obj
        except Exception as e:
            return self.initiate_internal_server_error(e)
        
        return self.validation_obj

    def validate_age(self,age):
        self.default_validation(age)
        
        self.validate_empty_input(input=age,input_name="Age")
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
        
    def validate_department(self,department):
        self.default_validation(department)
        
        self.validate_empty_input(input=department,input_name="Department")
        if not self.validation_obj.status:
            return self.validation_obj
        
        # checking length
        self.validate_length(min=1,max=40,input=department)
        if not self.validation_obj.status:
            return self.validation_obj
        
        self.validation_obj.input = department
        return self.validation_obj

    def validate_empty_input(self,input,input_name=""):
        self.default_validation(input)
        input_name = input_name if input_name else "Input"
        if not input:
            self.validation_obj.error_msg = f"{input_name} can not be empty"
            self.validation_obj.status = False
        return self.validation_obj

    # These method intitate internal server error 
    # if return_error is true then it directly returns error if not then it returns validation object
    # these is beneficial in case if we want to directly return error outside of the class
    # hence it is a reusable function
    def initiate_internal_server_error(self,e,return_error=False):
        self.validation_obj.error_msg = f"Internal Server Error, Please try again later: {str(e)}"
        self.validation_obj.status = False
        
        return self.validation_obj.error_msg if return_error else self.validation_obj
