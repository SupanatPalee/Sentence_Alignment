from fastapi import FastAPI, Form
import re
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from transformers import CamembertTokenizer
import torch
from torch import nn
import torch.functional as F
from transformers import RobertaForSequenceClassification
import bios

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

# dataset for inference
class SentDatasetInfer(Dataset):
    def __init__(self, data, tokenizer) -> None:
        self.tokenizer = tokenizer
        self.data = data # list of [A,B]
        self.inputs = []
        for i, example in enumerate(self.data): 
            tok_result = self.tokenizer(
                example[0], # A sequence
                example[1], # B sequence
                max_length=256,
                padding="max_length",
                truncation=True,
                return_tensors="pt"
            )

            tok_result['input_ids'] = torch.squeeze(tok_result['input_ids'])
            tok_result['attention_mask'] = torch.squeeze(tok_result['attention_mask'])
            self.inputs.append(tok_result)

    def __len__(self) -> int:   
        return len(self.inputs)

    def __getitem__(self, index: int):
        return self.inputs[index]

def assemble_result(pred:list, text:str) -> list:
    # bookkeeping variables
    row = 0
    previous_space = 0
    sentence_ans = ""
    sentences_ans = []

    # find how many spaces in text
    start = 0
    pos = text.find(" ", start)
    contexts = []
    num2check = 0
    while(pos != -1):
        num2check += 1
        start = pos + 1
        pos = text.find(" ", start)

    for i, c in enumerate(text):
        if c == " " and pred[row] == 0: # no cut
            x = text[previous_space:i]
            previous_space = i+1
            sentence_ans += x + " "
            row += 1
        elif c == " " and pred[row] == 1: # cut
            x = text[previous_space:i]
            previous_space = i+1
            sentence_ans += x + " "
            sentences_ans.append(sentence_ans.strip())
            sentence_ans = ""
            row += 1

        if row == num2check and i == len(text) - 1: # for the last sentence
            x = text[previous_space:i+1]
            previous_space = i+1
            sentence_ans += x + " "
            sentences_ans.append(sentence_ans.strip())

    return sentences_ans

@app.post("/cut_sent/")
async def cut_sent(text: str = Form(...), model_name: str=""):
    text = re.sub("\n", "", text).strip()
    # build context
    start = 0
    pos = text.find(" ", start)
    contexts = []
    while(pos != -1):
        left_context = text[0:pos]
        right_context = text[pos+1:]
        contexts.append([left_context, right_context])
        start = pos + 1
        pos = text.find(" ", start)
    
    # create dataset
    infer_dataset = SentDatasetInfer(contexts, tokenizer)
    infer_loader = DataLoader(infer_dataset, batch_size=8)

    # run inference
    pred_lst = []
    with torch.no_grad():
        for i, batch in enumerate(infer_loader):
            if GPU_ENV == "GPU":
                output = model.forward(
                    input_ids=batch["input_ids"].to(device),
                    attention_mask=batch["attention_mask"].to(device)
                )
                logits = output.logits
                pred = torch.argmax(sm(logits),dim=1)
                pred_lst += pred.cpu().detach().numpy().tolist()
            else:
                output = model.forward(
                    input_ids=batch["input_ids"],
                    attention_mask=batch["attention_mask"]
                )
                logits = output.logits
                pred = torch.argmax(sm(logits),dim=1)
                pred_lst += pred.detach().numpy().tolist()

    # assemble the result
    sentences = assemble_result(pred_lst, text)


    return {"sentences": sentences}
