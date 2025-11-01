""" Command - Line Interface Simple CLI for interacting with the RAG system """

import json
import argparse
from src.rag_system import BankStatementRAG


def load_config(config_path='config.json'):
    """Load configuration from JSON file."""
    with open(config_path) as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description='Bank Statement RAG System - Query your transactions'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Path to config file (default: config.json)'
    )
    parser.add_argument(
        '--refresh',
        action='store_true',
        help='Force refresh: re-extract PDFs and rebuild vectors'
    )
    parser.add_argument(
        '--query',
        type=str,
        help='Single query mode (non-interactive)'
    )

    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    print("\n" + "=" * 60)
    print("Bank Statement RAG System")
    print("=" * 60)

    # Initialize RAG system
    rag = BankStatementRAG(config, force_refresh=args.refresh)

    # Check if system is ready
    if rag.transactions_df is None or len(rag.transactions_df) == 0:
        print("\n No data loaded. Please:")
        print(f"   1. Place PDF statements in: {config.get('DATA_DIR', 'data/raw')}")
        print("   2. Run with --refresh flag")
        print("\nExample:")
        print("   python main.py --refresh")
        return

    # Show summary
    stats = rag.get_stats()
    print(f"\n Account Summary:")
    print(f"   • Total transactions: {stats['total_transactions']}")
    print(f"   • Total spent: ${stats['total_spent']:,.2f}")
    print(f"   • Total received: ${stats['total_received']:,.2f}")
    print(f"   • Net: ${stats['net']:,.2f}")
    print(f"   • Date range: {stats['date_range']}")
    print(f"   • Categories: {len(stats['categories'])}")

    # Single query mode
    if args.query:
        print(f"\n Q: {args.query}")
        answer = rag.ask(args.query)
        print(f"\n A: {answer}\n")
        return

    # Interactive mode
    print("\nAsk me anything about your transactions! (type 'quit' to exit)")
    print("   Example queries:")
    print("   - How much did I spend on groceries last month?")
    print("   - What were my top 5 largest purchases?")
    print("   - Show me all Amazon transactions")
    print("   - Give me a category breakdown for this year\n")

    while True:
        try:
            question = input("You: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("\n Goodbye!")
                break

            if not question:
                continue

            answer = rag.ask(question)
            print(f"\n Assistant: {answer}\n")

        except KeyboardInterrupt:
            print("\n\n Goodbye!")
            break
        except Exception as e:
            print(f"\n Error: {e}\n")


if __name__ == "__main__":
    main()
