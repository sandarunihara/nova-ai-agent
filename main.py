import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.agent import NovaAgent

def main():
    agent = NovaAgent()
    print("\n" + "=" * 60)
    print("✨ NOVA AI Agent Ready (Modular Architecture)")
    print("Commands: 'clear' to reset | 'exit' to quit")
    print("=" * 60 + "\n")

    while True:
        user_input = input("\nSandaru: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "q"]:
            print("\nNova: Powering down. Have a productive day, Sandaru.")
            break
        if user_input.lower() == "clear":
            agent.memory.reset()
            print("🧹 Memory cleared!")
            continue

        agent.process_turn(user_input)
        print("-" * 60)

if __name__ == "__main__":
    main()