from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/executar")
def executar(
    request: Request,
    filial: int = Form(...),
    cpf: str = Form(""),
    inscricao: str = Form(""),
    produto: str = Form(""),
    acao: str = Form(...)
):
    ip = f"10.0.{filial}.100"

    try:
        conn = psycopg2.connect(
            host=ip,
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        cur = conn.cursor()

        if acao == "inscricao":
            sql = f"UPDATE pessoa SET inscr_est = %s WHERE cpf = %s"
            cur.execute(sql, (inscricao, cpf))
        
        elif acao == "intervencao":
            sql = "UPDATE bico_encerrante SET flag = null WHERE flag = 'DE'"
            cur.execute(sql)

        elif acao == "desbloqueio":
            sql1 = f"""
                UPDATE produto_empresa pe
                SET permite_venda_dist = 't', permite_venda = 't'
                FROM produto p
                WHERE pe.produto = p.grid AND p.codigo = '{produto}'
            """
            sql2 = f"""
                UPDATE produto p
                SET permite_venda_dist = 't', permite_venda = 't'
                FROM produto_empresa pe
                WHERE pe.produto = p.grid AND p.codigo = '{produto}'
            """
            cur.execute(sql1)
            cur.execute(sql2)

        elif acao == "derrubar":
            cur.execute("SELECT pid FROM usuario_pid WHERE modulo = 'concentrador'")
            pids = cur.fetchall()
            for pid in pids:
                cur.execute(f"SELECT pg_terminate_backend({pid[0]})")

        conn.commit()
        cur.close()
        conn.close()
        return templates.TemplateResponse("index.html", {"request": request, "msg": "Comando executado com sucesso!"})

    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "msg": f"Erro: {str(e)}"})
