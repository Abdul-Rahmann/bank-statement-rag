"""
Command-Line Interface
Simple CLI for interacting with the RAG system
"""

import argparse, sys
from pathlib import Path
root_dir = Path(__file__).parent.resolve()
sys.path.append(str(root_dir))

from src.rag_system import BankStatementRAG
from src.config import get_config, get_config_value

def main():
    parser = argparse.ArgumentParser(
        description='Bank Statement RAG System - Query your transactions'
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

    print("\n" + "=" * 60)
    print("Bank Statement RAG System")
    print("=" * 60)

    # Load config
    try:
        config = get_config()
        print("config loaded: ", config, "\n\n")
    except FileNotFoundError:
        print(f"\nError: Config file not found.")
        return
    except Exception as e:
        print(f"\nError loading config: {e}")
        return

    try:
        rag = BankStatementRAG(config, force_refresh=args.refresh)
    except Exception as e:
        print(f"\nError initializing system: {e}")
        return

    if rag.transactions_df is None or len(rag.transactions_df) == 0:
        data_dir = get_config_value('DATA_DIR', 'data/raw')
        print("\nNo data loaded. Please:")
        print(f"   1. Place PDF statements in: {data_dir}")
        print("   2. Run with --refresh flag")
        print("\nExample:")
        print("   python cli.py --refresh")
        return

    stats = rag.get_stats()
    print(f"\nAccount Summary:")
    print(f"   • Total transactions: {stats['total_transactions']}")
    print(f"   • Total spent: ${stats['total_spent']:,.2f}")
    print(f"   • Total received: ${stats['total_received']:,.2f}")
    print(f"   • Net: ${stats['net']:,.2f}")
    print(f"   • Date range: {stats['date_range']}")
    print(f"   • Categories: {len(stats['categories'])}")

    if args.query:
        print(f"\nQ: {args.query}")
        try:
            answer = rag.ask(args.query)
            print(f"\nA: {answer}\n")
        except Exception as e:
            print(f"\nError: {e}\n")
        return

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
                print("\nGoodbye!")
                break

            if not question:
                continue

            answer = rag.ask(question)
            print(f"\nAssistant: {answer}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()