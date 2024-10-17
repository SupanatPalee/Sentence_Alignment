from fastapi import FastAPI, Form
import re
from torch.utils.data import Dataset, DataLoader
from transformers import CamembertTokenizer, RobertaForSequenceClassification
import torch
from torch import nn
import pandas as pd
import os

try:
    GPU_ENV = os.environ['GPU_ENV']
except:
    GPU_ENV = None

app = FastAPI()

model = RobertaForSequenceClassification.from_pretrained("models/version1")
sm = nn.Softmax(dim=1)
tokenizer = CamembertTokenizer.from_pretrained('models/tokenizer')

if GPU_ENV == "GPU":
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)

class SentDatasetInfer(Dataset):
    def __init__(self, data, tokenizer):
        self.tokenizer = tokenizer
        self.data = data
        self.inputs = []
        for example in self.data: 
            tok_result = self.tokenizer(
                example[0], 
                example[1], 
                max_length=256,
                padding="max_length",
                truncation=True,
                return_tensors="pt"
            )

            tok_result['input_ids'] = torch.squeeze(tok_result['input_ids'])
            tok_result['attention_mask'] = torch.squeeze(tok_result['attention_mask'])
            self.inputs.append(tok_result)

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, index):
        return self.inputs[index]

def assemble_result(pred, text):
    row = 0
    previous_space = 0
    sentence_ans = ""
    sentences_ans = []

    start = 0
    pos = text.find(" ", start)
    num2check = 0
    while pos != -1:
        num2check += 1
        start = pos + 1
        pos = text.find(" ", start)

    for i, c in enumerate(text):
        if c == " " and pred[row] == 0:
            x = text[previous_space:i]
            previous_space = i+1
            sentence_ans += x + " "
            row += 1
        elif c == " " and pred[row] == 1:
            x = text[previous_space:i]
            previous_space = i+1
            sentence_ans += x + " "
            sentences_ans.append(sentence_ans.strip())
            sentence_ans = ""
            row += 1

        if row == num2check and i == len(text) - 1:
            x = text[previous_space:i+1]
            previous_space = i+1
            sentence_ans += x + " "
            sentences_ans.append(sentence_ans.strip())

    return sentences_ans

@app.post("/cut_sent/")
async def cut_sent(data_path: str = Form(...), save_path: str = Form(...), mode: str = Form(...), model_name: str = ""):
    df = pd.read_csv(data_path)
    count = int(df.columns[0])
    mode = str_to_bool(mode)
    if mode:
        for i in range(count):
            print (f'thai_sentences_{i}.csv')
            cut(data_path, save_path, i)
    else:
        for i in range(count):
            if not os.path.exists(f'{save_path}thai_sentences_{i}.csv'):
                print(f'thai_sentences_{i}.csv')
                cut(data_path, save_path, i)

def str_to_bool(mode):
    if mode.lower() in ['true', '1', 't', 'y', 'yes']:
        return True
    elif mode.lower() in ['false', '0', 'f', 'n', 'no']:
        return False
    else:
        return True

def cut(data_path, save_path, i):
    df = pd.read_csv(f'{data_path}{i}.csv', usecols=['Journal_link', 'Archives_link', 'Archives_year', 'Article_link', 'Thai_sentence'])
    text = df.iloc[0, 4]
    text = re.sub("\n", "", text).strip()
    start = 0
    pos = text.find(" ", start)
    contexts = []
    while pos != -1:
        left_context = text[0:pos]
        right_context = text[pos+1:]
        contexts.append([left_context, right_context])
        start = pos + 1
        pos = text.find(" ", start)
        
    infer_dataset = SentDatasetInfer(contexts, tokenizer)
    infer_loader = DataLoader(infer_dataset, batch_size=8)

    pred_lst = []
    with torch.no_grad():
        for batch in infer_loader:
            if GPU_ENV == "GPU":
                output = model.forward(
                    input_ids=batch["input_ids"].to(device),
                    attention_mask=batch["attention_mask"].to(device)
                )
                logits = output.logits
                pred = torch.argmax(sm(logits), dim=1)
                pred_lst += pred.cpu().detach().numpy().tolist()
            else:
                output = model.forward(
                    input_ids=batch["input_ids"],
                    attention_mask=batch["attention_mask"]
                )
                logits = output.logits
                pred = torch.argmax(sm(logits), dim=1)
                pred_lst += pred.detach().numpy().tolist()

    sentences = assemble_result(pred_lst, text)

    df = pd.DataFrame({'sentences': sentences})
    df.to_csv(f'{save_path}thai_sentences_{i}.csv', index=False, encoding='utf-8')
