# main.py
from config import parse_arguments
from inference_pipeline import InferencePipeline

def main():
    args = parse_arguments()
    print(f"Arguments: {args}")

    pipeline = InferencePipeline(args)
    pipeline.pipeline()

if __name__ == "__main__":
    main()
