import sys
from core.config import GitkConfig


def main():
    try:
        config = GitkConfig()
        config.init_config()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
