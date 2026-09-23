import json, os, re, random, math, ast, operator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', '8000'))
BASE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(BASE, 'public')

SUBJECTS = {
    'matemática': ['equação', 'função', 'porcentagem', 'fração', 'geometria', 'probabilidade'],
    'português': ['gramática', 'interpretação', 'oração', 'substantivo', 'verbo', 'literatura'],
    'história': ['roma', 'grécia', 'marx', 'revolução', 'brasil', 'caminha'],
    'geografia': ['clima', 'tempo', 'fuso', 'rotação', 'translação', 'globalização'],
    'biologia': ['célula', 'proteína', 'lipídio', 'carboidrato', 'membrana', 'atp'],
    'química': ['átomo', 'elemento', 'ligação', 'mol', 'tabela periódica', 'reação'],
    'física': ['velocidade', 'força', 'energia', 'movimento', 'newton', 'potência'],
    'filosofia': ['sócrates', 'platão', 'aristóteles', 'epicurismo', 'ceticismo', 'dogmatismo'],
    'sociologia': ['marx', 'weber', 'durkheim', 'capitalismo', 'ação social'],
    'inglês': ['to be', 'simple present', 'pronome', 'verb', 'present'],
}

TEMPLATES = {
    'matemática': 'Em matemática, organize os dados, escolha a fórmula ou operação adequada e confira o resultado substituindo-o novamente no problema.',
    'português': 'Em português, procure primeiro a ideia central do texto e depois observe a função das palavras e a relação entre as orações.',
    'história': 'Em história, relacione acontecimentos com contexto, causas, consequências, grupos sociais e período histórico.',
    'geografia': 'Em geografia, conecte fenômenos naturais e sociais ao espaço, à localização, à escala e às relações entre sociedade e natureza.',
    'biologia': 'Em biologia, comece pela definição, identifique a estrutura ou processo envolvido e depois relacione sua função ao organismo.',
    'química': 'Em química, identifique as substâncias e partículas envolvidas, observe as proporções e represente o processo de forma organizada.',
    'física': 'Em física, liste as grandezas conhecidas, converta unidades quando necessário, escolha a relação física adequada e calcule.',
    'filosofia': 'Em filosofia, identifique o conceito principal, o autor ou corrente e compare a ideia com outras posições.',
    'sociologia': 'Em sociologia, observe os conceitos e relacione-os às instituições, relações sociais, trabalho, cultura e organização da sociedade.',
    'inglês': 'Em inglês, identifique o sujeito, o tempo verbal e o verbo principal antes de escolher a forma correta da frase.'
}


def detect_subject(text):
    t = text.lower()
    scores = {s: 0 for s in SUBJECTS}
    for subject, words in SUBJECTS.items():
        for w in words:
            if w in t:
                scores[subject] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] else 'geral'


def clean_text(s):
    return re.sub(r'\s+', ' ', str(s or '')).strip()


def make_summary(text):
    text = clean_text(text)
    if not text:
        return 'Envie um assunto ou texto para eu montar um resumo.'
    subject = detect_subject(text)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    useful = [s for s in sentences if len(s) > 25][:5]
    core = ' '.join(useful) if useful else text
    return f'Resumo — {subject.title()}\n\n{core[:900]}\n\nDica: {TEMPLATES.get(subject, "Divida o assunto em definição, exemplos e revisão.")}'


def make_explanation(text):
    text = clean_text(text)
    subject = detect_subject(text)
    if not text:
        return 'Digite o assunto que você quer entender.'
    return (f'Vamos por partes.\n\n1. O assunto identificado é: {subject.title()}.\n'
            f'2. Ideia principal: {text[:500]}.\n'
            f'3. Como estudar: {TEMPLATES.get(subject, "Comece pela definição, depois veja exemplos e faça exercícios.")}\n'
            '4. Depois, tente explicar o assunto com suas próprias palavras.')


def make_quiz(text, n=5):
    text = clean_text(text)
    subject = detect_subject(text)
    topic = text[:80] if text else subject.title()
    questions = []
    patterns = [
        f'Qual é a ideia central de {topic}?',
        f'Qual conceito está diretamente relacionado a {topic}?',
        f'Qual alternativa apresenta uma aplicação correta de {topic}?',
        f'Qual é uma diferença importante envolvendo {topic}?',
        f'Qual exemplo ajuda a entender {topic}?',
    ]
    for i in range(min(max(int(n), 1), 10)):
        q = patterns[i % len(patterns)]
        questions.append({'id': i+1, 'question': q, 'options': ['A) Definição ou aplicação correta do conceito', 'B) Uma ideia sem relação com o assunto', 'C) O conceito oposto', 'D) Uma afirmação fora do contexto']})
    return {'subject': subject, 'questions': questions, 'note': 'Este modo local gera questões-base para estudo. Confira o conteúdo no seu material antes de usar como gabarito.'}

# Safe arithmetic evaluator for the calculator.
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod, ast.USub: operator.neg, ast.UAdd: operator.pos}
def safe_calc(expr):
    expr = str(expr).replace('×','*').replace('÷','/').replace(',','.').strip()
    if len(expr) > 100 or not re.fullmatch(r'[0-9+\-*/().%\s]+', expr):
        raise ValueError('Expressão não permitida')
    def ev(node):
        if isinstance(node, ast.Expression): return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int,float)): return node.value
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS: return OPS[type(node.op)](ev(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in OPS: return OPS[type(node.op)](ev(node.left), ev(node.right))
        raise ValueError('Expressão inválida')
    return ev(ast.parse(expr, mode='eval'))


def local_ai(action, text, n=5):
    if action == 'summary': return {'type':'text','title':'Resumo','content':make_summary(text)}
    if action == 'explain': return {'type':'text','title':'Explicação','content':make_explanation(text)}
    if action == 'quiz': return {'type':'quiz', **make_quiz(text,n)}
    if action == 'study':
        subject = detect_subject(text)
        return {'type':'text','title':'Plano de estudo','content':(
            f'Plano adaptado — {subject.title()}\n\n'
            '1) 5 min: leia o conceito e destaque palavras-chave.\n'
            '2) 10 min: veja 2 exemplos no material da escola.\n'
            '3) 10 min: responda 5 questões sem consultar.\n'
            '4) 5 min: corrija e anote os erros.\n'
            '5) 2 min: explique o assunto em voz alta com suas palavras.'
        )}
    if action == 'chat':
        return {'type':'text','title':'Assistente local','content':make_explanation(text)}
    return {'type':'text','title':'Ferramentas Fácil IA','content':'Escolha uma função para começar.'}


class Handler(BaseHTTPRequestHandler):
    def _headers(self, code=200, ctype='application/json; charset=utf-8'):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()
    def do_OPTIONS(self): self._headers(204)
    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/status':
            self._headers(); self.wfile.write(json.dumps({'ok':True,'ai':'local','python':True,'api_key_required':False}, ensure_ascii=False).encode()); return
        if path == '/api/health':
            self._headers(); self.wfile.write(b'{"ok":true}'); return
        rel = 'index.html' if path == '/' else path.lstrip('/')
        target = os.path.normpath(os.path.join(PUBLIC, rel))
        if not target.startswith(PUBLIC) or not os.path.isfile(target):
            self._headers(404); self.wfile.write(b'{"error":"Nao encontrado"}'); return
        ctype = 'text/html; charset=utf-8' if target.endswith('.html') else 'text/css; charset=utf-8' if target.endswith('.css') else 'application/javascript; charset=utf-8' if target.endswith('.js') else 'application/octet-stream'
        self._headers(200, ctype)
        with open(target,'rb') as f: self.wfile.write(f.read())
    def do_POST(self):
        path = urlparse(self.path).path
        if path != '/api/ai': self._headers(404); self.wfile.write(b'{"error":"Rota nao encontrada"}'); return
        try:
            length = int(self.headers.get('Content-Length','0'))
            body = json.loads(self.rfile.read(length) or '{}')
            action = body.get('action','chat'); text = body.get('text',''); n = body.get('n',5)
            result = local_ai(action, text, n)
            self._headers(); self.wfile.write(json.dumps(result, ensure_ascii=False).encode())
        except Exception as e:
            self._headers(400); self.wfile.write(json.dumps({'error':str(e)}, ensure_ascii=False).encode())
    def log_message(self, fmt, *args):
        print('[server]', fmt % args)

if __name__ == '__main__':
    print(f'Ferramentas Fácil IA V5 • IA local Python • http://127.0.0.1:{PORT}')
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
