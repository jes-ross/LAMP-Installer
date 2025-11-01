#!/usr/bin/env python3
from difflib import get_close_matches
import subprocess
import sys
import os
import re

def doCommand(command):
    print(f"Ejecutando {command}")
    process = subprocess.run(command, shell=True)
    if process.returncode != 0:
        print(f"Error ejecutando: {command}")
        sys.exit(1)


def configLine(file, line, configuration):
    
    try:
        
        with open(file, "r") as f:
            lines = f.readlines()
            
        match = None
        for i, item in enumerate(lines):
            if re.search(line.strip(), item) or get_close_matches(line.strip(), [item.strip()], cutoff=0.6):
                match = i
                break
            
        if match is not None:
            
            print(f"Modificando línea: {lines[match].strip()}")
            lines[match] = configuration + "\n"
            
            with open(file, "w") as f:
                f.writelines(lines)
        else:
            print(f"No se necontro línea {line}")
            
    except FileNotFoundError:
        
        print("No existe el fichero")


def main():
    if os.geteuid() != 0:
        print("Ejecuta esto como root")
        print("Usa python3 lampinstall.py")
        sys.exit(1)
        
    #Actualización Linux
    doCommand("apt-get update -y")
    doCommand("apt-get upgrade -y")
    
    #Instalación de Apache
    doCommand("apt install -y apache2 apache2-doc")
    
    #Instalación de MySQL
    doCommand("apt install mysql-server -y")
    
    #Configuración de MySQL
    doCommand("systemctl enable mysql")
    configLine("/etc/mysql/mysql.conf.d/mysqld.cnf", r"general_log = ", "general_log = 1")
    configLine("/etc/mysql/mysql.conf.d/mysqld.cnf", r"general_log_file = ", "general_log_file = /var/log/mysql/mysql.log")
    
    #Instalación de PHP
    doCommand("apt-get install -y php php-cli php-mysql php-gd php-xml php-mbstring php-curl libapache2-mod-php")
    
    
    #Configuración de PHP
    configLine("/etc/php/8.1/apache2/php.ini", r"display_errors = ", "display_errors = On")
    configLine("/etc/php/8.1/apache2/php.ini", r"upload_max_filesize = ", "upload_max_filesize = 20M")
    configLine("/etc/php/8.1/apache2/php.ini", r"memory_limit = ", "memory_limit = 256M")
    
    #Prioridad de PHP
    configLine("/etc/apache2/mods-enabled/dir.conf", 
            r"DirectoryIndex index.html index.cgi index.pl index.php index.xhtml index.htm", 
            "DirectoryIndex index.php index.html index.cgi index.pl index.xhtml index.htm")
    
    #Reiniciar servicios
    doCommand("systemctl restart apache2")

    doCommand("systemctl restart mysql")

if __name__ == "__main__":
    main()




