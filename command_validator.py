"""
Sistema de proteção contra comandos perigosos
"""
import re
from typing import Tuple

# Lista de comandos perigosos que não podem ser executados
DANGEROUS_COMMANDS = [
    "rm",
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
    "sudo rm",
    "sudo shutdown",
    "sudo reboot",
    "sudo halt",
    "sudo poweroff",
    "dd",
    "mkfs",
    "fdisk",
    "format",
    "del",  # Windows, mas por segurança
    "format",  # Windows
]

# Padrões perigosos
DANGEROUS_PATTERNS = [
    r"rm\s+-rf",  # rm -rf
    r"rm\s+-\*",  # rm com flags perigosas
    r">\s*/dev/",  # Redirecionamento para /dev
    r"sudo\s+rm",  # sudo rm
    r"sudo\s+shutdown",  # sudo shutdown
    r"sudo\s+reboot",  # sudo reboot
    r"sudo\s+dd",  # sudo dd
    r"dd\s+if=.*of=/dev/",  # dd para dispositivo
    r"mkfs\s+",  # mkfs
    r"fdisk\s+",  # fdisk
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}",  # Fork bomb
    r"chmod\s+777",  # chmod perigoso
    r"chmod\s+-R\s+777",  # chmod recursivo perigoso
]


def is_command_dangerous(command: str) -> Tuple[bool, str]:
    """
    Verifica se um comando é perigoso
    
    Returns:
        (is_dangerous, reason)
    """
    command = command.strip()
    
    if not command:
        return True, "Comando vazio não é permitido"
    
    # Remove espaços extras
    command = re.sub(r'\s+', ' ', command)
    
    # Verifica comandos perigosos exatos
    first_word = command.split()[0] if command.split() else ""
    if first_word.lower() in DANGEROUS_COMMANDS:
        return True, f"Comando '{first_word}' não é permitido por questões de segurança"
    
    # Verifica padrões perigosos
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, f"Comando contém padrão perigoso: {pattern}"
    
    # Verifica se contém pipes ou redirecionamentos perigosos
    if "|" in command and any(cmd in command.lower() for cmd in ["rm", "shutdown", "dd"]):
        return True, "Comandos perigosos não podem ser usados com pipes"
    
    # Verifica redirecionamento para arquivos do sistema
    if re.search(r">\s*(/etc|/bin|/sbin|/usr/bin|/usr/sbin|/System)", command):
        return True, "Redirecionamento para diretórios do sistema não é permitido"
    
    return False, ""


def validate_command(command: str) -> Tuple[bool, str]:
    """
    Valida um comando antes de executá-lo
    
    Returns:
        (is_valid, error_message)
    """
    if not command:
        return False, "Comando não pode ser vazio"
    
    is_dangerous, reason = is_command_dangerous(command)
    if is_dangerous:
        return False, reason
    
    return True, ""

