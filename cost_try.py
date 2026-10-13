import json

PRICES = json.load(open("prices.json"))

def compute_cost(model, tokens_in, tokens_out):
    p = PRICES[model]
    return (tokens_in * p["input"] + tokens_out * p["output"]) 

print(compute_cost("openai/gpt-oss-20b", 77, 113))
print(compute_cost("openai/gpt-oss-120b", 77, 113))