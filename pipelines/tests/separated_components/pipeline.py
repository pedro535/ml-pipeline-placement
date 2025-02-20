from kfp import dsl, compiler
from kfp.kubernetes import mount_pvc
from kfp.dsl import Input, Output, Dataset

# from components.data_collection import data_collection
# from components.model_training import model_training
from components.save_model import save_model
from components.load_model import load_model

@dsl.pipeline(
    name='Test 2 pipeline'
)
def gts_pipeline(pvc_name: str):
    save_model_op = save_model()
    load_model_op = load_model(
        ml_model = save_model_op.outputs['ml_model']
    )

compiler.Compiler().compile(gts_pipeline, 'pipeline.yaml')