import time
from src.query.query_engine import query_tarantula


def run_cli():
    """
    Main loop for terminal interaction with timing and error handling.
    """
    # ANSI escape codes for basic terminal colors
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    print(f"{GREEN}🤖 Tarantula Engine Online (type 'quit' to exit){RESET}")
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
            answer = query_tarantula(question)
            end_time = time.time()
            duration = round(end_time - start_time, 2)

            print(f"\n💡 {GREEN}Answer:{RESET} {answer}")
            print(f"{CYAN}(Generated in {duration}s){RESET}")

        except Exception as e:
            print(f"\n❌ {YELLOW}Engine Error: {str(e)}{RESET}")


if __name__ == "__main__":
    run_cli()
