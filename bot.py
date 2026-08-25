import os
import pickle
import sys
import argparse

from src.agents.tools import init_tools_context
from src.agents.orchestrator_agent import AgenticOrchestrator

def main():
    parser = argparse.ArgumentParser(description="AROL Agentic AI BOT Interface")
    parser.add_argument("--context", default="data/processed/context.pkl", help="Path to precomputed context file")
    args = parser.parse_args()

    if not os.path.exists(args.context):
        print(f"Error: Context file '{args.context}' not found.")
        print("Please run 'python main.py' first to process the raw telemetry and generate the context cache.")
        sys.exit(1)

    print("Loading context cache...")
    with open(args.context, "rb") as f:
        context = pickle.load(f)

    # Initialize the tools with the loaded context
    init_tools_context(context)

    # Attempt to initialize Orchestrator
    try:
        orchestrator = AgenticOrchestrator()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("\n" + "="*50)
    print("Welcome to the AROL Telemetry Bot!")
    print("Ask me anything about the capping operations.")
    print("Type 'exit' or 'quit' to close.")
    print("="*50 + "\n")

    while True:
        try:
            query = input("\nUser: ")
            if query.strip().lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            if not query.strip():
                continue
                
            print("Bot is thinking...")
            response = orchestrator.process_query(query)
            print("\nBot:")
            if isinstance(response, list):
                for item in response:
                    if isinstance(item, dict) and 'text' in item:
                        print(item['text'])
                    else:
                        print(item)
            elif isinstance(response, str):
                print(response)
            else:
                print(response)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
