import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate git commit messages from diff",
        formatter_class=argparse.RawDescriptionHelpFormatter,
         epilog="""
                Examples:
                git diff | python generator.py
                git diff | python generator.py --detailed
                git diff | python generator.py --instruction "use conventional commits"
                git diff | python generator.py --template-file custom_template.tpl
            """
    )

    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize GitK config"
    )

    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Generate detailed commit message with body"
    )
    
    parser.add_argument(
        "--instruction",
        type=str,
        help="Additional instruction for commit message generation"
    )

    parser.add_argument(
        "--template-file",
        type=str,
        help="Path to custom commit template file (overrides config template)"
    )

    parser.add_argument(
        "--template",
        type=str,
        help="Inline custom commit template (overrides config template)"
    )

    return parser.parse_args()