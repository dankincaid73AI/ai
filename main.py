import time
from src.query.query_engine import query_tarantula

# Define the personas for the dynamic system prompts
PERSONAS = {
    "1": "research assistant",
    "2": "angry rude old man",
    "3": "overly enthusiastic game show host",
}


def choose_persona(cyan, green, reset):
    """
    Displays the persona menu using your existing terminal colors.
    """
    print(f"\n{cyan}--- Select Tarantula Persona ---{reset}")
    for key, name in PERSONAS.items():
        print(f"[{key}] {name.title()}")
    print("[Any other key] Default (Research Assistant)")

    choice = input(f"\n{cyan}Enter choice: {reset}").strip()
    selected = PERSONAS.get(choice, "research assistant")
    print(f"\n{green}✅ Persona locked in: {selected.upper()}{reset}")
    return selected


def run_cli():
    """
    Main loop for terminal interaction with timing, personas,
    and error handling.
    """
    # Preserving all of your exact ANSI escape codes
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    print(f"{GREEN}🤖 Tarantula Engine Online (type 'quit' to exit){RESET}")
    print("-" * 45)

    # Injecting the menu before the loop begins
    current_persona = choose_persona(CYAN, GREEN, RESET)
    print("-" * 45)

    while True:
        question = input(f"\n{CYAN}Ask Tarantula: {RESET}").strip()

        if question.lower() in ["quit", "exit"]:
            print(f"{YELLOW}Shutting down Tarantula engine...{RESET}")
            break

        if not question:
            continue

        print(f"{YELLOW}Thinking...{RESET}")
        start_time = time.time()

        try:
            # Passing your chosen persona down into the query engine
            answer = query_tarantula(question, persona=current_persona)
            end_time = time.time()
            duration = round(end_time - start_time, 2)

            print(f"\n💡 {GREEN}Answer:{RESET} {answer}")
            print(f"{CYAN}(Generated in {duration}s){RESET}")

        except Exception as e:
            print(f"\n❌ {YELLOW}Engine Error: {str(e)}{RESET}")


if __name__ == "__main__":
    run_cli()
