from huggingface_hub import hf_hub_download
import onnxruntime as ort

# Download / locate the model automatically
model_path = hf_hub_download(
    repo_id="PINGEcosystem/gv-yolo26",
    filename="weights.onnx"
)

print("Model path:")
print(model_path)

# Load the ONNX model
session = ort.InferenceSession(model_path)

print("\nMODEL LOADED SUCCESSFULLY!")

print("\nINPUT:")
for inp in session.get_inputs():
    print("Name:", inp.name)
    print("Shape:", inp.shape)
    print("Type:", inp.type)

print("\nOUTPUTS:")
for output in session.get_outputs():
    print("Name:", output.name)
    print("Shape:", output.shape)
    print("Type:", output.type)