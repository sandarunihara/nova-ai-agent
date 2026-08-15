import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.agent import NovaAgent

def main():
    agent = NovaAgent()
    print("\n" + "═" * 60)
    print("  ✨ NOVA AI — Personal Assistant for Mr. Sandaru")
    print("  🔧 Modular Architecture | Loyal & Ready to Serve")
    print("  📝 Commands: 'clear' to reset | 'exit' to quit")
    print("═" * 60 + "\n")

    while True:
        user_input = input("\nSandaru: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "q"]:
            print("\nNova: Powering down. It was an honor serving you, Sir. Have a productive day.")
            break
        if user_input.lower() == "clear":
            agent.memory.reset()
            print("🧹 Memory cleared! Ready for your next command, Sir.")
            continue

        agent.process_turn(user_input)
        print("-" * 60)

if __name__ == "__main__":
    main()