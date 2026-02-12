import json
import math
from .html import get_captcha_image
from PIL import Image
from pathlib import Path
import numpy as np
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LABEL_TXT = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
HEIGHT = 40
WIDTH = 200

def softmax(a):
    s = 0.0
    for f in a:
        s += math.exp(f)
    n = []
    for i in range(len(a)):
        n.append(math.exp(a[i]) / s)
    return n

def preProcess(im):
    avg = 0
    for row in im:
        for f in row:
            avg += f
    avg /= (24 * 22)
    ne = [[0]*len(im[0]) for _ in range(len(im))]
    for i in range(len(im)):
        for j in range(len(im[0])):
            if im[i][j] > avg:
                ne[i][j] = 1
            else:
                ne[i][j] = 0
    return ne

def matrixMultiplication(a, b):
    x = len(a)
    z = len(a[0])
    y = len(b[0])
    if len(b) != z:
        raise ValueError("Invalid matrix dimensions")
    product = [[0 for _ in range(y)] for _ in range(x)]
    for i in range(x):
        for j in range(y):
            for k in range(z):
                product[i][j] += a[i][k] * b[k][j]
    return product

def matrixAddition(a, b):
    c = []
    for i in range(len(a)):
        c.append(a[i] + b[i])
    return c

def saturation(d):
    sat = [0] * (len(d) // 4)
    for i in range(0, len(d), 4):
        r = d[i]
        g = d[i + 1]
        b = d[i + 2]
        mn = min(r, g, b)
        mx = max(r, g, b)
        if mx == 0:
            sat[i // 4] = 0
        else:
            sat[i // 4] = round(((mx - mn) * 255) / mx)
    return sat

def flatten(ar):
    h = len(ar)
    w = len(ar[0])
    ne = [0] * (h * w)
    for i in range(h):
        for j in range(w):
            ne[i * w + j] = ar[i][j]
    return ne

def deflatten(ar, shape):
    h, w = shape
    img = [[0]*w for _ in range(h)]
    for i in range(h):
        for j in range(w):
            img[i][j] = ar[i * w + j]
    return img

def C_Blocks(im):
    blocksList = [None] * 6
    for a in range(6):
        x1 = (a + 1) * 25 + 2
        y1 = 7 + 5 * (a % 2) + 1
        x2 = (a + 2) * 25 + 1
        y2 = 35 - 5 * ((a + 1) % 2)
        block = []
        for row in im[y1:y2]:
            block.append(row[x1:x2])
        blocksList[a] = block
    return blocksList

def load_image_rgba_flat_from_pil(img):
    img = img.convert("RGBA")
    arr = np.asarray(img, dtype=np.uint8)
    return arr.reshape(-1).tolist()

def solve_captcha(img):
    WEIGHTS_PATH = Path(__file__).parent / "weights.json"
    with open(WEIGHTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    weights = data["weights"]
    biases = data["biases"]
    flat_rgba = load_image_rgba_flat_from_pil(img)
    sat = saturation(flat_rgba)
    img2d = deflatten(sat, (HEIGHT, WIDTH))
    blocks = C_Blocks(img2d)
    out = ""
    for i in range(6):
        block = preProcess(blocks[i])
        block = flatten(block)
        block = [block]
        block = matrixMultiplication(block, weights)
        block = block[0]
        block = matrixAddition(block, biases)
        block = softmax(block)
        idx = block.index(max(block))
        out += LABEL_TXT[idx]
    return out

if __name__ == "__main__":
    result = solve_chennai("captcha.jpg", "weights.json")
    print(result)