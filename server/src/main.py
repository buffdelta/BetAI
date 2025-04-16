from Database import Database
from Logger import Logger
import argparse

def main(level):

    logger = Logger(level)
    database = Database()
    database.build_database()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Logging Levels")
    parser.add_argument("--level", type=str, default='INFO', help='INFO or DEBUG')
    args = parser.parse_args()
    main(level = args.level)
