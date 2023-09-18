from django.core.management.base import BaseCommand
from tabulate import tabulate
import json
import os
import sys
import time
from ...utilities.EmployeeValidations import EmployeeValidation
from ...models import Employee

class Command(BaseCommand):
    help = 'Display hello'
    Employees = []
    EmployeeHeaders = ["Name","Age","Department"]
    CommandHeaders = ["Command","Description"]
    validation = EmployeeValidation()
    
    def initialise_metadata(self):
        self.command_mappings = {
            "add":self.add,
            "show":self.show,
            "list":self.list,
            "clear":self.clear,
            "invalid_command":self.invalid_command,
            "exit":self.exit,
            "help":self.help,
            "delete":self.delete
        }

        self.prompts = {
            "command": ">> (Use 'help' command to know more)\n>> Enter Command: ",
            "name": ">> Please Enter Employee Name: ",
            "age": ">> Please Enter Employee Age: ",
            "department": ">> Please Enter Employee Department: ",
            "exit":">> Exiting Program........",
            "serverError": ">> Internal Server Error: Please try again later",
            "deleteWarning": ">> Are you sure you want to delete user? press N/n to cancel delete: ",
            "addWarning": ">> Are you sure want to add user? press N/n to cancel add: "
        }

    def commnad_to_function_map(self,command):
        if not command:
            return
        
        command = command if command in self.command_mappings else "invalid_command"
        mapper_function = self.command_mappings[command]
        mapper_function()

    def invalid_command(self):
        self.stdout.write("Invalid command, use command 'help' to know more")

    def handle(self,*args,**kwargs):
        file_path = "core/management/commands/welcome_text.txt"
        
        try:
            with open(file_path, 'r') as file:
                welcome_text = file.read()
        except Exception:
            welcome_text = ">> Welcome to Employee Management App\n>> Use help command to know more"
            

        self.initialise_metadata()        
        self.stdout.write(self.style.MIGRATE_LABEL(welcome_text))
        
        while True:
            command = self.validation.take_input(prompt=self.prompts["command"])
            self.commnad_to_function_map(command)

    def add(self):
        name = self.validation.take_input(prompt=self.prompts["name"],argument_name="name")
        age = self.validation.take_input(prompt=self.prompts["age"], argument_name="age")
        department = self.validation.take_input(self.prompts["department"],argument_name="department")

        # Adding Employee to the database
        try:
            input = self.validation.take_input(self.style.WARNING(self.prompts["addWarning"]))
            if input in ["n","N"]:
                self.stdout.write(self.style.NOTICE("Add Operation Canceled"))
                return
            else:
                Employee.objects.create(name=name,age=age,department=department)
        except Exception as e:
            self.stdout.write(self.style.ERROR(self.validation.initiate_internal_server_error(e,return_error=True)))
        
        self.stdout.write(self.style.SUCCESS(f"Employee {name} added Successfully!\n"))

    def help(self):
        commandFile = "core\management\commands\commands.json"
        with open(commandFile, "r") as json_file:
            # Use json.load() to parse the JSON data into a Python object
            data = json.load(json_file)
        
        commandList = [(cmd["command"],cmd["description"]) for cmd in data]
        headers = self.CommandHeaders
        table = tabulate(commandList,headers=headers,tablefmt="grid")

        self.stdout.write(table)

    def clear(self):
        if os.name == 'nt':  # Check if the OS is Windows
            os.system('cls')
        else:
           os.system('clear')
    
    def tabulate_data(self,data,headers):
       if data:
           table = tabulate(data,headers,tablefmt="grid")
           self.clear()
           self.stdout.write("\n"+"\n"+table+"\n"+"\n")
       else:
           self.stdout.write(self.style.MIGRATE_HEADING("No Data to Display!")) 

    def show(self):
        name = self.validation.take_input(prompt=self.prompts["name"])
        try:
            employee = Employee.objects.filter(name=name).first()
            
            if not employee:
                space = "" if name else ""
                self.stdout.write(self.style.WARNING(f"User {name}{space}Not Found!"))
                return
            employee_data = [] if not employee else [(employee.name,employee.age,employee.department)]
        except Exception:
            self.stdout.write(self.style.ERROR(self.prompts["serverError"]))
            return
        self.tabulate_data(data=employee_data,headers=self.EmployeeHeaders)

    def delete(self):
        name = self.validation.take_input(prompt="Please Enter name of employee you want to delete: ",argument_name="empty_input")
        try:
            user = Employee.objects.filter(name=name).first()
            if user:
                input_ = input(self.style.WARNING(self.prompts["deleteWarning"])).strip()
                if input_ in ["n","N"]:
                    self.stdout.write(self.style.NOTICE("Delete operation cancel"))
                    return
                else:
                    if user: 
                        user.delete()
                        self.stdout.write(self.style.NOTICE(f"User {name} Deleted Successfully"))
            
            else:
                self.stdout.write(self.style.NOTICE(f"User {name} Not Found you can use list command to check employee exists or not"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(self.validation.initiate_internal_server_error(e,return_error=True)))
        
    def list(self):
        try:
            employee_list = list(Employee.objects.all())
            employee_data = [(emp.name,emp.age,emp.department) for emp in employee_list]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"{self.prompts['serverError']}: {str(e)}"))
            return
        self.tabulate_data(data=employee_data,headers=self.EmployeeHeaders)

    def exit(self):
        self.stdout.write(self.style.WARNING(self.prompts["exit"]))
        time.sleep(0.5)
        sys.exit(0)




        