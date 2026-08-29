"""CLI entrypoint: run the full chunking pipeline against a folder of input documents."""
import argparse

from src.lineage import LineageWriter, connect_from_env
from src.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="Project 1 chunking pipeline")
    parser.add_argument("--input", required=True, help="Folder of raw documents to process")
    parser.add_argument("--output", required=True, help="Folder to write manifest files to")
    parser.add_argument("--config", default="config/artifact_config.yaml")
    args = parser.parse_args()

    writer = LineageWriter(connect_from_env())
    for path in run_pipeline(args.input, args.output, args.config, writer):
        print(f"wrote manifest: {path}")


if __name__ == "__main__":
    main()
