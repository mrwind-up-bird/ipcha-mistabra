"""Export cross-encoder/nli-deberta-v3-base to ONNX."""
import os

MODEL_ID = "cross-encoder/nli-deberta-v3-base"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "model")

def export():
    from optimum.onnxruntime import ORTModelForSequenceClassification
    from transformers import AutoTokenizer

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Exporting {MODEL_ID} to ONNX...")
    model = ORTModelForSequenceClassification.from_pretrained(MODEL_ID, export=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"Model exported to {OUTPUT_DIR}")

if __name__ == "__main__":
    export()
