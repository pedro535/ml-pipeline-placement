from kfp import dsl, compiler


@dsl.component(
    base_image='python:3.12',
)
def say_hello(name: str) -> str:
    hello_text = f'Hello, {name}!'
    print(hello_text)
    return f"{hello_text} - from return"


@dsl.component(
    base_image='python:3.12',
)
def say_bye(name: str) -> str:
    bye_text = f'Bye, {name}!'
    print(bye_text)
    return f"{bye_text} - from return"


@dsl.pipeline(
    name='Hello Pipeline',
    description='A simple intro pipeline'
)
def hello_pipeline(recipient: str) -> str:
    hello_task = say_hello(name=recipient)
    bye_task = say_bye(name=recipient)
    return bye_task.output

compiler.Compiler().compile(hello_pipeline, 'pipeline.yaml')