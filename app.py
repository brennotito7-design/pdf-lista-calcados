import os
import re
import io
import base64
from flask import Flask, request, jsonify
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from collections import Counter

app = Flask(__name__)

FORNECEDORES = [
    {"nome": "Adair", "whatsapp": "(37) 99160-7940", "tipo": "Fabricante", "marca": ""},
    {"nome": "Adeir", "whatsapp": "(37) 99109-0589", "tipo": "Fabricante", "marca": ""},
    {"nome": "Ademir", "whatsapp": "(37) 99126-2768", "tipo": "Fabricante", "marca": ""},
    {"nome": "Adriano Vários", "whatsapp": "(37) 99137-7015", "tipo": "Fabricante", "marca": ""},
    {"nome": "Adriene Carneiro", "whatsapp": "(37) 99135-0543", "tipo": "Fabricante", "marca": ""},
    {"nome": "Airone Jéssica", "whatsapp": "(37) 99973-4920", "tipo": "Fabricante", "marca": ""},
    {"nome": "Alencar", "whatsapp": "(37) 99123-1204", "tipo": "Fabricante", "marca": ""},
    {"nome": "Alessandra Vários Modelos", "whatsapp": "(37) 99103-7295", "tipo": "Fabricante", "marca": ""},
    {"nome": "Alex", "whatsapp": "(37) 99127-1752", "tipo": "Fabricante", "marca": ""},
    {"nome": "Alexandre Box 200", "whatsapp": "(37) 99164-3434", "tipo": "Fabricante", "marca": ""},
    {"nome": "Aline Dinaiara", "whatsapp": "(37) 98804-2512", "tipo": "Fabricante", "marca": "Manu Ferreira"},
    {"nome": "Aline Vários Modelos", "whatsapp": "(37) 99165-7407", "tipo": "Fabricante", "marca": ""},
    {"nome": "Ana Euro Tênis", "whatsapp": "(37) 99199-6150", "tipo": "Fabricante", "marca": "Euro Tênis"},
    {"nome": "Ana Luiza Dias", "whatsapp": "(37) 99143-9367", "tipo": "Fabricante", "marca": ""},
    {"nome": "Ana Paula Abreu", "whatsapp": "(37) 99112-3363", "tipo": "Fabricante", "marca": "Air Force / Vans / Cartago"},
    {"nome": "Ana Paula", "whatsapp": "(37) 99133-8665", "tipo": "Fabricante", "marca": ""},
    {"nome": "Ana Paula Chinelos", "whatsapp": "(37) 99128-3891", "tipo": "Fabricante", "marca": ""},
    {"nome": "Anderson", "whatsapp": "(37) 99971-9733", "tipo": "Fabricante", "marca": ""},
    {"nome": "Anderson New Balance", "whatsapp": "(37) 99142-9129", "tipo": "Fabricante", "marca": "New Balance"},
    {"nome": "Antonelly Sandálias", "whatsapp": "(37) 99184-0014", "tipo": "Fabricante", "marca": ""},
    {"nome": "Ariane Katrina", "whatsapp": "(37) 99905-0045", "tipo": "Fabricante", "marca": "Katrina"},
    {"nome": "Arley Adidas", "whatsapp": "(37) 99778-5959", "tipo": "Fabricante", "marca": "Adidas"},
    {"nome": "Armando", "whatsapp": "(37) 99970-5618", "tipo": "Fabricante", "marca": ""},
    {"nome": "Babaloo", "whatsapp": "(33) 99135-3077", "tipo": "Fabricante", "marca": "Babaloo"},
    {"nome": "Bárbara Guimarães", "whatsapp": "(37) 99146-9010", "tipo": "Fabricante", "marca": "Vapor Max"},
    {"nome": "Beatriz Tênis Infantil", "whatsapp": "(37) 99104-1958", "tipo": "Fabricante", "marca": ""},
    {"nome": "Binho", "whatsapp": "(37) 99921-3902", "tipo": "Fabricante", "marca": ""},
    {"nome": "Branco", "whatsapp": "(37) 99170-5060", "tipo": "Fabricante", "marca": ""},
    {"nome": "Breno", "whatsapp": "(37) 99102-1586", "tipo": "Fabricante", "marca": ""},
    {"nome": "Bruno César", "whatsapp": "(37) 99142-4268", "tipo": "Fabricante", "marca": ""},
    {"nome": "Bruno Lamoia", "whatsapp": "(37) 99136-7534", "tipo": "Fabricante", "marca": ""},
    {"nome": "Ana Vendedora Redshoes", "whatsapp": "(11) 99000-0001", "tipo": "Representante", "marca": "Redshoes"},
    {"nome": "Ivan Scaleno", "whatsapp": "(11) 99000-0002", "tipo": "Fabricante", "marca": ""},
    {"nome": "Júlia", "whatsapp": "(11) 99000-0003", "tipo": "Fornecedor", "marca": "Samba"},
    {"nome": "Laiane Rocha", "whatsapp": "(11) 99000-0004", "tipo": "Distribuidor", "marca": ""},
    {"nome": "Leandro Fartura", "whatsapp": "(11) 99000-0005", "tipo": "Fornecedor", "marca": "Fartura"},
    {"nome": "Léo Asics Nimbus", "whatsapp": "(11) 99000-0006", "tipo": "Fabricante", "marca": "Asics Nimbus"},
    {"nome": "Lucas Kenner", "whatsapp": "(11) 99000-0007", "tipo": "Fabricante", "marca": "Kenner"},
    {"nome": "Márlon Buiu", "whatsapp": "(11) 99000-0008", "tipo": "Fabricante", "marca": ""},
    {"nome": "Natallya Brutus", "whatsapp": "(11) 99000-0009", "tipo": "Fornecedor", "marca": "Brutus"},
    {"nome": "Nathalia Samba OG", "whatsapp": "(11) 99000-0010", "tipo": "Fornecedor", "marca": "Samba OG"},
]

ROXO       = colors.HexColor("#4A3F8F")
CINZA      = colors.HexColor("#F5F5F5")
CINZA_TXT  = colors.HexColor("#555555")
BRANCO     = colors.white
VERDE      = colors.HexColor("#1D9E75")
PAGE_W, PAGE_H = A4

def gerar_pdf_bytes(nome_comprador, cpf_comprador, email_comprador):
    buffer = io.BytesIO()

    def rodape(canvas_obj, doc):
        canvas_obj.saveState()
        canvas_obj.saveState()
        canvas_obj.translate(PAGE_W / 2, PAGE_H / 2)
        canvas_obj.rotate(35)
        canvas_obj.setFont("Helvetica", 28)
        canvas_obj.setFillColorRGB(0.88, 0.88, 0.88)
        canvas_obj.drawCentredString(0, 0, f"{nome_comprador}  •  {cpf_comprador}")
        canvas_obj.restoreState()
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.setFillColor(colors.HexColor("#AAAAAA"))
        canvas_obj.drawCentredString(PAGE_W / 2, 11 * mm,
            "Documento licenciado. Uso pessoal e intransferível. Proibida redistribuição.")
        canvas_obj.setFillColor(CINZA_TXT)
        canvas_obj.drawRightString(PAGE_W - 18 * mm, 11 * mm, f"Pág. {doc.page}")
        canvas_obj.restoreState()

    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=18*mm, leftMargin=18*mm,
                            topMargin=20*mm, bottomMargin=22*mm)

    es = {
        "titulo":     ParagraphStyle("t1", fontName="Helvetica-Bold", fontSize=20,
                                      textColor=ROXO, alignment=TA_CENTER, spaceAfter=2),
        "sub":        ParagraphStyle("t2", fontName="Helvetica", fontSize=9.5,
                                      textColor=CINZA_TXT, alignment=TA_CENTER, spaceAfter=3),
        "badge":      ParagraphStyle("t3", fontName="Helvetica-Bold", fontSize=8,
                                      textColor=VERDE, alignment=TA_CENTER),
        "aviso":      ParagraphStyle("t5", fontName="Helvetica", fontSize=7.5,
                                      textColor=CINZA_TXT, alignment=TA_CENTER),
        "secao":      ParagraphStyle("t4", fontName="Helvetica-Bold", fontSize=11,
                                      textColor=ROXO, spaceBefore=8, spaceAfter=5),
        "dica":       ParagraphStyle("t6", fontName="Helvetica", fontSize=8,
                                      textColor=CINZA_TXT, spaceAfter=3),
        "dica_title": ParagraphStyle("t7", fontName="Helvetica-Bold", fontSize=8.5,
                                      textColor=ROXO, spaceAfter=4),
    }

    story = []
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("Lista de Fornecedores de Calçados", es["titulo"]))
    story.append(Paragraph("Fabricantes e distribuidores diretos | Contato via WhatsApp | Edição 2025", es["sub"]))

    tipos = Counter(f["tipo"] for f in FORNECEDORES)
    resumo = "  •  ".join([f"{v} {k}s" for k, v in tipos.most_common()])
    story.append(Paragraph(f"● {len(FORNECEDORES)} contatos  •  {resumo}", es["badge"]))
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ROXO, spaceAfter=3))
    story.append(Paragraph(
        f"Documento licenciado para: <b>{nome_comprador}</b> — {cpf_comprador}. "
        "Uso pessoal e intransferível.", es["aviso"]))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("Diretório completo de fornecedores", es["secao"]))

    cabecalho = ["#", "Nome / Contato", "WhatsApp", "Tipo", "Marca / Produto"]
    dados = [cabecalho]
    for i, f in enumerate(FORNECEDORES, 1):
        dados.append([str(i), f["nome"], f["whatsapp"], f["tipo"],
                      f["marca"] if f["marca"] else "—"])

    col_w = [10*mm, 70*mm, 38*mm, 28*mm, 28*mm]
    tab = Table(dados, colWidths=col_w, repeatRows=1)
    tab.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), ROXO),
        ("TEXTCOLOR",     (0,0), (-1,0), BRANCO),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0), 8.5),
        ("ALIGN",         (0,0), (-1,0), "CENTER"),
        ("TOPPADDING",    (0,0), (-1,0), 7),
        ("BOTTOMPADDING", (0,0), (-1,0), 7),
        ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1), (-1,-1), 8),
        ("TEXTCOLOR",     (0,1), (-1,-1), colors.HexColor("#222222")),
        ("TOPPADDING",    (0,1), (-1,-1), 5),
        ("BOTTOMPADDING", (0,1), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
        ("RIGHTPADDING",  (0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [BRANCO, CINZA]),
        ("ALIGN",         (0,1), (0,-1), "CENTER"),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#DDDDDD")),
        ("LINEBELOW",     (0,0), (-1,0), 1.5, ROXO),
    ]))
    story.append(tab)
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#CCCCCC"), spaceAfter=4))
    story.append(Paragraph("Como usar esta lista:", es["dica_title"]))
    story.append(Paragraph("1. Entre em contato via WhatsApp apresentando-se como lojista ou revendedor.", es["dica"]))
    story.append(Paragraph("2. Pergunte sobre catálogo, pedido mínimo e condições de pagamento.", es["dica"]))
    story.append(Paragraph("3. Solicite amostras antes de fazer o primeiro pedido maior.", es["dica"]))
    story.append(Paragraph("4. Guarde este PDF com segurança — contém seus dados de licença.", es["dica"]))

    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    buffer.seek(0)
    return buffer.read()


@app.route("/gerar-pdf", methods=["POST"])
def gerar_pdf():
    dados = request.get_json()

    nome  = dados.get("nome", "Comprador")
    cpf   = dados.get("cpf", "Não informado")
    email = dados.get("email", "")

    if not email:
        email = "comprador@teste.com"

    pdf_bytes = gerar_pdf_bytes(nome, cpf, email)
    pdf_b64   = base64.b64encode(pdf_bytes).decode("utf-8")

    return jsonify({
        "sucesso": True,
        "nome_arquivo": f"Lista_Fornecedores_{nome.replace(' ','_')}.pdf",
        "pdf_base64": pdf_b64
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
