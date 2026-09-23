# Ferramentas Fácil IA V5

Versão para Android/Termux com **frontend web + backend Python + IA local baseada em regras**, sem OpenAI API e sem token.

## O que funciona
- Assistente local para explicar assuntos
- Resumos
- Plano de estudo
- Gerador de questões de treino
- Calculadora visual
- Interface responsiva para celular
- API `/api/ai`
- Status `/api/status`

## Rodar no Termux
```bash
pkg update -y
pkg install python -y
cd ~/ferramentas-facil-ia-v5
python server.py
```
Depois abra no navegador:
`http://127.0.0.1:8000`

## Se o projeto estiver em Downloads
```bash
cp -r ~/storage/downloads/ferramentas-facil-ia-v5 ~/
cd ~/ferramentas-facil-ia-v5
python server.py
```

## Importante
Esta V5 não usa uma API externa. A “IA local” é um motor educacional determinístico em Python. Isso significa que ela não tem o mesmo conhecimento de um modelo grande de linguagem. O projeto foi feito para funcionar imediatamente e servir de base para uma IA local mais avançada no futuro.
