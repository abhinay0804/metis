import traceback
try:
    import transformers.pipelines
except Exception as e:
    traceback.print_exc()

try:
    from transformers import pipeline
except Exception as e:
    traceback.print_exc()
