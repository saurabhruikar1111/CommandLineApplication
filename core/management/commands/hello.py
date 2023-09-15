from django.core.management.base import BaseCommand
from tabulate import tabulate
import json

class Command(BaseCommand):
    help = 'Display hello'

    def handle(self,*args,**kwargs):
        self.Employees = []
        self.help_user()
        
        file_path = "core/management/commands/help_text.txt"
        with open(file_path, 'r') as file:
            help_text = file.read()
                
        self.stdout.write(self.style.NOTICE(help_text))
        
        while True:
            command = input(">>Enter a command: ").strip()
            if command == 'exit':
                break
            elif command == 'add':
                self.add_employee()
            elif command == 'list':
                self.list_employees()
            else:
                self.stdout.write("Invalid command. Available commands: add, remove, view, list, exit")

    def add_employee(self):
        name = input(">> Please Enter Name of Employee: ")
        age = input(">> Please Enter the age of Employee: ")
        department = input(">> Please Specify department of Employee: ")

        new_employee = {
            "name":name,
            "age":age,
            "department":department
            }
        self.Employees.append(new_employee)

        self.stdout.write(self.style.SUCCESS(f"Employee {name} added Successfully!"))
        print(self.Employees)

    def list_employees(self):
        if self.Employees:
            employee_data = [(emp["name"],emp["age"],emp["department"]) for emp in self.Employees]
            headers = ["Name", "Age", "Department"]

            # Use tabulate to format the data as a table
            table = tabulate(employee_data, headers, tablefmt="grid")

            # Display the table
            self.stdout.write(table)
        else:
            self.stdout.write("No employees found.")

    def help_user(self):
        commandFile = "core\management\commands\commands.json"
        with open(commandFile, "r") as json_file:
            # Use json.load() to parse the JSON data into a Python object
            data = json.load(json_file)
        
        commandList = [(cmd["command"],cmd["description"]) for cmd in data]
        headers = ["Command","Description"]
        table = tabulate(commandList,headers=headers,tablefmt="grid")

        self.stdout.write(table)

    



        