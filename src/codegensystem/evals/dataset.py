from langsmith import Client


client = Client()

if client.has_dataset(dataset_name="codegen-system-eval"):
    client.delete_dataset(dataset_name="codegen-system-eval")

dataset = client.create_dataset(
    "codegen-system-eval",
    description="10 задач: 5 простых, 5 средних",
)

examples = [
    {"inputs": {"input": "Напиши функцию сложения двух чисел"},
     "outputs": {"expected_verdict": "APPROVE", "expected_tier": "SMALL", "min_changes": 2}},
    {"inputs": {"input": "Напиши функцию умножения двух чисел"},
     "outputs": {"expected_verdict": "APPROVE", "expected_tier": "SMALL", "min_changes": 2}},
    {"inputs": {"input": "Напиши функцию возведения числа в квадрат"},
     "outputs": {"expected_verdict": "APPROVE", "expected_tier": "SMALL", "min_changes": 2}},
    {"inputs": {"input": "Напиши функцию проверки чётности числа"},
     "outputs": {"expected_verdict": "APPROVE", "expected_tier": "SMALL", "min_changes": 2}},
    {"inputs": {"input": "Напиши функцию нахождения максимума из двух чисел"},
     "outputs": {"expected_verdict": "APPROVE", "expected_tier": "SMALL", "min_changes": 2}},

    {"inputs": {"input": "Напиши функцию для поиска слов по бинарному алгоритму"},
     "outputs": {"expected_verdict": "APPROVE", "expected_tier": "LARGE", "min_changes": 2}},
    {"inputs": {"input": "Напиши функцию сортировки списка пузырьком"},
     "outputs": {"expected_verdict": "APPROVE", "expected_tier": "LARGE", "min_changes": 2}},
    {"inputs": {"input": "Напиши функцию проверки палиндрома с тестами"},
     "outputs": {"expected_verdict": "APPROVE", "expected_tier": "SMALL", "min_changes": 2}},
    {"inputs": {"input": "Напиши функцию вычисления факториала с обработкой отрицательных чисел"},
     "outputs": {"expected_verdict": "APPROVE", "expected_tier": "SMALL", "min_changes": 2}},
    {"inputs": {"input": "Напиши функцию поиска наибольшего общего делителя"},
     "outputs": {"expected_verdict": "APPROVE", "expected_tier": "LARGE", "min_changes": 2}},
]

client.create_examples(
    inputs=[e["inputs"] for e in examples],
    outputs=[e["outputs"] for e in examples],
    dataset_id=dataset.id,
)