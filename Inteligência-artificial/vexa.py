import os
import threading
import tkinter as tk
from tkinter import scrolledtext
from dotenv import load_dotenv
import requests
from openai import OpenAI


# ============================================================
# CONFIGURAÇÃO
# ============================================================

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "A chave OPENAI_API_KEY não foi encontrada.\n\n"
        "Crie um arquivo .env na pasta do projeto e coloque:\n"
        "OPENAI_API_KEY=sua_chave"
    )

client = OpenAI(
    api_key=API_KEY
)

# Modelo atual da OpenAI
MODEL = "gpt-5.6-luna"


# ============================================================
# PERSONALIDADE DA VEXA
# ============================================================

SYSTEM_PROMPT = """
Você é Vexa, uma inteligência artificial conversacional.

Seu objetivo principal é conversar e ajudar o usuário de forma natural.

Você pode responder perguntas sobre praticamente qualquer assunto,
incluindo:

- tecnologia
- programação
- Python
- jogos
- filmes
- séries
- música
- história
- ciência
- matemática
- escola
- faculdade
- trabalho
- ideias
- escrita
- criatividade
- curiosidades
- informática
- negócios
- conversas casuais
- explicações
- dúvidas gerais

RESPONDA À PERGUNTA DO USUÁRIO DE FORMA DIRETA.

Não responda dizendo simplesmente que você não pode ajudar quando
a pergunta puder ser respondida de forma segura e útil.

Se a pergunta for difícil, tente raciocinar e explicar passo a passo.

Se houver informações da Wikipédia fornecidas pelo programa, use-as
quando forem relevantes.

Não invente fatos.

Se não souber algo com certeza, diga que não tem certeza e explique
o que consegue afirmar.

Você deve manter o contexto da conversa.

Exemplo:

Usuário:
"Quem foi Albert Einstein?"

Vexa:
responde normalmente.

Usuário:
"Onde ele nasceu?"

Vexa:
entende que "ele" se refere a Albert Einstein.

Fale naturalmente, como uma assistente pessoal.

Responda em português por padrão.
"""


# ============================================================
# MEMÓRIA
# ============================================================

conversation = []


# ============================================================
# WIKIPÉDIA
# ============================================================

def pesquisar_wikipedia(pergunta):

    try:

        url = "https://pt.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": pergunta,
            "srlimit": 2,
            "utf8": 1
        }

        headers = {
            "User-Agent": "VexaAI/1.0"
        }

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        resultados = data.get(
            "query",
            {}
        ).get(
            "search",
            []
        )

        if not resultados:
            return None

        contexto = []

        for resultado in resultados:

            titulo = resultado.get("title")

            if not titulo:
                continue

            params_resumo = {
                "action": "query",
                "format": "json",
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "redirects": 1,
                "titles": titulo
            }

            resumo = requests.get(
                url,
                params=params_resumo,
                headers=headers,
                timeout=5
            )

            resumo.raise_for_status()

            dados_resumo = resumo.json()

            paginas = dados_resumo.get(
                "query",
                {}
            ).get(
                "pages",
                {}
            )

            for pagina in paginas.values():

                texto = pagina.get("extract")

                if texto:

                    contexto.append(
                        f"ARTIGO: {titulo}\n"
                        f"{texto[:3000]}"
                    )

        if not contexto:
            return None

        return "\n\n".join(contexto)

    except Exception:

        # Se a Wikipédia estiver indisponível,
        # a Vexa continua funcionando normalmente.
        return None


# ============================================================
# CHAMAR A IA
# ============================================================

def perguntar_vexa(pergunta):

    try:

        # ----------------------------------------------------
        # Pesquisa complementar
        # ----------------------------------------------------

        contexto = pesquisar_wikipedia(
            pergunta
        )

        if contexto:

            mensagem = f"""
Pergunta do usuário:

{pergunta}


Informações complementares encontradas na Wikipédia:

{contexto}


Responda à pergunta do usuário naturalmente.

Use as informações da Wikipédia apenas quando forem relevantes.
Não diga que "recebeu um contexto".
Não mencione este sistema interno.
"""

        else:

            mensagem = pergunta


        # ----------------------------------------------------
        # Adicionar pergunta à memória
        # ----------------------------------------------------

        conversation.append(
            {
                "role": "user",
                "content": mensagem
            }
        )


        # ----------------------------------------------------
        # CHAMADA PARA OPENAI
        # ----------------------------------------------------

        response = client.responses.create(

            model=MODEL,

            instructions=SYSTEM_PROMPT,

            input=conversation,

            max_output_tokens=2000
        )


        # ----------------------------------------------------
        # PEGAR RESPOSTA
        # ----------------------------------------------------

        resposta = response.output_text


        if not resposta:

            resposta = (
                "Não consegui gerar uma resposta agora. "
                "Tente novamente."
            )


        # ----------------------------------------------------
        # SALVAR RESPOSTA NA MEMÓRIA
        # ----------------------------------------------------

        conversation.append(
            {
                "role": "assistant",
                "content": resposta
            }
        )


        return resposta


    except Exception as erro:

        # Se alguma coisa der errado,
        # remove a pergunta que estava sendo processada.

        if conversation:
            conversation.pop()


        return (
            "Não consegui me conectar à IA neste momento.\n\n"
            f"Detalhes: {erro}"
        )


# ============================================================
# INTERFACE DA VEXA
# ============================================================

class VexaApp:

    def __init__(self, root):

        self.root = root

        # ----------------------------------------------------
        # JANELA
        # ----------------------------------------------------

        self.root.title(
            "Vexa AI"
        )

        self.root.geometry(
            "950x700"
        )

        self.root.minsize(
            650,
            500
        )

        # Preto
        self.root.configure(
            bg="#000000"
        )


        # ----------------------------------------------------
        # CABEÇALHO
        # ----------------------------------------------------

        header = tk.Frame(
            root,
            bg="#000000",
            height=75
        )

        header.pack(
            fill="x"
        )


        logo = tk.Label(

            header,

            text="VEXA",

            font=(
                "Segoe UI",
                24,
                "bold"
            ),

            fg="#ffffff",

            bg="#000000"
        )

        logo.pack(
            side="left",
            padx=25,
            pady=18
        )


        status = tk.Label(

            header,

            text="● ONLINE",

            font=(
                "Segoe UI",
                9,
                "bold"
            ),

            fg="#ffffff",

            bg="#000000"
        )

        status.pack(
            side="left"
        )


        # ----------------------------------------------------
        # CHAT
        # ----------------------------------------------------

        self.chat = scrolledtext.ScrolledText(

            root,

            wrap=tk.WORD,

            font=(
                "Segoe UI",
                11
            ),

            bg="#080808",

            fg="#ffffff",

            insertbackground="#ffffff",

            selectbackground="#333333",

            relief="flat",

            padx=25,

            pady=20
        )

        self.chat.pack(

            fill="both",

            expand=True,

            padx=15,

            pady=10
        )


        # ----------------------------------------------------
        # ESTILOS DAS MENSAGENS
        # ----------------------------------------------------

        self.chat.tag_config(

            "vexa",

            foreground="#ffffff",

            font=(
                "Segoe UI",
                11,
                "bold"
            )
        )


        self.chat.tag_config(

            "user",

            foreground="#aaaaaa",

            font=(
                "Segoe UI",
                11,
                "bold"
            )
        )


        self.chat.tag_config(

            "text",

            foreground="#eeeeee",

            font=(
                "Segoe UI",
                11
            )
        )


        # ----------------------------------------------------
        # MENSAGEM INICIAL
        # ----------------------------------------------------

        self.add_message(

            "Vexa",

            "Olá! Eu sou a Vexa. 👋\n\n"
            "Pode perguntar o que quiser. "
            "Estou pronta para conversar, explicar assuntos, "
            "ajudar com código, ideias, estudos e muito mais."
        )


        # ----------------------------------------------------
        # ÁREA DE TEXTO
        # ----------------------------------------------------

        bottom = tk.Frame(

            root,

            bg="#000000"
        )

        bottom.pack(

            fill="x",

            padx=15,

            pady=(0, 15)
        )


        self.entry = tk.Entry(

            bottom,

            font=(
                "Segoe UI",
                12
            ),

            bg="#111111",

            fg="#ffffff",

            insertbackground="#ffffff",

            relief="flat"
        )

        self.entry.pack(

            side="left",

            fill="x",

            expand=True,

            padx=(10, 5),

            pady=10,

            ipady=12
        )


        # ENTER

        self.entry.bind(

            "<Return>",

            lambda event:
            self.send_message()
        )


        # ----------------------------------------------------
        # BOTÃO
        # ----------------------------------------------------

        self.send_button = tk.Button(

            bottom,

            text="ENVIAR",

            command=self.send_message,

            font=(
                "Segoe UI",
                10,
                "bold"
            ),

            bg="#ffffff",

            fg="#000000",

            activebackground="#dddddd",

            activeforeground="#000000",

            relief="flat",

            cursor="hand2",

            padx=25,

            pady=10
        )

        self.send_button.pack(

            side="right",

            padx=(5, 10),

            pady=10
        )


        self.entry.focus()


    # ========================================================
    # MOSTRAR MENSAGEM
    # ========================================================

    def add_message(

        self,

        sender,

        message

    ):

        if sender == "Vexa":

            tag = "vexa"

        else:

            tag = "user"


        self.chat.insert(

            tk.END,

            f"{sender}\n",

            tag
        )


        self.chat.insert(

            tk.END,

            f"{message}\n\n",

            "text"
        )


        self.chat.see(
            tk.END
        )


    # ========================================================
    # ENVIAR
    # ========================================================

    def send_message(self):

        pergunta = self.entry.get().strip()


        if not pergunta:

            return


        # Limpar campo

        self.entry.delete(
            0,
            tk.END
        )


        # Mostrar pergunta

        self.add_message(

            "Você",

            pergunta
        )


        # Bloquear botão

        self.send_button.config(

            state="disabled",

            text="PENSANDO..."
        )


        # Thread para não travar a janela

        thread = threading.Thread(

            target=self.processar,

            args=(pergunta,),

            daemon=True
        )

        thread.start()


    # ========================================================
    # PROCESSAR RESPOSTA
    # ========================================================

    def processar(

        self,

        pergunta
    ):

        resposta = perguntar_vexa(
            pergunta
        )


        self.root.after(

            0,

            lambda:
            self.finalizar(
                resposta
            )
        )


    # ========================================================
    # FINALIZAR
    # ========================================================

    def finalizar(

        self,

        resposta
    ):

        self.add_message(

            "Vexa",

            resposta
        )


        self.send_button.config(

            state="normal",

            text="ENVIAR"
        )


        self.entry.focus()


# ============================================================
# INICIAR
# ============================================================

def main():

    root = tk.Tk()

    VexaApp(
        root
    )

    root.mainloop()


if __name__ == "__main__":

    main()

