"""
Tarantula CLI
Entry point for interacting with the query engine.
"""

# Import directly from your root query_engine.py file
from query_engine import query_tarantula


def run_cli():
    """
    Main loop for terminal interaction.
    """
    print("🤖 Tarantula Engine Online (type 'quit' to exit)")
    print("-" * 45)

    while True:
        question = input("\nQuery: ")

        if question.lower() in ["quit", "exit"]:
            print("Shutting down engine...")
            break

        if not question.strip():
            continue

        print("Thinking...")
        answer = query_tarantula(question)
        print(f"\n💡 Answer: {answer}")


if __name__ == "__main__":
    run_cli()
