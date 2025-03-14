from colorama import Fore, Style, init

init(autoreset=True)

def Error(message: str) -> None:
    return (f"{Fore.RED}[ERREUR] {Fore.WHITE}{message}{Style.RESET_ALL}")

def Warning(message: str) -> None:
    return (f"{Fore.YELLOW}[AVERTISSEMENT] {Fore.WHITE}{message}{Style.RESET_ALL}")

def Info(message: str) -> None:
    return (f"{Fore.CYAN}[INFO] {Fore.WHITE}{message}{Style.RESET_ALL}")