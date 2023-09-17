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
            "command": ">> Enter Command: ",
            "name": ">> Please Enter Employee Name: ",
            "age": ">> Please Enter Employee Age: ",
            "department": ">> Please Enter Employee Department: ",
            "exit":">> Exiting Program........",
            "serverError": ">> Internal Server Error: Please try again later",
            "DeleteWarning": ">> Are you sure you want to delete user? press N/n to cancel delete: "
        }

    def commnad_to_function_map(self,command):
        if not command:
            return
        
        command = command if command in self.command_mappings else "invalid_command"
        mapper_function = self.command_mappings[command]
        mapper_function()

    def invalid_command(self):
        self.stdout.write("Invalid command, Please enter command help to know more")

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

        new_employee = {
            "name":name,
            "age":age,
            "department":department
            }
        self.Employees.append(new_employee)

        try:
            Employee.objects.create(name=name,age=age,department=department)
        except Exception:
            self.stdout.write(self.style.HTTP_SERVER_ERROR(self.prompts["serverError"]))
        
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
           self.stdout.write(table+"\n")
       else:
           self.stdout.write(self.style.MIGRATE_HEADING("No Data to Display!")) 

    def show(self):
        name = self.validation.take_input(prompt=self.prompts["name"])
        try:
            employee = Employee.objects.filter(name=name).first()
            employee_data = [] if not employee else [(employee.name,employee.age,employee.department)]
        except Exception:
            self.stdout.write(self.style.ERROR(self.prompts["serverError"]))
            return
        self.tabulate_data(data=employee_data,headers=self.EmployeeHeaders)

    def delete(self):
        name = self.validation.take_input(prompt=self.prompts["name"])
        try:
            user = Employee.objects.filter(name=name).first()
            if user:
                input_ = input(self.style.WARNING(self.prompts["DeleteWarning"])).strip()
                if input_ in ["n","N"]:
                    self.stdout.write(self.style.NOTICE("Delete operation cancel"))
                    return
                else:
                    if user: user.delete()
        except Exception:
            self.stdout.write(self.style.ERROR(self.prompts["serverError"]))
        self.stdout.write(self.style.NOTICE(f"User {name} Deleted Successfully"))

    def list(self):
        try:
            employee_list = list(Employee.objects.all())
            employee_data = [(emp.name,emp.age,emp.department) for emp in employee_list]
        except Exception:
            self.stdout.write(self.style.ERROR(self.prompts["serverError"]))
            return
        self.tabulate_data(data=employee_data,headers=self.EmployeeHeaders)

    def exit(self):
        self.stdout.write(self.style.WARNING(self.prompts["exit"]))
        time.sleep(1.5)
        sys.exit(0)




        