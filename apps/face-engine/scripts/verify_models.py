import insightface
import os

print("--- INSIGHTFACE MODEL PACK AUDIT ---")
app = insightface.app.FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
app.prepare(ctx_id=-1, det_size=(640, 640))

print("\nModels loaded in FaceAnalysis('buffalo_l'):")
for key, model in app.models.items():
    print(f"\n[Key: '{key}']")
    print(f"  Class: {type(model).__name__}")
    if hasattr(model, "model_file"):
        print(f"  Model File: {model.model_file}")
        basename = os.path.basename(model.model_file)
        print(f"  Basename: {basename}")
    if hasattr(model, "session"):
        session = model.session
        inputs = session.get_inputs()
        outputs = session.get_outputs()
        print(f"  ONNX Inputs: {[(i.name, i.shape, i.type) for i in inputs]}")
        print(f"  ONNX Outputs: {[(o.name, o.shape, o.type) for o in outputs]}")
    if hasattr(model, "input_size"):
        print(f"  Input Size: {model.input_size}")
    if hasattr(model, "input_mean"):
        print(f"  Input Mean: {model.input_mean}")
    if hasattr(model, "input_std"):
        print(f"  Input Std: {model.input_std}")

print("\n--- MODEL AUDIT COMPLETE ---")
