from colorama import init, Fore, Style

# Initialize colorama
init()


def print_header(text):
    print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{text.center(50)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")


def print_step(text):
    print(f"\n{Fore.YELLOW}▶ {text}{Style.RESET_ALL}")


def print_haiku(haiku):
    print(f"\n{Fore.GREEN}Generated Haiku:{Style.RESET_ALL}")
    for line in haiku.split("\n"):
        print(f"{Fore.WHITE}{line.center(50)}{Style.RESET_ALL}")


def print_evaluation(evaluation):
    if evaluation.strip() == "good_enough":
        print(f"\n{Fore.GREEN}Evaluation: Perfect! ✨{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}Evaluation Feedback:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{evaluation}{Style.RESET_ALL}")


def get_user_input(prompt):
    return input(f"\n{Fore.CYAN}{prompt}: {Style.RESET_ALL}")


def wait_for_enter(prompt):
    input(f"\n{Fore.YELLOW}{prompt}...{Style.RESET_ALL}")


def print_success(text):
    print(f"\n{Fore.GREEN}{text}{Style.RESET_ALL}")


def print_error(text):
    print(f"\n{Fore.RED}{text}{Style.RESET_ALL}")


def print_welcome():
    print(f"\n{Fore.CYAN}🐱 Welcome to the Cat Haiku Generator! ��{Style.RESET_ALL}")
